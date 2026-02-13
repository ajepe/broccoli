# Odoo Cloud Africa - Production Hardening Checklist

## 1. System Security

### SSH Configuration
- [ ] Disable root SSH login
- [ ] Use key-based authentication only
- [ ] Change default SSH port (22)
- [ ] Configure Fail2ban
- [ ] Limit SSH access by IP if possible

### Firewall Configuration
- [ ] Configure UFW firewall
- [ ] Allow SSH (custom port)
- [ ] Allow HTTP (80)
- [ ] Allow HTTPS (443)
- [ ] Allow control panel port (8000)
- [ ] Block all unnecessary ports

## 2. Docker Security

### Docker Configuration
- [ ] Enable Docker Content Trust
- [ ] Configure Docker daemon with limited privileges
- [ ] Use Docker socket isolation for control panel
- [ ] Enable Docker swarm mode for production
- [ ] Configure resource limits for all containers

### Container Security
- [ ] Run containers as non-root users
- [ ] Use read-only root filesystems where possible
- [ ] Implement container security scanning
- [ ] Keep container images updated
- [ ] Use official images only

## 3. Database Security

### PostgreSQL
- [ ] Use strong passwords (generated)
- [ ] Configure pg_hba.conf for local access only
- [ ] Enable SSL connections
- [ ] Regular security updates
- [ ] Separate database per client (implemented)

## 4. Network Security

### SSL/TLS
- [ ] Use Let's Encrypt for SSL certificates
- [ ] Enable HSTS
- [ ] Configure TLS 1.2+ only
- [ ] Use strong ciphers
- [ ] Implement certificate renewal automation

### Nginx
- [ ] Hide Nginx version
- [ ] Enable DDoS protection
- [ ] Configure rate limiting
- [ ] Set up proper proxy headers
- [ ] Enable caching for static content

## 5. Application Security

### Control Panel
- [ ] Enable HTTPS only
- [ ] Implement rate limiting on API
- [ ] Configure CORS properly
- [ ] Use secure session management
- [ ] Implement proper authentication
- [ ] Enable audit logging

### Environment
- [ ] Use environment variables for secrets
- [ ] Never commit secrets to git
- [ ] Rotate secrets regularly
- [ ] Use secret management (HashiCorp Vault)

## 6. Backup & Recovery

### Backup Configuration
- [ ] Daily automated backups
- [ ] Off-site backup storage (S3)
- [ ] Encryption at rest
- [ ] Regular backup testing
- [ ] Document recovery procedures

### Retention Policy
- [ ] 7 daily backups
- [ ] 4 weekly backups
- [ ] 3 monthly backups
- [ ] Automatic cleanup

## 7. Monitoring & Alerts

### Monitoring
- [ ] Resource usage per container
- [ ] Disk space monitoring
- [ ] SSL certificate expiry
- [ ] Service health checks
- [ ] Performance metrics

### Alerts
- [ ] Email notifications for critical issues
- [ ] Slack/Discord webhooks
- [ ] SMS for critical failures
- [ ] Alert escalation procedures

## 8. Access Control

### User Management
- [ ] Principle of least privilege
- [ ] Role-based access control
- [ ] Multi-factor authentication
- [ ] Regular access reviews
- [ ] Audit logging

### API Security
- [ ] API key authentication
- [ ] Rate limiting
- [ ] Request validation
- [ ] Output encoding

## 9. Infrastructure

### Server Hardening
- [ ] Regular OS updates
- [ ] Intrusion detection
- [ ] File integrity monitoring
- [ ] Log aggregation
- [ ] Regular security audits

### Scalability
- [ ] Horizontal scaling ready
- [ ] Load balancer configuration
- [ ] Database replication
- [ ] Session management
- [ ] CDN integration

## 10. Compliance

### Documentation
- [ ] Security policies
- [ ] Incident response plan
- [ ] Change management
- [ ] Backup procedures
- [ ] Contact information

### Regular Reviews
- [ ] Monthly security reviews
- [ ] Quarterly penetration testing
- [ ] Annual compliance audits
- [ ] Vulnerability scanning

## Quick Commands

```bash
# Check open ports
sudo netstat -tulpn

# Check Docker container status
docker ps -a

# Check Fail2ban status
sudo fail2ban-client status

# Check SSL certificate
sudo certbot certificates

# Check disk usage
df -h

# Check memory usage
free -m

# Check CPU load
uptime

# View recent logs
sudo journalctl -n 50

# Check nginx status
sudo systemctl status nginx
```

## Emergency Contacts

| Service | Contact |
|---------|---------|
| Platform Admin | admin@yourdomain.com |
| Security | security@yourdomain.com |
| On-Call | oncall@yourdomain.com |

---

**Last Updated:** 2026-02-13
**Version:** 1.0.0
