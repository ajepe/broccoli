import subprocess
import os
import logging
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
logger = logging.getLogger(__name__)


def get_s3_client():
    if not BOTO3_AVAILABLE:
        logger.warning("boto3 not available, S3 operations will fail")
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


def trigger_backup(client_name: str, backup_type: str = "manual", db: Session = None) -> dict:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{client_name}_{backup_type}_{timestamp}.sql.gz"
    s3_key = f"{settings.S3_PREFIX}{client_name}/{filename}"
    local_path = f"{settings.BACKUP_DIR}/{client_name}/{filename}"
    
    os.makedirs(f"{settings.BACKUP_DIR}/{client_name}", exist_ok=True)
    
    try:
        dump_result = subprocess.run(
            [
                "docker", "exec", f"db_{client_name}",
                "pg_dump", "-U", f"odoo_{client_name.replace('-', '_')}",
                "-Fc", "-f", f"/var/lib/postgresql/data/{filename}"
            ],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if dump_result.returncode != 0:
            logger.error(f"Failed to dump database: {dump_result.stderr}")
            return {"success": False, "message": f"Database dump failed: {dump_result.stderr}"}
        
        copy_result = subprocess.run(
            [
                "docker", "cp", f"db_{client_name}:/var/lib/postgresql/data/{filename}", local_path
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if copy_result.returncode != 0:
            logger.error(f"Failed to copy backup: {copy_result.stderr}")
            return {"success": False, "message": f"Copy failed: {copy_result.stderr}"}
        
        cleanup_dump = subprocess.run(
            [
                "docker", "exec", f"db_{client_name}", "rm", f"/var/lib/postgresql/data/{filename}"
            ],
            capture_output=True,
            text=True
        )
        
        s3 = get_s3_client()
        if s3:
            s3.upload_file(
                local_path,
                settings.S3_BUCKET,
                s3_key
            )
            logger.info(f"Uploaded backup to S3: {s3_key}")
        
        backup = Backup(
            client_id=0,
            client_name=client_name,
            backup_type=backup_type,
            filename=filename,
            s3_key=s3_key,
            size_mb=int(os.path.getsize(local_path) / (1024 * 1024)),
            status="completed"
        )
        
        if db:
            db.add(backup)
            db.commit()
        
        os.remove(local_path)
        
        logger.info(f"Backup completed for {client_name}")
        return {"success": True, "message": "Backup completed successfully", "filename": filename}
        
    except subprocess.TimeoutExpired:
        logger.error(f"Backup timed out for {client_name}")
        return {"success": False, "message": "Backup timed out"}
    except Exception as e:
        logger.error(f"Backup failed for {client_name}: {str(e)}")
        return {"success": False, "message": str(e)}


def restore_backup(client_name: str, backup_filename: str, db: Session) -> dict:
    backup = db.query(Backup).filter(
        Backup.filename == backup_filename,
        Backup.client_name == client_name
    ).first()
    
    if not backup:
        return {"success": False, "message": "Backup record not found"}
    
    s3 = get_s3_client()
    if not s3:
        return {"success": False, "message": "S3 not available"}
    
    try:
        local_path = f"/tmp/{backup_filename}"
        
        s3.download_file(
            settings.S3_BUCKET,
            backup.s3_key,
            local_path
        )
        
        restore_result = subprocess.run(
            [
                "docker", "exec", f"db_{client_name}",
                "psql", "-U", f"odoo_{client_name.replace('-', '_')}",
                "-c", f"DROP DATABASE IF EXISTS {f'odoo_{client_name.replace('-', '_')}'}"
            ],
            capture_output=True,
            text=True
        )
        
        subprocess.run(
            [
                "docker", "exec", f"db_{client_name}",
                "createdb", "-U", f"odoo_{client_name.replace('-', '_')}",
                f"odoo_{client_name.replace('-', '_')}"
            ],
            capture_output=True,
            text=True
        )
        
        restore_result = subprocess.run(
            [
                "docker", "exec", "-i", f"db_{client_name}",
                "pg_restore", "-U", f"odoo_{client_name.replace('-', '_')}",
                "-d", f"odoo_{client_name.replace('-', '_')}"
            ],
            stdin=open(local_path, 'rb'),
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if os.path.exists(local_path):
            os.remove(local_path)
        
        logger.info(f"Restore completed for {client_name}")
        return {"success": True, "message": "Restore completed successfully"}
        
    except Exception as e:
        logger.error(f"Restore failed for {client_name}: {str(e)}")
        return {"success": False, "message": str(e)}


def delete_backup(backup_id: int, db: Session) -> dict:
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    
    if not backup:
        return {"success": False, "message": "Backup not found"}
    
    try:
        if backup.s3_key:
            s3 = get_s3_client()
            if s3:
                s3.delete_object(
                    Bucket=settings.S3_BUCKET,
                    Key=backup.s3_key
                )
        
        db.delete(backup)
        db.commit()
        
        logger.info(f"Deleted backup {backup_id}")
        return {"success": True, "message": "Backup deleted"}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete backup {backup_id}: {str(e)}")
        return {"success": False, "message": str(e)}


def get_backup_status(client_name: str) -> dict:
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name=odoo_{client_name}", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        return {
            "container_status": result.stdout.strip() or "not running",
            "last_backup": None,
            "next_scheduled": None
        }
    except Exception as e:
        logger.error(f"Failed to get backup status: {str(e)}")
        return {"container_status": "error", "error": str(e)}
