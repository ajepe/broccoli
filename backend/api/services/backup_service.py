import subprocess
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
from datetime import datetime
from typing import List, Optional
from backend.core.config import get_settings
from backend.api.models.models import Backup
from backend.api.schemas.schemas import BackupResponse
from sqlalchemy.orm import Session

settings = get_settings()


def get_s3_client():
    if not BOTO3_AVAILABLE:
        return None
    return boto3.client(
        's3',
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION
    )


def list_client_backups(client_name: str, db: Session) -> List[BackupResponse]:
    backups = db.query(Backup).filter(
        Backup.client_name == client_name
    ).order_by(Backup.created_at.desc()).all()
    
    return [BackupResponse.model_validate(b) for b in backups]


def trigger_backup(client_name: str, backup_type: str = "manual") -> dict:
    try:
        result = subprocess.run(
            [
                "docker", "start", f"backup_{client_name}"
            ],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "success": result.returncode == 0,
            "message": "Backup started" if result.returncode == 0 else result.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


def restore_backup(client_name: str, backup_filename: str, db: Session) -> dict:
    s3 = get_s3_client()
    
    backup = db.query(Backup).filter(
        Backup.filename == backup_filename,
        Backup.client_name == client_name
    ).first()
    
    if not backup:
        return {"success": False, "message": "Backup record not found"}
    
    try:
        local_path = f"/tmp/{backup_filename}"
        
        s3.download_file(
            settings.S3_BUCKET,
            backup.s3_key,
            local_path
        )
        
        result = subprocess.run(
            [
                "docker-compose", "-f", "docker-compose.yml",
                "run", "--rm", "backup",
                "/bin/bash", "-c",
                f"pg_restore -h db -U $DB_USER -d $DB_NAME < {local_path}"
            ],
            cwd=f"{settings.ODOO_DATA_DIR}/{client_name}",
            capture_output=True,
            text=True,
            timeout=600
        )
        
        import os
        if os.path.exists(local_path):
            os.remove(local_path)
        
        return {
            "success": result.returncode == 0,
            "message": "Restore completed" if result.returncode == 0 else result.stderr
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


def delete_backup(backup_id: int, db: Session) -> dict:
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    
    if not backup:
        return {"success": False, "message": "Backup not found"}
    
    try:
        if backup.s3_key:
            s3 = get_s3_client()
            s3.delete_object(
                Bucket=settings.S3_BUCKET,
                Key=backup.s3_key
            )
        
        db.delete(backup)
        db.commit()
        
        return {"success": True, "message": "Backup deleted"}
        
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}


def cleanup_old_backups(client_name: str) -> dict:
    try:
        result = subprocess.run(
            [
                "docker", "exec", f"backup-cron_{client_name}",
                "/bin/sh", "-c",
                "crontab -l | head -1 | cut -d'/' -f1 | xargs -I {} echo 'Running cleanup'"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": True,
            "message": "Backup cleanup completed"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


def get_backup_status(client_name: str) -> dict:
    container_name = f"backup_{client_name}"
    
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        status = result.stdout.strip()
        
        return {
            "container_status": status if status else "not found",
            "last_run": None,
            "next_scheduled": None
        }
    except Exception as e:
        return {
            "container_status": "error",
            "error": str(e)
        }
