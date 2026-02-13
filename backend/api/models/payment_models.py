from sqlalchemy import Column, Integer, String, DateTime, Float, Enum
from sqlalchemy.sql import func
from backend.core.database import Base
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    client_id = Column(Integer, nullable=True, index=True)
    
    amount = Column(Integer, nullable=False)
    currency = Column(String(10), default="NGN")
    
    payment_status = Column(String(20), default=PaymentStatus.PENDING.value)
    
    paystack_reference = Column(String(100), unique=True, index=True)
    paystack_customer_id = Column(String(100))
    
    plan = Column(String(50))
    billing_cycle = Column(String(20), default="monthly")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    
    plan = Column(String(50), nullable=False)
    status = Column(String(20), default="active")
    
    start_date = Column(DateTime, server_default=func.now())
    end_date = Column(DateTime, nullable=True)
    next_billing_date = Column(DateTime, nullable=True)
    
    auto_renew = Column(Integer, default=1)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
