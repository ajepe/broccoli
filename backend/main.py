from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from backend.core.config import get_settings
from backend.core.database import engine, Base
from backend.api.routes import clients, payments

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    
    if paystack.verify_webhook(payload, signature):
        import json
        data = json.loads(payload)
        
        event = data.get("event")
        if event == "charge.success":
            reference = data["data"]["reference"]
            
            from backend.core.database import SessionLocal
            from backend.api.models.payment_models import Payment
            
            db = SessionLocal()
            payment = db.query(Payment).filter(
                Payment.paystack_reference == reference
            ).first()
            
            if payment and payment.payment_status != "success":
                payment.payment_status = "success"
                payment.completed_at = datetime.utcnow()
                db.commit()
            
            db.close()
        
        return {"status": "success"}
    
    return {"status": "error", "message": "Invalid signature"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.get("/")
def root():
    return {"message": "Odoo Cloud Platform API", "version": settings.APP_VERSION}
