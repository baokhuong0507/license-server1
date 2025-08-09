from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from ..deps import get_db
from ..services.activations import ensure_device, bind_or_switch, current_online_activation
from ..services.keys import get_key_by_value, set_key_status
from ..models import KeyStatus, Activation
from ..auth import decode_token
from ..config import settings
from datetime import datetime, timedelta

router = APIRouter(prefix="/api", tags=["client"])

@router.post("/activate")
def activate(payload: dict, db: Session = Depends(get_db)):
    key_value = payload.get("key")
    fp = payload.get("device_fingerprint")
    name = payload.get("device_name")
    ver = payload.get("client_version")
    build = payload.get("build")

    if not key_value or not fp:
        raise HTTPException(400, "MISSING_KEY_OR_FINGERPRINT")

    key = get_key_by_value(db, key_value)
    if not key:
        raise HTTPException(404, "KEY_NOT_FOUND")
    if key.status == KeyStatus.DELETED:
        raise HTTPException(400, "KEY_DELETED")
    if key.status == KeyStatus.DISABLED:
        raise HTTPException(400, "KEY_DISABLED")
    if key.status == KeyStatus.TEMP_LOCKED:
        raise HTTPException(423, "KEY_LOCKED")

    dev = ensure_device(db, fp, name)
    try:
        act = bind_or_switch(db, key, dev, ver, build)
        resp = {"session_token": act.session_token}
        if key.offline_ttl_minutes and key.offline_ttl_minutes > 0:
            from ..auth import create_token
            resp["offline_token"] = create_token(f"offline:{act.id}", key.offline_ttl_minutes)
        return resp
    except ValueError as e:
        if str(e) == "CONCURRENT_USE_DETECTED":
            raise HTTPException(423, "CONCURRENT_USE_DETECTED")
        raise

@router.post("/heartbeat")
def heartbeat(Authorization: str = Header(None), db: Session = Depends(get_db)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(401, "NO_TOKEN")
    token = Authorization.split(" ",1)[1]
    try:
        data = decode_token(token)
    except Exception:
        raise HTTPException(401, "TOKEN_INVALID")

    act_id = data.get("sub")
    act = db.get(Activation, act_id)
    if not act:
        raise HTTPException(401, "SESSION_NOT_FOUND")

    key = act.license_key
    if key.status in (KeyStatus.DISABLED, KeyStatus.DELETED, KeyStatus.TEMP_LOCKED):
        raise HTTPException(423, "KEY_NOT_AVAILABLE")

    # Detect concurrent usage
    online = current_online_activation(db, key.id)
    if online and online.device_id != act.device_id:
        set_key_status(db, key, KeyStatus.TEMP_LOCKED)
        raise HTTPException(423, "CONCURRENT_USE_DETECTED")

    act.last_seen_at = datetime.utcnow()
    db.commit()
    allow_until = None
    if key.offline_ttl_minutes and key.offline_ttl_minutes > 0:
        allow_until = (datetime.utcnow() + timedelta(minutes=key.offline_ttl_minutes)).isoformat()
    return {"ok": True, "allow_offline_until": allow_until}
