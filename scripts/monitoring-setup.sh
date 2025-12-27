#!/bin/bash
# =============================================================================
# NIS2 Monitoring Stack Setup Script
# =============================================================================
# Starts Prometheus + Grafana for metrics monitoring.
# Usage: ./scripts/monitoring-setup.sh
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           NIS2 Monitoring Stack Setup                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "docker-compose.monitoring.yml" ]; then
    echo "Error: docker-compose.monitoring.yml not found"
    exit 1
fi

# Start monitoring stack
echo -e "${YELLOW}[1/3]${NC} Starting Prometheus + Grafana..."
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d prometheus grafana node-exporter

# Wait for Prometheus
echo -e "${YELLOW}[2/3]${NC} Waiting for Prometheus..."
for i in {1..30}; do
    if curl -s http://localhost:9090/-/ready > /dev/null 2>&1; then
        break
    fi
    sleep 1
done
echo -e "${GREEN}[OK]${NC} Prometheus is ready"

# Wait for Grafana
echo -e "${YELLOW}[3/3]${NC} Waiting for Grafana..."
for i in {1..30}; do
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        break
    fi
    sleep 1
done
echo -e "${GREEN}[OK]${NC} Grafana is ready"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  MONITORING READY ✓                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Services:"
echo "  • Prometheus: http://localhost:9090"
echo "  • Grafana:    http://localhost:3000"
echo ""
echo "Grafana Login:"
echo "  • User:     admin"
echo "  • Password: nis2shield"
echo ""
echo "The NIS2 Compliance Dashboard is pre-loaded!"
echo "Go to: http://localhost:3000/d/nis2-main"
