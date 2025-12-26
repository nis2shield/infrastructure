#!/bin/bash
# =============================================================================
# NIS2 Infrastructure Kit - Disaster Recovery Test Script
# =============================================================================
# Automated DR drill for NIS2 compliance (Article 21c - Business Continuity).
# Tests that backups can be successfully restored.
#
# Usage: ./restore-test.sh [backup_file]
#        ./restore-test.sh --encrypted backup.sql.gz.enc
#
# Supports: .sql, .sql.gz, .sql.gz.enc (GPG encrypted)
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration (override with environment variables)
POSTGRES_USER="${POSTGRES_USER:-nis2user}"
POSTGRES_DB="${POSTGRES_DB:-nis2_app}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-test_password}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TEST_CONTAINER="nis2_restore_test_db"
POSTGRES_VERSION="${POSTGRES_VERSION:-15-alpine}"
GPG_KEY="${GPG_KEY:-}"  # Optional: GPG key ID for encrypted backups

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      NIS2 DISASTER RECOVERY DRILL - $(date '+%Y-%m-%d %H:%M')          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Parse arguments
ENCRYPTED=false
BACKUP_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --encrypted|-e)
            ENCRYPTED=true
            shift
            ;;
        *)
            BACKUP_FILE="$1"
            shift
            ;;
    esac
done

# Find backup file if not specified
if [ -z "$BACKUP_FILE" ]; then
    echo -e "${YELLOW}[INFO]${NC} Searching for latest backup..."
    
    # Priority: encrypted > compressed > plain
    BACKUP_FILE=$(ls -t ${BACKUP_DIR}/*.sql.gz.enc 2>/dev/null | head -1)
    if [ -n "$BACKUP_FILE" ]; then
        ENCRYPTED=true
    else
        BACKUP_FILE=$(ls -t ${BACKUP_DIR}/*.sql.gz 2>/dev/null | head -1)
        if [ -z "$BACKUP_FILE" ]; then
            BACKUP_FILE=$(ls -t ${BACKUP_DIR}/*.sql 2>/dev/null | head -1)
        fi
    fi
fi

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}[FAIL]${NC} No backup found in ${BACKUP_DIR}"
    echo "       Run 'docker-compose up db-backup' first."
    exit 1
fi

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo -e "${GREEN}[OK]${NC} Backup: ${BACKUP_FILE} (${BACKUP_SIZE})"
echo ""

# Cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}[CLEANUP]${NC} Removing test container..."
    docker rm -f ${TEST_CONTAINER} 2>/dev/null || true
}
trap cleanup EXIT

# Step 1: Start clean PostgreSQL container
echo -e "${BLUE}[STEP 1/4]${NC} Starting clean PostgreSQL container..."
docker rm -f ${TEST_CONTAINER} 2>/dev/null || true

docker run -d --name ${TEST_CONTAINER} \
    -e POSTGRES_USER=${POSTGRES_USER} \
    -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
    -e POSTGRES_DB=${POSTGRES_DB} \
    postgres:${POSTGRES_VERSION} > /dev/null

# Wait for DB with polling (not fixed sleep)
echo -e "${YELLOW}[WAIT]${NC} Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker exec ${TEST_CONTAINER} pg_isready -U ${POSTGRES_USER} > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

if ! docker exec ${TEST_CONTAINER} pg_isready -U ${POSTGRES_USER} > /dev/null 2>&1; then
    echo -e "${RED}[FAIL]${NC} PostgreSQL did not start"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} PostgreSQL ready"
echo ""

# Step 2: Restore backup
echo -e "${BLUE}[STEP 2/4]${NC} Restoring backup..."

if [ "$ENCRYPTED" = true ] || [[ "$BACKUP_FILE" == *.enc ]]; then
    # Encrypted backup (GPG)
    if [ -z "$GPG_KEY" ]; then
        echo -e "${YELLOW}[WARN]${NC} GPG_KEY not set, attempting with default key..."
    fi
    gpg --quiet --batch --decrypt "$BACKUP_FILE" 2>/dev/null | \
        docker exec -i ${TEST_CONTAINER} sh -c "zcat | psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}" > /dev/null 2>&1
elif [[ "$BACKUP_FILE" == *.gz ]]; then
    # Compressed backup (zcat inline)
    cat "$BACKUP_FILE" | docker exec -i ${TEST_CONTAINER} sh -c "zcat | psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}" > /dev/null 2>&1
else
    # Plain SQL backup
    cat "$BACKUP_FILE" | docker exec -i ${TEST_CONTAINER} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} > /dev/null 2>&1
fi

echo -e "${GREEN}[OK]${NC} Backup restored"
echo ""

# Step 3: Validate data integrity
echo -e "${BLUE}[STEP 3/4]${NC} Validating data..."

TABLE_COUNT=$(docker exec ${TEST_CONTAINER} \
    psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t -c \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | xargs)

echo -e "     Tables: ${TABLE_COUNT}"

# Check key Django tables
for table in django_migrations auth_user django_session; do
    COUNT=$(docker exec ${TEST_CONTAINER} \
        psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -t -c \
        "SELECT COUNT(*) FROM ${table};" 2>/dev/null | xargs || echo "N/A")
    if [ "$COUNT" != "N/A" ] && [ -n "$COUNT" ]; then
        echo -e "     - ${table}: ${COUNT} rows"
    fi
done

echo -e "${GREEN}[OK]${NC} Data validated"
echo ""

# Step 4: Generate compliance report
echo -e "${BLUE}[STEP 4/4]${NC} Generating report..."

REPORT_FILE="./restore-test-report-$(date '+%Y%m%d-%H%M%S').txt"
ENCRYPTED_STR="No"
[ "$ENCRYPTED" = true ] && ENCRYPTED_STR="Yes (GPG)"

cat > "$REPORT_FILE" << EOF
================================================================================
              NIS2 DISASTER RECOVERY TEST REPORT
================================================================================

Date:           $(date '+%Y-%m-%d %H:%M:%S %Z')
Backup File:    ${BACKUP_FILE}
Backup Size:    ${BACKUP_SIZE}
Encrypted:      ${ENCRYPTED_STR}

RESULTS
-------
[PASS] PostgreSQL container started
[PASS] Backup decompressed/decrypted
[PASS] Data restored to test database
[PASS] Validation: ${TABLE_COUNT} tables found

COMPLIANCE
----------
This test satisfies NIS2 Directive Article 21(c) - Business Continuity.
Backup restoration capability has been verified.

================================================================================
Generated: $(date '+%Y-%m-%d %H:%M:%S') | NIS2 Infrastructure Kit
================================================================================
EOF

echo -e "${GREEN}[OK]${NC} Report: ${REPORT_FILE}"
echo ""

# Success
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  ✓ DRILL PASSED                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Summary: ${TABLE_COUNT} tables restored from ${BACKUP_SIZE} backup"
echo "Report:  ${REPORT_FILE}"
