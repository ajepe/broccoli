#!/bin/bash
# Test script for Odoo Cloud Platform with lvh.me or custom domain
# Usage: ./test-domain.sh [domain]

DOMAIN=${1:-"lvh.me"}
echo "Testing with domain: $DOMAIN"

echo ""
echo "=== Testing lvh.me resolution ==="
ping -c 1 $DOMAIN 2>/dev/null || echo "Note: lvh.me should resolve to 127.0.0.1"

echo ""
echo "=== Update /etc/hosts for custom domain (run with sudo) ==="
echo "127.0.0.1  $DOMAIN"
echo "127.0.0.1  app.$DOMAIN"
echo "127.0.0.1  demo.$DOMAIN"

echo ""
echo "=== Start backend with custom domain ==="
echo "BASE_DOMAIN=$DOMAIN DEBUG=true uvicorn backend.main:app --reload"

echo ""
echo "=== Example client creation ==="
echo "Create client with domain: client.$DOMAIN"

echo ""
echo "=== CORS configuration ==="
echo "Add to CORS_ORIGINS in backend/.env:"
echo "CORS_ORIGINS=http://localhost:5173,http://$DOMAIN,https://$DOMAIN"
