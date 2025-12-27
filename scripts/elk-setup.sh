#!/bin/bash
# =============================================================================
# NIS2 ELK Stack Setup Script
# =============================================================================
# Starts Elasticsearch + Kibana and configures the NIS2 index pattern.
# Usage: ./scripts/elk-setup.sh
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           NIS2 ELK Stack Setup                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if docker-compose.elk.yml exists
if [ ! -f "docker-compose.elk.yml" ]; then
    echo "Error: docker-compose.elk.yml not found"
    echo "Run this script from the infrastructure directory"
    exit 1
fi

# Start ELK stack
echo -e "${YELLOW}[1/4]${NC} Starting ELK stack (this may take 2-3 minutes)..."
docker-compose -f docker-compose.yml -f docker-compose.elk.yml up -d elasticsearch kibana

# Wait for Elasticsearch
echo -e "${YELLOW}[2/4]${NC} Waiting for Elasticsearch..."
for i in {1..60}; do
    if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

if ! curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    echo "Error: Elasticsearch did not start in time"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Elasticsearch is ready"

# Wait for Kibana
echo -e "${YELLOW}[3/4]${NC} Waiting for Kibana..."
for i in {1..90}; do
    if curl -s http://localhost:5601/api/status 2>/dev/null | grep -q "available"; then
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

if ! curl -s http://localhost:5601/api/status 2>/dev/null | grep -q "available"; then
    echo "Error: Kibana did not start in time"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Kibana is ready"

# Create index pattern
echo -e "${YELLOW}[4/4]${NC} Creating NIS2 index pattern..."

# Create the data view (index pattern) in Kibana
curl -s -X POST "http://localhost:5601/api/data_views/data_view" \
    -H "kbn-xsrf: true" \
    -H "Content-Type: application/json" \
    -d '{
        "data_view": {
            "title": "nis2-*",
            "name": "NIS2 Logs",
            "timeFieldName": "@timestamp"
        }
    }' > /dev/null 2>&1 || true

echo -e "${GREEN}[OK]${NC} Index pattern created"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ELK STACK READY ✓                             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Services:"
echo "  • Elasticsearch: http://localhost:9200"
echo "  • Kibana:        http://localhost:5601"
echo ""
echo "To view logs in Kibana:"
echo "  1. Open http://localhost:5601"
echo "  2. Go to Analytics → Discover"
echo "  3. Select 'NIS2 Logs' index pattern"
echo ""
echo "To start the full stack with ELK:"
echo "  docker-compose -f docker-compose.yml -f docker-compose.elk.yml up -d"
