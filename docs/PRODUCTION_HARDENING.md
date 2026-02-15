# Odoo Cloud Africa - Production Hardening Checklist

## What's New (v2.0)

- External PostgreSQL for client databases
- JWT token refresh
- Soft delete with 12-hour cleanup
- Payment before activation
- Custom domains for all plans

---

## 1. System Security

### SSH Configuration
- [ ] Disable root SSH login
- [ ] Use key-based authentication only
- [ ] Change default SSH port (22)
- [ ] Configure Fail2ban
- [ ] Limit SSH access by IP if possible

### Firewall Configuration
```bash
# UFW Configuration
sudo ufw enable
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp       # HTTP
sudo ufw allow 443/tcp      # HTTPS
sudo ufw allow 8001/tcp     # Control Panel API
sudo ufw enable
```

---

## 2. Environment Configuration

### Required Environment Variables
```bash
# backend/.env - MUST BE CONFIGURED

# Platform
BASE_DOMAIN=yourdomain.com
DEBUG=false
CORS_ORIGINS=https://yourdomain.com

# Security - CRITICAL
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External PostgreSQL (Client Databases)
EXTERNAL_DB_HOST=10.0.0.20
EXTERNAL_DB_PORT=5432
EXTERNAL_DB_USER=odoo_clients
EXTERNAL_DB_PASSWORD=<strong-password>

# Paystack
PAYSTACK_SECRET_KEY=sk_live_xxx
PAYSTACK_PUBLIC_KEY=pk_live_xxx
PAYSTACK_WEBHOOK_SECRET=whsec_xxx

# S3 Backups
S3_BUCKET=odoo-backups
S3_ACCESS_KEY=xxx
S3_SECRET_KEY=xxx
S3_REGION=eu-west-1

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@yourdomain.com
SMTP_PASSWORD=xxx
```

### Production Checklist
- [ ] Generate new SECRET_KEY
- [ ] Configure BASE_DOMAIN
- [ ] Set DEBUG=false
- [ ] Configure CORS_ORIGINS
- [ ] Configure external PostgreSQL
- [ ] Configure Paystack (live keys)
- [ ] Configure S3
- [ ] Configure SMTP

---

## 3. Database Security

### PostgreSQL (External VPS)
```bash
# On PostgreSQL VPS
sudo -u postgres psql

-- Create user with limited permissions
CREATE USER odoo_clients WITH PASSWORD 'strong_password';
ALTER USER odoo_clients CREATEDB;

-- Grant access to template1 for database creation
GRANT ALL PRIVILEGES ON DATABASE template1 TO odoo_clients;

-- Restrict local access
\q
```

- [ ] Use strong passwords (16+ characters)
- [ ] Configure pg_hba.conf for limited access
- [ ] Enable SSL connections
- [ ] Regular security updates
- [ ] Separate database per client (implemented)

---

## 4. Docker Security

### Container Configuration
```yaml
# Security best practices implemented:
- Non-root users in Odoo containers
- Resource limits (CPU, memory)
- Network isolation per client
- Read-only where possible
```

- [ ] Enable Docker Content Trust
- [ ] Configure resource limits for all containers
- [ ] Use official Odoo images only
- [ ] Keep images updated
- [ ] Run containers as non-root users

---

## 5. Network Security

### SSL/TLS
- [ ] Use Let's Encrypt for SSL certificates
- [ ] Enable HSTS
- [ ] Configure TLS 1.2+ only
- [ ] Use strong ciphers
- [ ] Implement certificate renewal automation

### Nginx Security
```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "frame-ancestors 'self'" always;

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

- [ ] Hide Nginx version
- [ ] Enable DDoS protection
- [ ] Configure rate limiting
- [ ] Set up proper proxy headers
- [ ] Enable caching for static content

---

## 6. Application Security

### Authentication
- [x] Password strength validation (8+ chars, uppercase, lowercase, number, special)
- [x] JWT tokens with expiration
- [x] Token refresh mechanism
- [x] Rate limiting on login (5/min)

### Authorization
- [x] Users can only manage own clients
- [x] Admin-only endpoints protected
- [x] Superuser checks on sensitive operations

### API Security
- [x] Request validation with Pydantic
- [x] Proper error handling
- [x] No sensitive data in logs

---

## 7. Payment Security

### Paystack Integration
- [x] Webhook signature verification
- [x] Payment verification before activation
- [x] Reference tracking

### Payment Flow Security
- [x] Client created as "pending" until payment
- [x] 24-hour payment deadline
- [x] Auto-cleanup of unpaid clients

---

## 8. Backup & Recovery

### Backup Configuration
```bash
# Environment variables
S3_BUCKET=odoo-backups
S3_PREFIX=clients/
BACKUP_DIR=/opt/odoo-cloud/backups
```

- [x] Daily automated backups
- [x] Off-site backup storage (S3)
- [x] Encryption at rest
- [ ] Regular backup testing
- [x] Document recovery procedures

### Retention Policy
- [x] 7 daily backups
- [x] 4 weekly backups
- [x] 3 monthly backups
- [x] Automatic cleanup

---

## 9. Monitoring & Alerts

### Implemented Monitoring
- [x] System metrics (CPU, RAM, disk)
- [x] Container stats per client
- [x] Client status tracking
- [x] Payment tracking

### Recommended Alerts
- [ ] Email notifications for critical issues
- [ ] SSL certificate expiry
- [ ] Disk space warnings
- [ ] Failed payment alerts

---

## 10. Access Control

### User Management
- [x] Role-based access (user/admin)
- [x] Principle of least privilege
- [ ] Multi-factor authentication
- [x] Audit logging (activity logs)

### API Security
- [x] Rate limiting
- [x] JWT authentication
- [x] Request validation

---

## 11. Soft Delete & Cleanup

### Implemented Features
- [x] Schedule deletion (12 hours)
- [x] Auto-cleanup of unpaid clients (24 hours)
- [x] Admin force delete
- [x] Cancel deletion before deadline

### Cron Job Setup
```bash
# Add to crontab
0 * * * * curl -X POST http://localhost:8001/api/cleanup/expired-clients?admin_token=YOUR_TOKEN
```

---

## 12. Custom Domains

### Security
- [x] Domain validation (regex)
- [x] SSL auto-provisioning
- [x] Unique domain enforcement

---

## Security Checklist

```bash
# Pre-deployment checklist
[ ] Generate SECRET_KEY
[ ] Configure BASE_DOMAIN
[ ] Set DEBUG=false
[ ] Configure CORS_ORIGINS
[ ] Setup external PostgreSQL
[ ] Configure Paystack live keys
[ ] Configure S3
[ ] Configure SMTP
[ ] Setup SSL certificate
[ ] Configure firewall
[ ] Setup Fail2ban
[ ] Configure backups
[ ] Setup monitoring
[ ] Test payment flow
[ ] Test soft delete
[ ] Review logs
```

---

## Emergency Commands

```bash
# Check running containers
docker ps

# Check container logs
docker logs odoo_clientname

# Force delete client
curl -X POST http://localhost:8001/api/clients/{name}/force-delete \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# View pending clients
curl http://localhost:8001/api/clients/pending \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Run cleanup manually
curl -X POST "http://localhost:8001/api/cleanup/expired-clients?admin_token=TOKEN"

# Check SSL
sudo certbot certificates

# Check disk usage
df -h

# Check memory
free -m
```

---

## Compliance

- [ ] Monthly security reviews
- [ ] Quarterly penetration testing
- [ ] Annual compliance audits
- [ ] Vulnerability scanning
- [ ] Data retention policy
- [ ] GDPR compliance (if needed)

---

**Last Updated:** 2026-02-15
**Version:** 2.0
