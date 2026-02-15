from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re


class ClientBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    domain: str = Field(..., pattern=r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?(\.[a-zA-Z]{2,})+$')
    email: EmailStr
    plan: str = Field(default="basic", pattern=r'^(basic|business|enterprise)$')


class ClientCreate(ClientBase):
    db_password: Optional[str] = None
    redis_enabled: bool = True


class ClientUpdate(BaseModel):
    email: Optional[EmailStr] = None
    plan: Optional[str] = None
    memory_limit: Optional[str] = None
    db_memory_limit: Optional[str] = None
    cpu_limit: Optional[float] = None
    db_cpu_limit: Optional[float] = None
    redis_enabled: Optional[bool] = None
    notes: Optional[str] = None


class ClientResponse(ClientBase):
    id: int
    db_name: str
    odoo_port: int
    status: str
    memory_limit: str
    db_memory_limit: str
    cpu_limit: float
    db_cpu_limit: float
    redis_enabled: bool
    disk_usage_mb: Optional[int] = 0
    last_backup: Optional[datetime] = None
    created_at: datetime
    activated_at: Optional[datetime] = None
    custom_domains: Optional[List[str]] = Field(default_factory=lambda: [])
    payment_deadline: Optional[datetime] = None
    payment_reference: Optional[str] = None
    payment_status: Optional[str] = "pending"
    deletion_scheduled_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('custom_domains', mode='before')
    @classmethod
    def parse_custom_domains(cls, v):
        if v is None or v == '':
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except:
                return []
        return []


class ClientDetailResponse(ClientResponse):
    db_user: str
    db_password: str
    backup_retention_daily: int
    backup_retention_weekly: int
    backup_retention_monthly: int
    suspended_at: Optional[datetime] = None
    updated_at: datetime


class ClientStats(BaseModel):
    total_clients: int
    active_clients: int
    suspended_clients: int
    total_disk_usage_mb: int
    avg_memory_usage_percent: float


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class BackupBase(BaseModel):
    client_id: int
    backup_type: str


class BackupResponse(BackupBase):
    id: int
    client_name: str
    filename: str
    size_mb: float
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BackupCreate(BaseModel):
    backup_type: str = "manual"


class ActivityLogResponse(BaseModel):
    id: int
    client_id: Optional[int] = None
    user_id: Optional[int] = None
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContainerStats(BaseModel):
    container_name: str
    status: str
    cpu_percent: float
    memory_usage_mb: float
    memory_limit_mb: float
    memory_percent: float
    network_rx_mb: float
    network_tx_mb: float
    uptime: str


class CustomDomainResponse(BaseModel):
    domain: str
    status: str
    ssl_enabled: bool
    added_at: datetime
