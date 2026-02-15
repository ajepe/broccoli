from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from datetime import datetime
from backend.core.config import get_settings
from backend.core.database import engine, Base
from backend.api.routes import clients, payments
import logging

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router, prefix="/api", tags=["Clients"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])


@app.post("/api/payments/webhook")
async def paystack_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("x-paystack-signature", "")
    
    from backend.api.services.paystack_service import get_paystack_service
    paystack = get_paystack_service()
    
    try:
        if paystack.verify_webhook(payload, signature):
            import json
            data = json.loads(payload)
            
            event = data.get("event")
            logger.info(f"Paystack webhook received: {event}")
            
            if event == "charge.success":
                reference = data["data"]["reference"]
                
                from backend.core.database import SessionLocal
                from backend.api.models.payment_models import Payment
                from backend.api.models.models import Client, ClientStatus
                from backend.api.services.provisioning import (
                    start_client_stack, create_nginx_config, reload_nginx, request_ssl_certificate
                )
                
                db = SessionLocal()
                try:
                    payment = db.query(Payment).filter(
                        Payment.paystack_reference == reference
                    ).first()
                    
                    if payment and payment.payment_status != "success":
                        payment.payment_status = "success"
                        payment.completed_at = datetime.utcnow()
                        
                        if payment.client_id:
                            client = db.query(Client).filter(Client.id == payment.client_id).first()
                            if client and client.status == ClientStatus.PENDING.value:
                                try:
                                    if start_client_stack(client.name):
                                        client.status = ClientStatus.ACTIVE.value
                                        client.activated_at = datetime.utcnow()
                                        
                                        create_nginx_config(client)
                                        reload_nginx()
                                        
                                        try:
                                            request_ssl_certificate(client.domain, settings.SMTP_FROM)
                                            reload_nginx()
                                        except Exception as e:
                                            logger.warning(f"SSL certificate not ready: {e}")
                                        
                                        logger.info(f"Client {client.name} activated after payment")
                                except Exception as e:
                                    logger.error(f"Failed to activate client: {e}")
                        
                        db.commit()
                        logger.info(f"Payment {reference} marked as successful")
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error processing payment: {e}")
                    return {"status": "error", "message": str(e)}
                finally:
                    db.close()
            
            elif event == "subscription.create":
                logger.info(f"Subscription created: {data.get('data', {}).get('subscription_code')}")
            
            elif event == "subscription.disable":
                logger.info(f"Subscription disabled")
            
            return {"status": "success"}
        
        logger.warning("Invalid webhook signature")
        return {"status": "error", "message": "Invalid signature"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/")
def root():
    return {"message": "Odoo Cloud Platform API", "version": settings.APP_VERSION}
