from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import json
import os

from backend.core.database import get_db
from backend.core.security import verify_password, create_access_token, create_refresh_token, decode_access_token, get_password_hash
from backend.api.models.models import Client, User, ClientStatus, ActivityLog
from backend.api.schemas.schemas import (
    ClientCreate, ClientUpdate, ClientResponse, ClientDetailResponse,
    ClientStats, UserCreate, UserResponse, Token
)
from backend.api.services.provisioning import (
    generate_secure_password, generate_db_name, generate_db_user, get_next_odoo_port,
    get_plan_resources, create_client_directories, create_docker_compose, create_env_file,
    create_nginx_config, start_client_stack, stop_client_stack, remove_client_stack,
    reload_nginx, request_ssl_certificate, get_container_stats, get_disk_usage,
    create_external_database, delete_external_database
)
from backend.api.services.backup_service import trigger_backup
from backend.core.config import get_settings

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
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/auth/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        new_access_token = create_access_token(data={"sub": user.username})
        new_refresh_token = create_refresh_token(data={"sub": user.username})
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


@router.get("/system/metrics")
def get_system_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import subprocess
    import psutil
    
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        container_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        
        total_clients = db.query(Client).count()
        active_clients = db.query(Client).filter(Client.status == ClientStatus.ACTIVE.value).count()
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "percent": disk.percent
            },
            "containers": {
                "running": container_count
            },
            "clients": {
                "total": total_clients,
                "active": active_clients
            }
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/clients", response_model=List[ClientResponse])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    include_scheduled: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Client)
    
    if status:
        query = query.filter(Client.status == status)
    
    if not current_user.is_superuser:
        query = query.filter(Client.status != ClientStatus.SCHEDULED_FOR_DELETION.value)
    
    if include_scheduled and current_user.is_superuser:
        pass
    
    clients = query.offset(skip).limit(limit).all()
    
    for client in clients:
        if client.custom_domains and isinstance(client.custom_domains, str):
            import json
            client.custom_domains = json.loads(client.custom_domains)
        elif not client.custom_domains:
            client.custom_domains = []
    
    return clients


@router.get("/clients/stats", response_model=ClientStats)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = db.query(Client).count()
    active = db.query(Client).filter(Client.status == ClientStatus.ACTIVE.value).count()
    suspended = db.query(Client).filter(Client.status == ClientStatus.SUSPENDED.value).count()
    
    return ClientStats(
        total_clients=total,
        active_clients=active,
        suspended_clients=suspended,
        total_disk_usage_mb=0,
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
    
    from datetime import timedelta
    payment_deadline = datetime.utcnow() + timedelta(hours=24)
    
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
        payment_deadline=payment_deadline,
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    try:
        db_created = create_external_database(
            client.db_name,
            client.db_user,
            db_password
        )
        
        if not db_created:
            print("Warning: Could not create external database")
        
        create_client_directories(client.name)
        create_docker_compose(client, db_password)
        create_env_file(client, db_password, settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY)
        
        log_activity(db, current_user.id, client.id, "create", f"Created pending client {client.name} - awaiting payment")
        
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
    
    if client.custom_domains and isinstance(client.custom_domains, str):
        import json
        client.custom_domains = json.loads(client.custom_domains)
    elif not client.custom_domains:
        client.custom_domains = []
    
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


@router.post("/clients/{client_name}/schedule-delete")
def schedule_delete(
    client_name: str,
    hours_until_deletion: int = 12,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    is_owner = client.email == current_user.email
    is_admin = current_user.is_superuser
    
    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only schedule deletion of your own clients"
        )
    
    if client.status == ClientStatus.SCHEDULED_FOR_DELETION.value:
        return {
            "success": True,
            "message": "Client is already scheduled for deletion",
            "deletion_time": client.deletion_scheduled_at
        }
    
    if client.status == ClientStatus.DELETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client has already been deleted"
        )
    
    from datetime import timedelta
    deletion_time = datetime.utcnow() + timedelta(hours=hours_until_deletion)
    
    client.status = ClientStatus.SCHEDULED_FOR_DELETION.value
    client.deletion_scheduled_at = deletion_time
    
    try:
        stop_client_stack(client.name)
    except Exception:
        pass
    
    db.commit()
    
    log_activity(
        db, 
        current_user.id, 
        client.id, 
        "schedule_delete", 
        f"Scheduled deletion of {client.name} for {deletion_time}"
    )
    
    return {
        "success": True,
        "message": f"Client scheduled for deletion in {hours_until_deletion} hours",
        "deletion_time": deletion_time,
        "can_cancel_until": deletion_time
    }


@router.post("/clients/{client_name}/cancel-delete")
def cancel_delete(
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
    
    if client.status != ClientStatus.SCHEDULED_FOR_DELETION.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client is not scheduled for deletion"
        )
    
    is_owner = client.email == current_user.email
    is_admin = current_user.is_superuser
    
    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel deletion of your own clients"
        )
    
    client.status = ClientStatus.ACTIVE.value
    client.deletion_scheduled_at = None
    
    try:
        start_client_stack(client.name)
    except Exception:
        pass
    
    db.commit()
    
    log_activity(
        db, 
        current_user.id, 
        client.id, 
        "cancel_delete", 
        f"Cancelled deletion of {client.name}"
    )
    
    return {
        "success": True,
        "message": "Client deletion cancelled - instance restored"
    }


@router.post("/clients/{client_name}/force-delete")
def force_delete(
    client_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can force delete clients"
        )
    
    client = db.query(Client).filter(Client.name == client_name).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    db_name = client.db_name
    db_user = client.db_user
    
    try:
        stop_client_stack(client.name)
        remove_client_stack(client.name)
    except Exception:
        pass
    
    try:
        delete_external_database(db_name, db_user)
    except Exception:
        pass
    
    import os
    nginx_config = f"/etc/nginx/sites-available/{client_name}.conf"
    nginx_enabled = f"/etc/nginx/sites-enabled/{client_name}.conf"
    for path in [nginx_config, nginx_enabled]:
        if os.path.exists(path):
            os.remove(path)
    
    client.status = ClientStatus.DELETED.value
    db.commit()
    
    log_activity(
        db, 
        current_user.id, 
        client.id, 
        "force_delete", 
        f"Force deleted client {client.name}"
    )
    
    try:
        reload_nginx()
    except Exception:
        pass
    
    return {"success": True, "message": f"Client {client_name} has been force deleted"}


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


@router.get("/backups")
def list_all_backups(
    skip: int = 0,
    limit: int = 50,
    client_name: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from backend.api.models.models import Backup
    
    query = db.query(Backup)
    
    if client_name:
        query = query.filter(Backup.client_name == client_name)
    
    backups = query.order_by(Backup.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"backups": backups, "total": query.count()}


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


@router.post("/clients/{client_name}/activate")
def activate_client(
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
    
    if client.status == ClientStatus.ACTIVE.value:
        return {"success": True, "message": "Client is already active"}
    
    try:
        if start_client_stack(client.name):
            client.status = ClientStatus.ACTIVE.value
            client.activated_at = datetime.utcnow()
            
            create_nginx_config(client)
            reload_nginx()
            
            try:
                request_ssl_certificate(client.domain, settings.SMTP_FROM)
                reload_nginx()
            except Exception:
                pass
            
            db.commit()
            
            log_activity(db, current_user.id, client.id, "activate", f"Activated client {client.name}")
            
            return {"success": True, "message": "Client activated successfully"}
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start client services"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Activation failed: {str(e)}"
        )


@router.post("/cleanup/expired-clients")
def cleanup_expired_clients(
    db: Session = Depends(get_db),
    admin_token: str = None
):
    if not settings.DEBUG and admin_token != os.getenv("ADMIN_CLEANUP_TOKEN"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin token"
        )
    
    now = datetime.utcnow()
    
    expired_clients = db.query(Client).filter(
        Client.status == ClientStatus.PENDING.value,
        Client.payment_deadline < now
    ).all()
    
    scheduled_for_deletion = db.query(Client).filter(
        Client.status == ClientStatus.SCHEDULED_FOR_DELETION.value,
        Client.deletion_scheduled_at < now
    ).all()
    
    all_to_delete = expired_clients + scheduled_for_deletion
    
    deleted_count = 0
    for client in all_to_delete:
        db_name = client.db_name
        db_user = client.db_user
        
        try:
            stop_client_stack(client.name)
            remove_client_stack(client.name)
        except Exception:
            pass
        
        try:
            delete_external_database(db_name, db_user)
        except Exception:
            pass
        
        import os
        nginx_config = f"/etc/nginx/sites-available/{client.name}.conf"
        nginx_enabled = f"/etc/nginx/sites-enabled/{client.name}.conf"
        for path in [nginx_config, nginx_enabled]:
            if os.path.exists(path):
                os.remove(path)
        
        try:
            reload_nginx()
        except Exception:
            pass
        
        client.status = ClientStatus.DELETED.value
        db.commit()
        
        log_activity(db, None, client.id, "cleanup", f"Auto-deleted client: {client.name}")
        deleted_count += 1
    
    return {
        "success": True,
        "deleted": deleted_count,
        "unpaid_expired": len(expired_clients),
        "scheduled_deletions": len(scheduled_for_deletion),
        "message": f"Cleaned up {deleted_count} clients"
    }


@router.get("/clients/pending")
def get_pending_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    now = datetime.utcnow()
    pending = db.query(Client).filter(
        Client.status == ClientStatus.PENDING.value
    ).all()
    
    result = []
    for client in pending:
        is_expired = client.payment_deadline and client.payment_deadline < now
        result.append({
            "id": client.id,
            "name": client.name,
            "domain": client.domain,
            "email": client.email,
            "plan": client.plan,
            "payment_deadline": client.payment_deadline,
            "created_at": client.created_at,
            "is_expired": is_expired
        })
    
    return result
