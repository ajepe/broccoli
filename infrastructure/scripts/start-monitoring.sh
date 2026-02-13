#!/bin/bash

set -e

echo "Starting monitoring stack..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITORING_DIR="$SCRIPT_DIR/../infrastructure/docker/monitoring"

cd "$MONITORING_DIR"

echo "Pulling latest images..."
docker-compose pull

echo "Starting Prometheus, Grafana, and exporters..."
docker-compose up -d

echo ""
echo "Monitoring stack started!"
echo "Grafana: http://localhost:3000"
echo "Prometheus: http://localhost:9090"
echo "Node Exporter: http://localhost:9100"
echo "cAdvisor: http://localhost:8080"
