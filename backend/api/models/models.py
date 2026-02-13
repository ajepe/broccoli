from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, Enum
from sqlalchemy.sql import func
from backend.core.database import Base
import enum


class ClientStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class PlanType(str, enum.Enum):
    BASIC = "basic"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    domain = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    db_name = Column(String(255), nullable=False)
    db_user = Column(String(255), nullable=False)
    db_password = Column(String(255), nullable=False)
    
    odoo_port = Column(Integer, nullable=False)
    
    status = Column(String(50), default=ClientStatus.PENDING.value)
    plan = Column(String(50), default=PlanType.BASIC.value)
    
    memory_limit = Column(String(50), default="2g")
    db_memory_limit = Column(String(50), default="1g")
    cpu_limit = Column(Float, default=1.0)
    db_cpu_limit = Column(Float, default=0.5)
    redis_enabled = Column(Boolean, default=False)
    
    disk_usage_mb = Column(Integer, default=0)
    last_backup = Column(DateTime, nullable=True)
    next_backup = Column(DateTime, nullable=True)
    
    backup_retention_daily = Column(Integer, default=7)
    backup_retention_weekly = Column(Integer, default=4)
    backup_retention_monthly = Column(Integer, default=3)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    activated_at = Column(DateTime, nullable=True)
    suspended_at = Column(DateTime, nullable=True)
    
    notes = Column(Text, nullable=True)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class Backup(Base):
    __tablename__ = "backups"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    client_name = Column(String(255), nullable=False, index=True)
    backup_type = Column(String(50), nullable=False)
    filename = Column(String(255), nullable=False)
    size_mb = Column(Float, default=0)
    s3_key = Column(String(500), nullable=True)
    status = Column(String(50), default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
