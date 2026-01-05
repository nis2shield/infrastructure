#!/bin/bash
set -e

# NIS2 Shield - Disaster Recovery Quickstart
# Facilitates the setup of the DR Agent by generating valid configuration and certificates.

echo "🛡️  NIS2 Shield - Disaster Recovery Setup"
echo "========================================"

if [ -z "$1" ]; then
    CONFIG_DIR="./dr-config"
else
    CONFIG_DIR="$1"
fi

echo "📂  Configuration directory: $CONFIG_DIR"
mkdir -p "$CONFIG_DIR/certs"

# 1. Gather Information
echo ""
echo "📝  Please provide your environment details:"
read -p "   - Primary Server Port (default 8443): " SERVER_PORT
SERVER_PORT=${SERVER_PORT:-8443}

read -p "   - Primary DB Connection String (PostgreSQL): " DB_SOURCE
read -p "   - Cloudflare API Token: " CF_TOKEN
read -p "   - Cloudflare Zone ID: " CF_ZONE
read -p "   - DNS Record to Failover (e.g., app.example.com): " RECORD_NAME
read -p "   - Backup Server IP (Standby): " BACKUP_IP

# 2. Generate Random Secrets
echo ""
echo "🔑  Generating secure keys..."
AES_KEY=$(openssl rand -hex 32)
echo "   - Generated AES-256 Replication Key"

# 3. Generate Mock Certificates (Self-Signed)
echo "🔐  Generating mTLS certificates..."
openssl req -x509 -newkey rsa:4096 -keyout "$CONFIG_DIR/certs/server.key" -out "$CONFIG_DIR/certs/server.crt" -days 365 -nodes -subj "/CN=nis2-dr-agent" 2>/dev/null
echo "   - Created server.crt and server.key"

# 4. Create Configuration File
CONFIG_FILE="$CONFIG_DIR/dr-agent.yaml"
cat > "$CONFIG_FILE" <<EOF
server:
  port: $SERVER_PORT
  tls_cert: "./certs/server.crt"
  tls_key: "./certs/server.key"

replication:
  source_url: "$DB_SOURCE"
  target_url: "postgres://standby-user:secret@$BACKUP_IP:5432/dbname"
  encryption_key: "$AES_KEY"
  sync_interval: "500ms"

cloud:
  provider: "cloudflare"
  api_token: "$CF_TOKEN"
  zone_id: "$CF_ZONE"

failover:
  enabled: true
  primary_ip: "$(curl -s ifconfig.me)"
  backup_ip: "$BACKUP_IP"
  record_name: "$RECORD_NAME"
  max_failures: 3
  check_interval: "30s"

logging:
  level: "info"
  format: "json"
EOF

echo ""
echo "✅  Setup Complete!"
echo "    1. Configuration saved to: $CONFIG_FILE"
echo "    2. Certificates saved to: $CONFIG_DIR/certs/"
echo ""
echo "🚀  To start the agent:"
echo "    docker run -d -v \$(pwd)/$CONFIG_DIR:/etc/nis2shield -p $SERVER_PORT:$SERVER_PORT nis2shield/dr-agent serve --config /etc/nis2shield/dr-agent.yaml"
echo ""
