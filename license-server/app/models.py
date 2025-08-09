import uuid, enum
from datetime import datetime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer

Base = declarative_base()

def now():
    return datetime.utcnow()

class KeyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    TEMP_LOCKED = "TEMP_LOCKED"
    DELETED = "DELETED"

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="admin")
    created_at = Column(DateTime, default=now)

class LicenseKey(Base):
    __tablename__ = "license_keys"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(KeyStatus), default=KeyStatus.ACTIVE, index=True)
    note = Column(String)
    last_violation_at = Column(DateTime)
    offline_ttl_minutes = Column(Integer, default=0)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

class Device(Base):
    __tablename__ = "devices"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fingerprint = Column(String, index=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=now)

class ActivationStatus(str, enum.Enum):
    BOUND = "BOUND"
    UNBOUND = "UNBOUND"

class Activation(Base):
    __tablename__ = "activations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    license_key_id = Column(String, ForeignKey("license_keys.id"), nullable=False)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    status = Column(Enum(ActivationStatus), default=ActivationStatus.BOUND, index=True)
    bound_at = Column(DateTime, default=now)
    unbound_at = Column(DateTime)
    last_seen_at = Column(DateTime)
    client_version = Column(String)
    client_build = Column(String)
    session_token = Column(String)

    license_key = relationship("LicenseKey")
    device = relationship("Device")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_type = Column(String)  # ADMIN | SYSTEM | CLIENT
    actor_id = Column(String)
    action = Column(String)
    details = Column(String)
    created_at = Column(DateTime, default=now)
