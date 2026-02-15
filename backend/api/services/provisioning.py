import os
import secrets
import string
import subprocess
import json
import logging
from typing import Optional
from datetime import datetime
from jinja2 import Template

from backend.core.config import get_settings
from backend.api.models.models import Client, ClientStatus

settings = get_settings()
logger = logging.getLogger(__name__)


def generate_secure_password(length: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)):
            return password


def generate_db_name(client_name: str) -> str:
    return f"odoo_{client_name.replace('-', '_')}"


def generate_db_user(client_name: str) -> str:
    return f"odoo_{client_name.replace('-', '_')}"


def create_external_database(db_name: str, db_user: str, db_password: str) -> bool:
    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        logger.warning("psycopg2 not installed, skipping database creation")
        return False
    
    try:
        conn = psycopg2.connect(
            host=settings.EXTERNAL_DB_HOST,
            port=settings.EXTERNAL_DB_PORT,
            user=settings.EXTERNAL_DB_USER,
            password=settings.EXTERNAL_DB_PASSWORD,
            database=settings.EXTERNAL_DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
            sql.Identifier(db_user)
        ), [db_password])
        
        cursor.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(
            sql.Identifier(db_name),
            sql.Identifier(db_user)
        ))
        
        cursor.close()
        conn.close()
        
        logger.info(f"Created database {db_name} and user {db_user} on external PostgreSQL")
        return True
        
    except psycopg2.errors.DuplicateDatabase:
        logger.info(f"Database {db_name} already exists")
        return True
    except psycopg2.errors.DuplicateObject:
        logger.info(f"User {db_user} already exists")
        return True
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False


def delete_external_database(db_name: str, db_user: str) -> bool:
    try:
        import psycopg2
        from psycopg2 import sql
    except ImportError:
        logger.warning("psycopg2 not installed, skipping database deletion")
        return False
    
    try:
        conn = psycopg2.connect(
            host=settings.EXTERNAL_DB_HOST,
            port=settings.EXTERNAL_DB_PORT,
            user=settings.EXTERNAL_DB_USER,
            password=settings.EXTERNAL_DB_PASSWORD,
            database=settings.EXTERNAL_DB_NAME
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(
            sql.Identifier(db_name)
        ))
        
        cursor.execute(sql.SQL("DROP USER IF EXISTS {}").format(
            sql.Identifier(db_user)
        ))
        
        cursor.close()
        conn.close()
        
        logger.info(f"Deleted database {db_name} and user {db_user} from external PostgreSQL")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting database: {e}")
        return False


def get_next_odoo_port() -> int:
    clients_dir = settings.ODOO_DATA_DIR
    
    if not os.path.exists(clients_dir):
        os.makedirs(clients_dir, exist_ok=True)
        return settings.DEFAULT_ODOO_PORT_START
    
    used_ports = set()
    for client_name in os.listdir(clients_dir):
        client_path = os.path.join(clients_dir, client_name)
        if os.path.isdir(client_path):
            env_file = os.path.join(client_path, ".env")
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith("ODOO_PORT="):
                            port = line.split("=")[1].strip()
                            try:
                                used_ports.add(int(port))
                            except ValueError:
                                pass
    
    if not used_ports:
        return settings.DEFAULT_ODOO_PORT_START
    
    return max(used_ports) + 1


def render_template(template_path: str, context: dict) -> str:
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    return template.render(**context)


def get_plan_resources(plan: str) -> dict:
    plan_configs = {
        "basic": {
            "memory_limit": settings.PLAN_BASIC_RAM,
            "db_memory_limit": settings.PLAN_BASIC_DB_RAM,
            "cpu_limit": settings.PLAN_BASIC_CPU,
            "backup_frequency": "daily",
        },
        "business": {
            "memory_limit": settings.PLAN_BUSINESS_RAM,
            "db_memory_limit": settings.PLAN_BUSINESS_DB_RAM,
            "cpu_limit": settings.PLAN_BUSINESS_CPU,
            "backup_frequency": "hourly",
        },
        "enterprise": {
            "memory_limit": settings.PLAN_ENTERPRISE_RAM,
            "db_memory_limit": settings.PLAN_ENTERPRISE_DB_RAM,
            "cpu_limit": settings.PLAN_ENTERPRISE_CPU,
            "backup_frequency": "hourly",
        },
    }
    return plan_configs.get(plan.lower(), plan_configs["basic"])


def create_client_directories(client_name: str) -> None:
    client_dir = os.path.join(settings.ODOO_DATA_DIR, client_name)
    os.makedirs(client_dir, exist_ok=True)
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)


def create_docker_compose(client: Client, db_password: str) -> None:
    template_path = "/home/babatope/Documents/projects/saas/infrastructure/docker/templates/docker-compose.yml.j2"
    
    context = {
        "CLIENT_NAME": client.name,
        "CLIENT_DOMAIN": client.domain,
        "DB_NAME": client.db_name,
        "DB_USER": client.db_user,
        "DB_PASSWORD": db_password,
        "DB_HOST": settings.EXTERNAL_DB_HOST,
        "DB_PORT": settings.EXTERNAL_DB_PORT,
        "ODOO_PORT": client.odoo_port,
        "MEMORY_LIMIT": client.memory_limit,
        "DB_MEMORY_LIMIT": client.db_memory_limit,
        "CPU_LIMIT": client.cpu_limit,
        "DB_CPU_LIMIT": client.db_cpu_limit,
        "redis_enabled": client.redis_enabled,
        "REDIS_MEMORY": "512m" if client.redis_enabled else None,
        "PLAN": client.plan,
    }
    
    docker_compose_content = render_template(template_path, context)
    
    output_path = os.path.join(settings.ODOO_DATA_DIR, client.name, "docker-compose.yml")
    with open(output_path, 'w') as f:
        f.write(docker_compose_content)


def create_env_file(client: Client, db_password: str, s3_access_key: str, s3_secret_key: str) -> None:
    env_content = f"""CLIENT_NAME={client.name}
CLIENT_DOMAIN={client.domain}
DB_NAME={client.db_name}
DB_USER={client.db_user}
DB_PASSWORD={db_password}
ODOO_PORT={client.odoo_port}
MEMORY_LIMIT={client.memory_limit}
DB_MEMORY_LIMIT={client.db_memory_limit}
CPU_LIMIT={client.cpu_limit}
DB_CPU_LIMIT={client.db_cpu_limit}
PLAN={client.plan}

# External PostgreSQL (shared across all clients)
DB_HOST={settings.EXTERNAL_DB_HOST}
DB_PORT={settings.EXTERNAL_DB_PORT}

S3_BUCKET={settings.S3_BUCKET}
S3_PREFIX={settings.S3_PREFIX}
S3_ACCESS_KEY={s3_access_key}
S3_SECRET_KEY={s3_secret_key}
S3_ENDPOINT={settings.S3_ENDPOINT}
S3_REGION={settings.S3_REGION}

RETENTION_DAILY={client.backup_retention_daily}
RETENTION_WEEKLY={client.backup_retention_weekly}
RETENTION_MONTHLY={client.backup_retention_monthly}

BACKUP_SCHEDULE=0 2 * * *
"""
    
    output_path = os.path.join(settings.ODOO_DATA_DIR, client.name, ".env")
    with open(output_path, 'w') as f:
        f.write(env_content)


def create_nginx_config(client: Client) -> None:
    template_path = "/home/babatope/Documents/projects/saas/infrastructure/nginx/sites-available/client.conf.j2"
    
    custom_domains = json.loads(client.custom_domains or "[]")
    all_domains = [client.domain] + custom_domains
    
    context = {
        "client_name": client.name,
        "client_domain": client.domain,
        "odoo_port": client.odoo_port,
        "all_domains": all_domains,
    }
    
    nginx_content = render_template(template_path, context)
    
    output_path = os.path.join(settings.NGINX_CONFIG_DIR, f"{client.name}.conf")
    with open(output_path, 'w') as f:
        f.write(nginx_content)
    
    symlink_path = os.path.join(settings.NGINX_ENABLED_DIR, f"{client.name}.conf")
    if not os.path.exists(symlink_path):
        os.symlink(output_path, symlink_path)


def start_client_stack(client_name: str) -> bool:
    client_dir = os.path.join(settings.ODOO_DATA_DIR, client_name)
    
    try:
        subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=client_dir,
            check=True,
            capture_output=True,
            timeout=300
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Docker Compose: {e.stderr.decode()}")
        return False
    except Exception as e:
        logger.error(f"Error starting client stack: {e}")
        return False


def stop_client_stack(client_name: str) -> bool:
    client_dir = os.path.join(settings.ODOO_DATA_DIR, client_name)
    
    try:
        subprocess.run(
            ["docker-compose", "down"],
            cwd=client_dir,
            check=True,
            capture_output=True,
            timeout=120
        )
        return True
    except Exception as e:
        logger.error(f"Error stopping client stack: {e}")
        return False


def remove_client_stack(client_name: str) -> bool:
    client_dir = os.path.join(settings.ODOO_DATA_DIR, client_name)
    
    try:
        subprocess.run(
            ["docker-compose", "down", "-v", "--remove-orphans"],
            cwd=client_dir,
            check=True,
            capture_output=True,
            timeout=120
        )
        
        import shutil
        if os.path.exists(client_dir):
            shutil.rmtree(client_dir)
        
        return True
    except Exception as e:
        logger.error(f"Error removing client stack: {e}")
        return False


def reload_nginx() -> bool:
    try:
        subprocess.run(
            ["nginx", "-t"],
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["systemctl", "reload", "nginx"],
            check=True,
            capture_output=True
        )
        return True
    except Exception as e:
        logger.error(f"Error reloading nginx: {e}")
        return False


def get_container_stats(client_name: str) -> list:
    try:
        result = subprocess.run(
            [
                "docker", "stats", "--no-stream", "--format",
                "{{.Container}},{{.Name}},{{.Status}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.PIDs}}"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        stats = []
        for line in result.stdout.strip().split('\n'):
            if client_name in line:
                parts = line.split(',')
                if len(parts) >= 8:
                    container_id = parts[0]
                    name = parts[1]
                    status = parts[2]
                    cpu = parts[3]
                    mem_usage = parts[4]
                    mem_perc = parts[5]
                    net_io = parts[6]
                    pids = parts[7]
                    
                    stats.append({
                        "container_id": container_id,
                        "name": name,
                        "status": status,
                        "cpu_percent": cpu,
                        "memory_usage": mem_usage,
                        "memory_percent": mem_perc,
                        "network_io": net_io,
                        "pids": pids
                    })
        
        return stats
    except Exception as e:
        logger.error(f"Error getting container stats: {e}")
        return []


def get_disk_usage(client_name: str) -> int:
    client_dir = os.path.join(settings.ODOO_DATA_DIR, client_name)
    
    if not os.path.exists(client_dir):
        return 0
    
    try:
        result = subprocess.run(
            ["du", "-sm", client_dir],
            capture_output=True,
            text=True,
            check=True
        )
        
        size = result.stdout.split()[0]
        return int(size)
    except Exception:
        return 0


def request_ssl_certificate(domain: str, email: str) -> bool:
    try:
        result = subprocess.run(
            [
                "certbot", "certonly", "--nginx", "-d", domain,
                "--non-interactive", "--agree-tos", "--email", email
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error requesting SSL certificate: {e}")
        return False
