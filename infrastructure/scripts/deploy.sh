#!/bin/bash

set -e

echo "========================================="
echo "  Odoo Cloud Platform - Deployment"
echo "========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="$(dirname "$SCRIPT_DIR")"

echo "[1/8] Updating system packages..."
apt update && apt upgrade -y

echo "[2/8] Installing required packages..."
apt install -y \
    curl \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

echo "[3/8] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | bash
    usermod -aG docker ubuntu
    systemctl enable docker
    systemctl start docker
fi

echo "[4/8] Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

echo "[5/8] Installing Python and dependencies..."
apt install -y python3.11 python3-pip python3-venv python3-dev

echo "[6/8] Creating directories..."
mkdir -p /opt/odoo-clients
mkdir -p /opt/backups
mkdir -p /var/log/odoo
mkdir -p /etc/nginx/ssl

echo "[7/8] Setting up environment..."
cd "$PLATFORM_DIR/backend"
cp env.template .env 2>/dev/null || true

echo "[8/8] Installing Python dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "========================================="
echo "  Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit /home/babatope/Documents/projects/saas/backend/.env with your configuration"
echo "2. Run: cd /home/babatope/Documents/projects/saas/backend && source venv/bin/activate"
echo "3. Run: python -m alembic upgrade head"
echo "4. Run: uvicorn main:app --host 0.0.0.0 --port 8000"
echo "5. Configure Nginx for the control panel"
echo ""
