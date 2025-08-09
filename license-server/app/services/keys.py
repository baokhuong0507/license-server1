from datetime import datetime
from sqlalchemy.orm import Session
from ..models import LicenseKey, KeyStatus

def get_key_by_value(db: Session, key_value: str) -> LicenseKey | None:
    return db.query(LicenseKey).filter_by(key=key_value).first()

def set_key_status(db: Session, key: LicenseKey, status: KeyStatus):
    key.status = status
    if status == KeyStatus.TEMP_LOCKED:
        key.last_violation_at = datetime.utcnow()
    db.commit()
