# Odoo Cloud Africa - Deployment Guide

## What's New (v2.0)

- **External PostgreSQL** - Single centralized database server (not per-client)
- **Token Refresh** - JWT refresh token mechanism
- **Soft Delete** - Clients scheduled for deletion, auto-cleanup after 12 hours
- **Custom Domains** - Users can whitelist their own domains
- **Payment Flow** - Clients created as "pending" until payment confirmed
- **Rate Limiting** - Protected auth endpoints
- **HTTPS Enforcement** - Auto-redirect in production

## Prerequisites

- Ubuntu 22.04 LTS (minimum 4GB RAM, 2 CPU cores)
- Domain name with DNS configured
- S3-compatible storage (AWS S3, MinIO, Backblaze B2)
- SMTP credentials for email alerts
- **Separate VPS for PostgreSQL** (recommended for production)

## Architecture

```
                                    ┌─────────────────┐
                                    │   DNS (Route53) │
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │  Nginx Reverse  │
                                    │     Proxy      │
                                    └────────┬────────┘
                                             │
                    ┌─────────────────────────┼─────────────────────────┐
                    │                         │                         │
            ┌──────▼──────┐          ┌──────▼──────┐          ┌──────▼──────┐
            │  Client A   │          │  Client B   │          │  Client N   │
            │  ┌────────┐ │          │  ┌────────┐ │          │  ┌────────┐ │
            │  │ Odoo   │ │          │  │ Odoo   │ │          │  │ Odoo   │ │
            │  │(Docker)│ │          │  │(Docker)│ │          │  │(Docker)│ │
            │  └────────┘ │          │  └────────┘ │          │  └────────┘ │
            │  ┌────────┐ │          │  ┌────────┐ │          │  ┌────────┐ │
            │  │ Redis  │ │          │  │ Redis  │ │          │  │ Redis  │ │
            │  │(Cache) │ │          │  │(Cache) │ │          │  │(Cache) │ │
            │  └────────┘ │          │  └────────┘ │          │  └────────┘ │
            └──────────────┘          └──────────────┘          └──────────────┘
                    │                         │                         │
                    └─────────────────────────┼─────────────────────────┘
                                              │
                                    ┌─────────▼─────────┐
                                    │  External PostgreSQL│
                                    │     (VPS #2)      │
                                    └─────────┬─────────┘
                                              │
                                    ┌─────────▼─────────┐
                                    │   S3 Storage      │
                                    │   (Backups)       │
                                    └───────────────────┘
```

## Quick Start

### 1. Clone & Setup

```bash
cd /opt
git clone https://github.com/your-repo/odoo-cloud.git
cd odoo-cloud
```

### 2. Configure Environment

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Required variables:
```env
# Platform
BASE_DOMAIN=yourdomain.com
DEBUG=false
CORS_ORIGINS=https://yourdomain.com

# External PostgreSQL (for client databases)
EXTERNAL_DB_HOST=10.0.0.20
EXTERNAL_DB_PORT=5432
EXTERNAL_DB_USER=odoo_clients
EXTERNAL_DB_PASSWORD=strong_password_here

# Security
SECRET_KEY=generate-with-openssl-rand-hex-32

# Paystack
PAYSTACK_SECRET_KEY=sk_live_xxx
PAYSTACK_PUBLIC_KEY=pk_live_xxx
PAYSTACK_WEBHOOK_SECRET=whsec_xxx
```

### 3. Setup External PostgreSQL (VPS #2)

```bash
# On PostgreSQL VPS
sudo apt update
sudo apt install postgresql

sudo -u postgres psql
CREATE USER odoo_clients WITH PASSWORD 'strong_password_here';
ALTER USER odoo_clients CREATEDB;
\q
```

### 4. Install Dependencies

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 5. Start Services

```bash
# Backend (port 8001)
cd backend
source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8001

# Frontend (port 5173)
cd frontend
npm run dev
```

### 6. Default Users

- **Admin**: `admin` / `admin123`
- **Demo**: `demo` / `demo123`

## API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login (returns access + refresh token) |
| `/api/auth/refresh` | POST | Refresh access token |

### Clients

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/clients` | GET | List user's clients |
| `/api/clients` | POST | Create new client |
| `/api/clients/{name}` | GET | Get client details |
| `/api/clients/{name}` | PATCH | Update client |
| `/api/clients/{name}/suspend` | POST | Suspend client |
| `/api/clients/{name}/resume` | POST | Resume client |
| `/api/clients/{name}/schedule-delete` | POST | Schedule deletion (12h) |
| `/api/clients/{name}/cancel-delete` | POST | Cancel scheduled deletion |
| `/api/clients/{name}/force-delete` | POST | Force delete (admin) |
| `/api/clients/{name}/domains` | GET | List custom domains |
| `/api/clients/{name}/domains` | POST | Add custom domain |
| `/api/clients/{name}/domains/{domain}` | DELETE | Remove custom domain |
| `/api/clients/{name}/backup` | POST | Trigger manual backup |
| `/api/clients/{name}/activate` | POST | Activate pending client |

### Payments

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/payments/initialize` | POST | Initialize payment |
| `/api/payments/verify/{ref}` | GET | Verify payment |
| `/api/payments/history` | GET | Payment history |

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/clients/stats` | GET | Platform statistics |
| `/api/system/metrics` | GET | Server metrics (CPU, RAM, disk) |
| `/api/backups` | GET | List all backups |
| `/api/cleanup/expired-clients` | POST | Cleanup unpaid/expired (cron) |

## Payment Flow

```
1. User signs up
2. User creates client → Status: "pending", payment deadline: 24h
3. User selects plan → Initialize Paystack payment
4. User pays → Webhook confirms → Client activated
5. If no payment in 24h → Auto-delete
```

## Soft Delete Flow

```
1. User clicks delete → Status: "scheduled_for_deletion"
2. Client hidden from user's list
3. After 12 hours → Cleanup job deletes:
   - Docker containers/volumes
   - PostgreSQL database/user
   - Nginx config
4. Admin can force-delete anytime
5. Admin can cancel deletion before 12h
```

## Custom Domains

All plans include custom domain support:

1. User adds domain in Client Detail page
2. System creates nginx config for domain
3. SSL certificate auto-provisioned via Let's Encrypt
4. User points DNS to their instance

## Backup System

- **Storage**: S3-compatible (AWS S3, MinIO, Backblaze B2)
- **Schedule**: Daily at 2 AM (configurable)
- **Retention**: 7 daily, 4 weekly, 3 monthly
- **Restore**: Available in client detail page

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_DOMAIN` | `lvh.me` | Platform base domain |
| `DEBUG` | `false` | Debug mode |
| `USE_SQLITE` | `true` | Use SQLite for platform DB |
| `EXTERNAL_DB_HOST` | - | PostgreSQL server IP |
| `EXTERNAL_DB_PORT` | `5432` | PostgreSQL port |
| `ODOO_DATA_DIR` | `clients/` | Client data directory |
| `BACKUP_DIR` | `backups/` | Backup storage |
| `S3_BUCKET` | - | S3 bucket name |
| `PAYSTACK_SECRET_KEY` | - | Paystack secret key |

## Security

- Passwords: Min 8 chars, uppercase, lowercase, number, special char
- JWT: 30-minute access token, 7-day refresh token
- Rate limiting: 5 requests/minute on login
- HTTPS redirect in production
- Admin-only endpoints protected

## Scaling

### Current Capacity (32GB RAM)
- Basic plans: ~9 clients
- Business plans: ~5 clients
- Enterprise plans: ~2-3 clients

### To Scale
1. Add more VPS nodes for clients
2. Use connection pooling (PgBouncer)
3. Implement Redis cluster for caching

## Troubleshooting

### Check Logs
```bash
# Backend logs
tail -f /tmp/backend.log

# Docker logs
docker logs odoo_clientname
```

### Reset Client
```bash
# Force delete
curl -X POST http://localhost:8001/api/clients/{name}/force-delete \
  -H "Authorization: Bearer $TOKEN"
```

### Check Pending Clients
```bash
curl http://localhost:8001/api/clients/pending \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Run Cleanup Manually
```bash
curl -X POST http://localhost:8001/api/cleanup/expired-clients \
  ?admin_token=your_admin_token
```

## Files Structure

```
/home/babatope/Documents/projects/saas/
├── backend/
│   ├── api/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── core/               # Config, DB, Security
│   └── main.py            # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── views/          # Vue pages
│   │   ├── stores/         # Pinia stores
│   │   └── router/         # Vue Router
│   └── vite.config.js
├── infrastructure/
│   ├── docker/             # Docker templates
│   └── nginx/              # Nginx configs
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```
