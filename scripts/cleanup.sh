#!/bin/bash
# Cron job to clean up expired unpaid clients and scheduled deletions
# Run every hour: 0 * * * * /opt/odoo-cloud/scripts/cleanup.sh

API_URL="http://localhost:8001"
ADMIN_TOKEN="${ADMIN_CLEANUP_TOKEN:-}"

echo "Running cleanup of expired and scheduled deletion clients..."

response=$(curl -s -X POST "${API_URL}/api/cleanup/expired-clients?admin_token=${ADMIN_TOKEN}")

echo "Cleanup result: $response"

# Parse and log the results
deleted=$(echo "$response" | grep -o '"deleted":[0-9]*' | grep -o '[0-9]*')
echo "Cleaned up $deleted clients"
