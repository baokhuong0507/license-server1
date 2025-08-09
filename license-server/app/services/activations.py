from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import Activation, ActivationStatus, Device, LicenseKey, KeyStatus
from ..auth import create_token
from ..config import settings

HB_TIMEOUT = timedelta(seconds=settings.HEARTBEAT_TIMEOUT_SEC)

def ensure_device(db: Session, fingerprint: str, name: str | None = None) -> Device:
    dev = db.query(Device).filter_by(fingerprint=fingerprint).first()
    if dev: 
        return dev
    dev = Device(fingerprint=fingerprint, name=name)
    db.add(dev); db.commit(); db.refresh(dev)
    return dev

def current_online_activation(db: Session, key_id: str) -> Activation | None:
    a = (
        db.query(Activation)
        .filter_by(license_key_id=key_id, status=ActivationStatus.BOUND)
        .order_by(Activation.bound_at.desc())
        .first()
    )
    if not a: 
        return None
    if not a.last_seen_at:
        return None
    if datetime.utcnow() - a.last_seen_at <= HB_TIMEOUT:
        return a
    return None

def bind_or_switch(db: Session, key: LicenseKey, dev: Device, client_version: str | None = None, build: str | None = None) -> Activation:
    if key.status != KeyStatus.ACTIVE:
        raise ValueError("KEY_NOT_ACTIVE")

    online = current_online_activation(db, key.id)
    if online and online.device_id != dev.id:
        # concurrent usage -> temp lock
        key.status = KeyStatus.TEMP_LOCKED
        key.last_violation_at = datetime.utcnow()
        db.commit()
        raise ValueError("CONCURRENT_USE_DETECTED")

    # If same device -> continue; else unbind previous and create new
    if not (online and online.device_id == dev.id):
        # Unbind any existing
        db.query(Activation).filter_by(license_key_id=key.id, status=ActivationStatus.BOUND).update({
            Activation.status: ActivationStatus.UNBOUND,
            Activation.unbound_at: datetime.utcnow(),
        })
        a = Activation(license_key_id=key.id, device_id=dev.id, status=ActivationStatus.BOUND)
        db.add(a); db.commit(); db.refresh(a)
        online = a

    token = create_token(online.id, settings.SESSION_TTL_MINUTES)
    online.session_token = token
    online.last_seen_at = datetime.utcnow()
    online.client_version = client_version
    online.client_build = build
    db.commit()
    return online
