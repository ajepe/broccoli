import requests
import hashlib
import hmac
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from backend.core.config import get_settings

settings = get_settings()


class PaystackService:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.base_url = "https://api.paystack.co"
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
    
    def create_customer(self, email: str, first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """Create a Paystack customer"""
        data = {
            "email": email
        }
        if first_name:
            data["first_name"] = first_name
        if last_name:
            data["last_name"] = last_name
        
        response = requests.post(
            f"{self.base_url}/customer",
            json=data,
            headers=self._get_headers()
        )
        return response.json()
    
    def initialize_transaction(
        self,
        email: str,
        amount: int,
        currency: str = "NGN",
        reference: str = None,
        callback_url: str = None,
        metadata: dict = None
    ) -> Dict[str, Any]:
        """Initialize a Paystack transaction"""
        data = {
            "email": email,
            "amount": amount * 100,
            "currency": currency,
        }
        
        if reference:
            data["reference"] = reference
        
        if callback_url:
            data["callback_url"] = callback_url
        
        if metadata:
            data["metadata"] = metadata
        
        response = requests.post(
            f"{self.base_url}/transaction/initialize",
            json=data,
            headers=self._get_headers()
        )
        return response.json()
    
    def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """Verify a Paystack transaction"""
        response = requests.get(
            f"{self.base_url}/transaction/verify/{reference}",
            headers=self._get_headers()
        )
        return response.json()
    
    def create_subscription(
        self,
        customer: str,
        plan: str,
        start_date: datetime = None
    ) -> Dict[str, Any]:
        """Create a Paystack subscription"""
        data = {
            "customer": customer,
            "plan": plan
        }
        
        if start_date:
            data["start_date"] = start_date.isoformat()
        
        response = requests.post(
            f"{self.base_url}/subscription",
            json=data,
            headers=self._get_headers()
        )
        return response.json()
    
    def get_plans(self) -> Dict[str, Any]:
        """Get all subscription plans"""
        response = requests.get(
            f"{self.base_url}/plan",
            headers=self._get_headers()
        )
        return response.json()
    
    def create_plan(
        self,
        name: str,
        amount: int,
        interval: str = "monthly",
        description: str = None
    ) -> Dict[str, Any]:
        """Create a subscription plan"""
        data = {
            "name": name,
            "amount": amount * 100,
            "interval": interval,
        }
        
        if description:
            data["description"] = description
        
        response = requests.post(
            f"{self.base_url}/plan",
            json=data,
            headers=self._get_headers()
        )
        return response.json()
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify Paystack webhook signature"""
        expected_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def get_transaction_logs(self, reference: str) -> Dict[str, Any]:
        """Get transaction logs"""
        response = requests.get(
            f"{self.base_url}/transaction/{reference}",
            headers=self._get_headers()
        )
        return response.json()
    
    def refund_transaction(self, transaction: str, amount: int = None) -> Dict[str, Any]:
        """Refund a transaction"""
        data = {}
        if amount:
            data["amount"] = amount * 100
        
        response = requests.post(
            f"{self.base_url}/refund",
            json=data,
            headers=self._get_headers()
        )
        return response.json()


def get_paystack_service() -> PaystackService:
    return PaystackService()


PLAN_PRICES = {
    "basic": 15000,
    "business": 45000,
    "enterprise": 120000
}


def get_plan_price(plan: str, billing_cycle: str = "monthly") -> int:
    """Get price in Naira"""
    price = PLAN_PRICES.get(plan, 15000)
    
    if billing_cycle == "annual":
        price = int(price * 12 * 0.8)
    
    return price


def get_plan_code(plan: str) -> str:
    """Get Paystack plan code"""
    codes = {
        "basic": "PLN_basic_monthly",
        "business": "PLN_business_monthly", 
        "enterprise": "PLN_enterprise_monthly"
    }
    return codes.get(plan, "PLN_basic_monthly")
