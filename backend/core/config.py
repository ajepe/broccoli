from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    APP_NAME: str = "Odoo Cloud Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    USE_SQLITE: bool = True
    
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "odoo_cloud"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "odoo_cloud_platform"
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    SECRET_KEY: str = "dev-secret-key-change-in-production-12345678901234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DOCKER_SOCKET_PATH: str = "/var/run/docker.sock"
    ODOO_DATA_DIR: str = "/home/babatope/Documents/projects/saas/clients"
    NGINX_CONFIG_DIR: str = "/home/babatope/Documents/projects/saas/nginx/sites-available"
    NGINX_ENABLED_DIR: str = "/home/babatope/Documents/projects/saas/nginx/sites-enabled"
    BACKUP_DIR: str = "/home/babatope/Documents/projects/saas/backups"
    
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
        env_file = "/home/babatope/Documents/projects/saas/backend/.env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings():
    return Settings()
