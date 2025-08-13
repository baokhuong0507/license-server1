from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session

from ..deps import get_db
from ..services.activations import ensure_device, bind_or_switch, current_online_activation
from ..services.keys import get_key_by_value, set_key_status
from ..models import KeyStatus, Activation, ActivationStatus
from ..auth import decode_token, create_token
from ..config import settings

router = APIRouter(prefix="/api", tags=["client"])


def _now_utc() -> datetime:
    """Trả thời gian UTC dạng naive (đồng bộ với DB)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _get_bearer_token(header_val: str | None) -> str:
    if not header_val or not header_val.startswith("Bearer "):
        raise HTTPException(401, "NO_TOKEN")
    return header_val.split(" ", 1)[1].strip()


@router.post("/activate")
def activate(payload: dict, db: Session = Depends(get_db)):
    """
    Body (JSON):
    {
      "key": "AAAA-BBBB-CCCC",
      "device_fingerprint": "fingerprint-1",
      "device_name": "PC Khuong",              (optional)
      "client_version": "1.0.0",               (optional)
      "build": "2024.08.09"                    (optional)
    }
    """
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

    # đảm bảo device tồn tại/cập nhật tên nếu có
    dev = ensure_device(db, fp, name)

    try:
        # bind hoặc switch thiết bị cho key theo logic của bạn
        act = bind_or_switch(db, key, dev, ver, build)

        resp = {"session_token": act.session_token}
        # nếu có TTL offline → phát offline token (cho phép chạy offline X phút)
        if key.offline_ttl_minutes and key.offline_ttl_minutes > 0:
            resp["offline_token"] = create_token(f"offline:{act.id}", key.offline_ttl_minutes)
        return resp

    except ValueError as e:
        if str(e) == "CONCURRENT_USE_DETECTED":
            # dùng song song tại thời điểm activate
            raise HTTPException(423, "CONCURRENT_USE_DETECTED")
        raise


@router.post("/heartbeat")
def heartbeat(
    Authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Header:
      Authorization: Bearer <session_token>

    Trả:
      {"ok": true, "allow_offline_until": "2025-08-09T12:34:56Z" | null}
    """
    token = _get_bearer_token(Authorization)

    try:
        data = decode_token(token)
    except Exception:
        raise HTTPException(401, "TOKEN_INVALID")

    act_id = data.get("sub")
    if not act_id:
        raise HTTPException(401, "TOKEN_INVALID")

    act = db.get(Activation, act_id)
    if not act:
        raise HTTPException(401, "SESSION_NOT_FOUND")

    key = act.license_key
    # nếu key không khả dụng → 423
    if key.status in (KeyStatus.DISABLED, KeyStatus.DELETED, KeyStatus.TEMP_LOCKED):
        raise HTTPException(423, "KEY_NOT_AVAILABLE")

    # phát hiện dùng song song:
    # current_online_activation phải trả về phiên BOUND, last_seen_at mới trong timeout,
    # nếu phiên đó thuộc device khác với act hiện tại → temp lock.
    online = current_online_activation(db, key.id)
    if online and online.id != act.id and online.device_id != act.device_id:
        set_key_status(db, key, KeyStatus.TEMP_LOCKED)
        db.commit()
        raise HTTPException(423, "CONCURRENT_USE_DETECTED")

    # cập nhật "đang online"
    act.last_seen_at = _now_utc()
    if act.status != ActivationStatus.BOUND:
        act.status = ActivationStatus.BOUND

    db.commit()

    allow_until = None
    if key.offline_ttl_minutes and key.offline_ttl_minutes > 0:
        # cho phép offline đến thời điểm này (ISO + Z cho dễ đọc)
        allow_until = (_now_utc() + timedelta(minutes=key.offline_ttl_minutes)).isoformat() + "Z"

    return {"ok": True, "allow_offline_until": allow_until}
