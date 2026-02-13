from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

from backend.core.database import get_db
from backend.api.models.models import User, Client
from backend.api.models.payment_models import Payment, Subscription
from backend.api.services.paystack_service import (
    get_paystack_service, get_plan_price, PLAN_PRICES
)
from backend.api.routes.clients import get_current_user

router = APIRouter()


class PaymentInitializeRequest(BaseModel):
    plan: str
    billing_cycle: str = "monthly"


class PaymentInitializeResponse(BaseModel):
    authorization_url: str
    reference: str


class PaymentResponse(BaseModel):
    id: int
    amount: int
    currency: str
    payment_status: str
    plan: str
    billing_cycle: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/initialize", response_model=PaymentInitializeResponse)
def initialize_payment(
    request: PaymentInitializeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if request.plan not in PLAN_PRICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan selected"
        )
    
    amount = get_plan_price(request.plan, request.billing_cycle)
    reference = f"ODOO-{uuid.uuid4().hex[:12].upper()}"
    
    paystack = get_paystack_service()
    
    callback_url = f"{'http://localhost:5173'}/payment/callback?reference={reference}"
    
    metadata = {
        "user_id": current_user.id,
        "plan": request.plan,
        "billing_cycle": request.billing_cycle,
        "custom_fields": [
            {
                "display_name": "Plan",
                "variable_name": "plan",
                "value": request.plan
            },
            {
                "display_name": "Billing",
                "variable_name": "billing_cycle", 
                "value": request.billing_cycle
            }
        ]
    }
    
    try:
        result = paystack.initialize_transaction(
            email=current_user.email,
            amount=amount,
            reference=reference,
            callback_url=callback_url,
            metadata=metadata
        )
        
        if not result.get("status"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize payment"
            )
        
        payment = Payment(
            user_id=current_user.id,
            amount=amount,
            plan=request.plan,
            billing_cycle=request.billing_cycle,
            paystack_reference=reference,
            payment_status="pending"
        )
        db.add(payment)
        db.commit()
        
        return PaymentInitializeResponse(
            authorization_url=result["data"]["authorization_url"],
            reference=reference
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/verify/{reference}")
def verify_payment(
    reference: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = db.query(Payment).filter(
        Payment.paystack_reference == reference,
        Payment.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.payment_status == "success":
        return {"status": "success", "message": "Payment already verified"}
    
    paystack = get_paystack_service()
    result = paystack.verify_transaction(reference)
    
    if result.get("status") and result["data"]["status"] == "success":
        payment.payment_status = "success"
        payment.completed_at = datetime.utcnow()
        
        existing_sub = db.query(Subscription).filter(
            Subscription.user_id == current_user.id
        ).first()
        
        if existing_sub:
            existing_sub.plan = payment.plan
            existing_sub.status = "active"
            existing_sub.next_billing_date = datetime.utcnow() + timedelta(days=30)
        else:
            subscription = Subscription(
                user_id=current_user.id,
                plan=payment.plan,
                status="active",
                next_billing_date=datetime.utcnow() + timedelta(days=30)
            )
            db.add(subscription)
        
        db.commit()
        
        return {"status": "success", "message": "Payment verified"}
    
    return {"status": "pending", "message": "Payment not completed"}


@router.get("/history", response_model=List[PaymentResponse])
def get_payment_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()
    
    return payments


@router.get("/subscription")
def get_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        return {
            "status": "no_subscription",
            "message": "No active subscription"
        }
    
    return {
        "status": subscription.status,
        "plan": subscription.plan,
        "start_date": subscription.start_date,
        "end_date": subscription.end_date,
        "next_billing_date": subscription.next_billing_date,
        "auto_renew": subscription.auto_renew
    }


@router.post("/webhook")
def paystack_webhook(
    db: Session = Depends(get_db)
):
    pass


@router.post("/cancel-subscription")
def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    subscription.status = "cancelled"
    subscription.auto_renew = 0
    db.commit()
    
    return {"status": "success", "message": "Subscription cancelled"}
