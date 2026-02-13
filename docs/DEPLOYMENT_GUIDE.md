# Odoo Cloud Africa - Deployment Guide

## Prerequisites

- Ubuntu 22.04 LTS (minimum 4GB RAM, 2 CPU cores)
- Domain name with DNS configured
- S3-compatible storage (AWS S3, MinIO, Backblaze B2)
- SMTP credentials for email alerts

## Quick Start

### 1. Initial Server Setup

```bash
# Run as root or with sudo
cd /home/babatope/Documents/projects/saas/infrastructure/scripts
chmod +x deploy.sh
./deploy.sh
```

### 2. Configure Environment

```bash
cd /home/babatope/Documents/projects/saas/backend
cp env.template .env

# Edit .env with your configuration
nano .env
```

### 3. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE odoo_cloud_platform;
CREATE USER odoo_cloud WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE odoo_cloud_platform TO odoo_cloud;
\q
```

### 4. Start Control Panel

```bash
cd /home/babatope/Documents/projects/saas/backend
source venv/bin/activate

# Run migrations
python -m alembic upgrade head

# Create admin user
python -c "
from backend.core.database import SessionLocal
from backend.api.models.models import User
from backend.core.security import get_password_hash
db = SessionLocal()
admin = User(
    email='admin@yourdomain.com',
    username='admin',
    hashed_password=get_password_hash('admin123'),
    is_superuser=True
)
db.add(admin)
db.commit()
db.close()
"

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start Monitoring Stack

```bash
cd /home/babatope/Documents/projects/saas/infrastructure/scripts
chmod +x start-monitoring.sh
./start-monitoring.sh
```

### 6. Configure Nginx for Control Panel

```nginx
server {
    listen 80;
    server_name cloud.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 7. Get SSL Certificate

```bash
sudo certbot --nginx -d cloud.yourdomain.com
```

## Architecture Overview

```
                                    ┌─────────────────┐
                                    │   DNS (Route53) │
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │  Nginx Reverse │
                                    │      Proxy      │
                                    └────────┬────────┘
                                             │
                     ┌───────────────────────┼───────────────────────┐
                     │                       │                       │
            ┌────────▼────────┐      ┌────────▼────────┐      ┌────────▼────────┐
            │  Client A       │      │  Client B       │      │  Client N       │
            │  ┌───────────┐   │      │  ┌───────────┐   │      │  ┌───────────┐   │
            │  │   Odoo    │   │      │  │   Odoo    │   │      │  │   Odoo    │   │
            │  │ Container │   │      │  │ Container │   │      │  │ Container │   │
            │  └─────┬─────┘   │      │  └─────┬─────┘   │      │  └─────┬─────┘   │
            │        │         │      │        │         │      │        │         │
            │  ┌─────▼─────┐   │      │  ┌─────▼─────┐   │      │  ┌─────▼─────┐   │
            │  │ PostgreSQL │   │      │  │ PostgreSQL │   │      │  │ PostgreSQL │   │
            │  │ Container  │   │      │  │ Container  │   │      │  │ Container  │   │
            │  └───────────┘   │      │  └───────────┘   │      │  └───────────┘   │
            └───────────────────┘      └───────────────────┘      └───────────────────┘
                                             │
                                    ┌────────▼────────┐
                                    │   S3 Storage     │
                                    │   (Backups)      │
                                    └──────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────┐
│                              CONTROL PLANE                                        │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │   FastAPI    │   │  PostgreSQL  │   │  Prometheus  │   │   Grafana    │       │
│  │   Backend    │   │  (Metadata)  │   │  (Metrics)   │   │   (Dashboards│       │
│  └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘       │
│                                                                                   │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                          │
│  │  Vue.js UI   │   │  Node Exp.   │   │  cAdvisor    │                          │
│  │  (Dashboard) │   │  (Host)      │   │  (Containers)                          │
│  └──────────────┘   └──────────────┘   └──────────────┘                          │
└──────────────────────────────────────────────────────────────────────────────────┘
```

## Managing Clients

### Create Client

```bash
# Via API
curl -X POST http://localhost:8000/api/clients \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "acme-corp",
    "domain": "acme-corp.yourdomain.com",
    "email": "admin@acmecorp.com",
    "plan": "business",
    "redis_enabled": true
  }'
```

### Suspend Client

```bash
curl -X POST http://localhost:8000/api/clients/acme-corp/suspend \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Delete Client

```bash
curl -X DELETE http://localhost:8000/api/clients/acme-corp \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Monitoring

- **Grafana**: http://your-server:3000
- **Prometheus**: http://your-server:9090
- **Node Exporter**: http://your-server:9100
- **cAdvisor**: http://your-server:8080

## Backup

Backups are automated and run daily at 2 AM. They are:
- Compressed with gzip
- Encrypted with GPG
- Uploaded to S3
- Retained: 7 daily, 4 weekly, 3 monthly

## Troubleshooting

### Check Container Logs

```bash
docker logs odoo_clientname
docker logs db_clientname
```

### Check Resource Usage

```bash
docker stats
```

### Restart Client Stack

```bash
cd /opt/odoo-clients/clientname
docker-compose restart
```

### Check SSL Certificate

```bash
sudo certbot certificates
sudo certbot renew --dry-run
```

## Scaling Considerations

### Stage 2: Separate DB Server
- Move PostgreSQL to dedicated server
- Use connection pooling (PgBouncer)
- Configure replication

### Stage 3: Horizontal Scaling
- Add load balancer (HAProxy)
- Implement GlusterFS for shared storage
- Use Redis for session sharing
