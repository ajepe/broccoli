from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    APP_NAME: str = "Odoo Cloud Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    USE_SQLITE: bool = True
    
    # Platform domain (e.g., lvh.me, cloud.yourdomain.com)
    BASE_DOMAIN: str = "lvh.me"
    
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Platform database (SQLite for control panel)
    DATABASE_URL: str = "sqlite:///./odoo_cloud.db"
    
    # External PostgreSQL for client databases (separate VPS)
    EXTERNAL_DB_HOST: str = "10.0.0.20"
    EXTERNAL_DB_PORT: int = 5432
    EXTERNAL_DB_USER: str = "odoo_clients"
    EXTERNAL_DB_PASSWORD: str = "change_me_strong_password"
    EXTERNAL_DB_NAME: str = "template1"
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    SECRET_KEY: str = "dev-secret-key-change-in-production-12345678901234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DOCKER_SOCKET_PATH: str = "/var/run/docker.sock"
    ODOO_DATA_DIR: str = os.getenv("ODOO_DATA_DIR", "/home/babatope/Documents/projects/saas/clients")
    NGINX_CONFIG_DIR: str = os.getenv("NGINX_CONFIG_DIR", "/etc/nginx/sites-available")
    NGINX_ENABLED_DIR: str = os.getenv("NGINX_ENABLED_DIR", "/etc/nginx/sites-enabled")
    BACKUP_DIR: str = os.getenv("BACKUP_DIR", "/home/babatope/Documents/projects/saas/backups")
    
    S3_ENDPOINT: str = "https://s3.amazonaws.com"
    S3_BUCKET: str = "odoo-backups"
    S3_ACCESS_KEY: str = "test-key"
    S3_SECRET_KEY: str = "test-secret"
    S3_REGION: str = "eu-west-1"
    S3_PREFIX: str = "clients/"
    
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "alerts@yourdomain.com"
    SMTP_PASSWORD: str = "smtp_password"
    SMTP_FROM: str = "Odoo Cloud <alerts@yourdomain.com>"
    
    DEFAULT_ODOO_PORT_START: int = 20000
    DEFAULT_MEMORY_LIMIT: str = "2g"
    DEFAULT_DB_MEMORY_LIMIT: str = "1g"
    DEFAULT_CPU_LIMIT: float = 1.0
    DEFAULT_DB_CPU_LIMIT: float = 0.5
    
    PLAN_BASIC_RAM: str = "2g"
    PLAN_BASIC_DB_RAM: str = "1g"
    PLAN_BASIC_CPU: float = 1.0
    PLAN_BUSINESS_RAM: str = "4g"
    PLAN_BUSINESS_DB_RAM: str = "2g"
    PLAN_BUSINESS_CPU: float = 2.0
    PLAN_ENTERPRISE_RAM: str = "8g"
    PLAN_ENTERPRISE_DB_RAM: str = "4g"
    PLAN_ENTERPRISE_CPU: float = 4.0
    
    PAYSTACK_SECRET_KEY: str = "sk_test_xxx"
    PAYSTACK_PUBLIC_KEY: str = "pk_test_xxx"
    PAYSTACK_WEBHOOK_SECRET: str = "whsec_xxx"
    
    FRONTEND_URL: str = "http://localhost:5173"
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings():
    return Settings()
