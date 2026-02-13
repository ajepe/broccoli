from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from backend.core.database import get_db
from backend.core.security import verify_password, create_access_token, decode_access_token, get_password_hash
from backend.api.models.models import Client, User, ClientStatus, ActivityLog
from backend.api.schemas.schemas import (
    ClientCreate, ClientUpdate, ClientResponse, ClientDetailResponse,
    ClientStats, UserCreate, UserResponse, Token
)
from backend.api.services.provisioning import (
    generate_secure_password, generate_db_name, generate_db_user, get_next_odoo_port,
    get_plan_resources, create_client_directories, create_docker_compose, create_env_file,
    create_nginx_config, start_client_stack, stop_client_stack, remove_client_stack,
    reload_nginx, request_ssl_certificate, get_container_stats, get_disk_usage
)
from backend.api.services.backup_service import trigger_backup
from backend.core.config import get_settings
import json

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
settings = get_settings()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


def log_activity(db: Session, user_id: int, client_id: int, action: str, details: str = None, ip: str = None):
    log = ActivityLog(
        user_id=user_id,
        client_id=client_id,
        action=action,
        details=details,
        ip_address=ip
    )
    db.add(log)
    db.commit()


@router.post("/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/clients", response_model=List[ClientResponse])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Client)
    
    if status:
        query = query.filter(Client.status == status)
    
    clients = query.offset(skip).limit(limit).all()
    
    for client in clients:
        client.disk_usage_mb = get_disk_usage(client.name)
    
    return clients


@router.get("/clients/stats", response_model=ClientStats)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = db.query(Client).count()
    active = db.query(Client).filter(Client.status == ClientStatus.ACTIVE.value).count()
    suspended = db.query(Client).filter(Client.status == ClientStatus.SUSPENDED.value).count()
    
    clients = db.query(Client).all()
    total_disk = sum(get_disk_usage(c.name) for c in clients)
    
    return ClientStats(
        total_clients=total,
        active_clients=active,
        suspended_clients=suspended,
        total_disk_usage_mb=total_disk,
        avg_memory_usage_percent=0.0
    )


@router.post("/clients", response_model=ClientDetailResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Client).filter(
        (Client.name == client_data.name) | (Client.domain == client_data.domain)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this name or domain already exists"
        )
    
    db_password = client_data.db_password or generate_secure_password()
    plan_resources = get_plan_resources(client_data.plan)
    
    client = Client(
        name=client_data.name,
        domain=client_data.domain,
        email=client_data.email,
        db_name=generate_db_name(client_data.name),
        db_user=generate_db_user(client_data.name),
        db_password=db_password,
        odoo_port=get_next_odoo_port(),
        plan=client_data.plan,
        memory_limit=plan_resources["memory_limit"],
        db_memory_limit=plan_resources["db_memory_limit"],
        cpu_limit=plan_resources["cpu_limit"],
        db_cpu_limit=plan_resources["cpu_limit"] * 0.5,
        redis_enabled=client_data.redis_enabled,
        status=ClientStatus.PENDING.value,
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    try:
        create_client_directories(client.name)
        create_docker_compose(client, db_password)
        create_env_file(client, db_password, settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY)
        
        if start_client_stack(client.name):
            client.status = ClientStatus.ACTIVE.value
            client.activated_at = datetime.utcnow()
            
            create_nginx_config(client)
            reload_nginx()
            
            if request_ssl_certificate(client.domain, settings.SMTP_FROM):
                reload_nginx()
        
        db.commit()
        db.refresh(client)
        
        log_activity(db, current_user.id, client.id, "create", f"Created client {client.name}")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to provision client: {str(e)}"
        )
    
    return client


@router.get("/clients/{client_name}", response_model=ClientDetailResponse)
def get_client(
    client_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    client.disk_usage_mb = get_disk_usage(client.name)
    
    return client


@router.patch("/clients/{client_name}", response_model=ClientResponse)
def update_client(
    client_name: str,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    update_data = client_data.model_dump(exclude_unset=True)
    
    if "plan" in update_data:
        plan = update_data["plan"]
        if plan:
            plan_resources = get_plan_resources(plan)
            client.memory_limit = plan_resources["memory_limit"]
            client.db_memory_limit = plan_resources["db_memory_limit"]
            client.cpu_limit = plan_resources["cpu_limit"]
    
    for key, value in update_data.items():
        setattr(client, key, value)
    
    db.commit()
    db.refresh(client)
    
    log_activity(db, current_user.id, client.id, "update", f"Updated client {client.name}")
    
    return client


@router.post("/clients/{client_name}/suspend")
def suspend_client(
    client_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    if client.status == ClientStatus.SUSPENDED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client is already suspended"
        )
    
    stop_client_stack(client.name)
    
    client.status = ClientStatus.SUSPENDED.value
    client.suspended_at = datetime.utcnow()
    db.commit()
    
    log_activity(db, current_user.id, client.id, "suspend", f"Suspended client {client.name}")
    
    return {"success": True, "message": f"Client {client.name} has been suspended"}


@router.post("/clients/{client_name}/resume")
def resume_client(
    client_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    if client.status != ClientStatus.SUSPENDED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client is not suspended"
        )
    
    if start_client_stack(client.name):
        client.status = ClientStatus.ACTIVE.value
        client.suspended_at = None
        db.commit()
        
        log_activity(db, current_user.id, client.id, "resume", f"Resumed client {client.name}")
        
        return {"success": True, "message": f"Client {client.name} has been resumed"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to resume client"
    )


@router.delete("/clients/{client_name}")
def delete_client(
    client_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete clients"
        )
    
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    stop_client_stack(client.name)
    remove_client_stack(client.name)
    
    nginx_config = f"/etc/nginx/sites-available/{client_name}.conf"
    nginx_enabled = f"/etc/nginx/sites-enabled/{client_name}.conf"
    
    import os
    for path in [nginx_config, nginx_enabled]:
        if os.path.exists(path):
            os.remove(path)
    
    client.status = ClientStatus.DELETED.value
    db.commit()
    
    log_activity(db, current_user.id, client.id, "delete", f"Deleted client {client.name}")
    
    reload_nginx()
    
    return {"success": True, "message": f"Client {client_name} has been deleted"}


@router.get("/clients/{client_name}/stats")
def get_client_stats(
    client_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    stats = get_container_stats(client_name)
    disk_usage = get_disk_usage(client_name)
    
    return {
        "containers": stats,
        "disk_usage_mb": disk_usage,
        "status": client.status
    }


@router.post("/clients/{client_name}/backup")
def create_backup(
    client_name: str,
    backup_type: str = "manual",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    result = trigger_backup(client_name, backup_type)
    
    log_activity(db, current_user.id, client.id, "backup", f"Started {backup_type} backup")
    
    return result


@router.get("/clients/{client_name}/domains")
def list_custom_domains(
    client_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    domains = json.loads(client.custom_domains or "[]")
    return {"domains": domains, "primary_domain": client.domain}


@router.post("/clients/{client_name}/domains")
def add_custom_domain(
    client_name: str,
    domain: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import re
    domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?(\.[a-zA-Z]{2,})+$'
    
    if not re.match(domain_pattern, domain):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid domain format"
        )
    
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    domains = json.loads(client.custom_domains or "[]")
    
    if domain in domains:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain already added"
        )
    
    existing_client = db.query(Client).filter(Client.domain == domain).first()
    if existing_client and existing_client.id != client.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain is already in use"
        )
    
    domains.append(domain)
    client.custom_domains = json.dumps(domains)
    db.commit()
    
    try:
        create_nginx_config(client)
        reload_nginx()
        request_ssl_certificate(domain, settings.SMTP_FROM)
        reload_nginx()
    except Exception as e:
        pass
    
    log_activity(db, current_user.id, client.id, "domain_add", f"Added custom domain: {domain}")
    
    return {"success": True, "domain": domain, "message": "Domain added. SSL certificate will be provisioned automatically."}


@router.delete("/clients/{client_name}/domains/{domain}")
def remove_custom_domain(
    client_name: str,
    domain: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    domains = json.loads(client.custom_domains or "[]")
    
    if domain not in domains:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    domains.remove(domain)
    client.custom_domains = json.dumps(domains)
    db.commit()
    
    remove_nginx_domain_config(client, domain)
    reload_nginx()
    
    log_activity(db, current_user.id, client.id, "domain_remove", f"Removed custom domain: {domain}")
    
    return {"success": True, "message": f"Domain {domain} removed"}


def remove_nginx_domain_config(client: Client, domain: str):
    import os
    nginx_config = f"/etc/nginx/sites-available/{client.name}_{domain.replace('.', '_')}.conf"
    nginx_enabled = f"/etc/nginx/sites-enabled/{client.name}_{domain.replace('.', '_')}.conf"
    
    for path in [nginx_config, nginx_enabled]:
        if os.path.exists(path):
            os.remove(path)


from datetime import datetime
