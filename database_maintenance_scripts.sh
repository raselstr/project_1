#!/bin/bash

# ======================================================

# PostgreSQL Global Maintenance Script v2

# ======================================================

set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

# ======================================================

# CONFIG

# ======================================================

DB_CONTAINER="postgres"

SECRETS_DIR="./secrets"
BACKUP_DIR="./backups"

DB_NAME_FILE="${SECRETS_DIR}/db_name.txt"
DB_USER_FILE="${SECRETS_DIR}/db_user.txt"
DB_PASSWORD_FILE="${SECRETS_DIR}/db_password.txt"

DATE=$(date +"%Y-%m-%d_%H-%M-%S")

DATA_BACKUP_FILE="${BACKUP_DIR}/backup_data_${DATE}.sql"
FULL_SQL_BACKUP_FILE="${BACKUP_DIR}/full_backup_${DATE}.sql"
FULL_DUMP_BACKUP_FILE="${BACKUP_DIR}/full_backup_${DATE}.dump"

LATEST_SQL_BACKUP="${BACKUP_DIR}/latest_backup.sql"
LATEST_DUMP_BACKUP="${BACKUP_DIR}/latest_backup.dump"

# ======================================================

# LOAD CONFIG

# ======================================================

load_config() {

for file in \
    "$DB_NAME_FILE" \
    "$DB_USER_FILE" \
    "$DB_PASSWORD_FILE"
do
    if [ ! -f "$file" ]; then
        echo "ERROR: File tidak ditemukan:"
        echo "$file"
        exit 1
    fi
done

DB_NAME=$(cat "$DB_NAME_FILE")
DB_USER=$(cat "$DB_USER_FILE")
DB_PASSWORD=$(cat "$DB_PASSWORD_FILE")

}

# ======================================================

# CHECK ENVIRONMENT

# ======================================================

check_requirements() {

echo ""
echo "Checking environment..."

command -v docker >/dev/null 2>&1 || {
    echo "ERROR: Docker tidak ditemukan"
    exit 1
}

mkdir -p "$BACKUP_DIR"

sudo docker ps >/dev/null 2>&1 || {
    echo "ERROR: Docker tidak dapat diakses"
    exit 1
}

sudo docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$" || {
    echo "ERROR: Container ${DB_CONTAINER} tidak berjalan"
    exit 1
}

echo "Environment OK"

}

# ======================================================

# CONFIRM

# ======================================================

confirm_action() {

read -rp "$1 (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Dibatalkan"
    exit 0
fi

}

# ======================================================

# SETUP

# ======================================================

setup_permissions() {

chmod +x "$0"

mkdir -p "$BACKUP_DIR"

chmod 700 "$BACKUP_DIR" 2>/dev/null || true

echo "Permission updated"

}

# ======================================================

# BACKUP DATA ONLY

# ======================================================

backup_data() {

echo ""
echo "Backup DATA ONLY..."

sudo docker exec -t ${DB_CONTAINER} pg_dump \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    --data-only \
    --column-inserts \
    --disable-triggers \
    > "${DATA_BACKUP_FILE}"

cp "${DATA_BACKUP_FILE}" "${LATEST_SQL_BACKUP}"

echo ""
echo "Backup selesai:"
echo "${DATA_BACKUP_FILE}"

}

# ======================================================

# FULL BACKUP SQL

# ======================================================

backup_full_sql() {

echo ""
echo "Full SQL backup..."

sudo docker exec -t ${DB_CONTAINER} pg_dump \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    > "${FULL_SQL_BACKUP_FILE}"

cp "${FULL_SQL_BACKUP_FILE}" "${LATEST_SQL_BACKUP}"

echo ""
echo "Backup selesai:"
echo "${FULL_SQL_BACKUP_FILE}"

}

# ======================================================

# FULL BACKUP CUSTOM

# ======================================================

backup_full_dump() {

echo ""
echo "Full custom backup..."

sudo docker exec ${DB_CONTAINER} pg_dump \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    -Fc \
    > "${FULL_DUMP_BACKUP_FILE}"

cp "${FULL_DUMP_BACKUP_FILE}" "${LATEST_DUMP_BACKUP}"

echo ""
echo "Backup selesai:"
echo "${FULL_DUMP_BACKUP_FILE}"

}

# ======================================================

# RESET DATABASE

# ======================================================

reset_database() {

confirm_action "SEMUA DATA DATABASE AKAN DIHAPUS"

echo ""
echo "Reset database..."

sudo docker exec -i ${DB_CONTAINER} psql \
    -U ${DB_USER} \
    -d ${DB_NAME} <<EOF

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO ${DB_USER};
GRANT ALL ON SCHEMA public TO public;
EOF

echo "Database berhasil dikosongkan"

}

# ======================================================

# RESTORE SQL

# ======================================================

restore_latest_sql() {

[ -f "${LATEST_SQL_BACKUP}" ] || {
    echo "ERROR: ${LATEST_SQL_BACKUP} tidak ditemukan"
    exit 1
}

confirm_action "Restore SQL akan menimpa data"

cat "${LATEST_SQL_BACKUP}" | sudo docker exec -i ${DB_CONTAINER} psql \
    -U ${DB_USER} \
    -d ${DB_NAME}

echo "Restore selesai"

}

# ======================================================

# RESTORE CUSTOM DUMP

# ======================================================

restore_latest_dump() {

[ -f "${LATEST_DUMP_BACKUP}" ] || {
    echo "ERROR: ${LATEST_DUMP_BACKUP} tidak ditemukan"
    exit 1
}

confirm_action "Restore dump akan menimpa data"

cat "${LATEST_DUMP_BACKUP}" | sudo docker exec -i ${DB_CONTAINER} pg_restore \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    --clean \
    --if-exists

echo "Restore selesai"

}

# ======================================================

# RESTORE FILE MANUAL

# ======================================================

restore_file() {

echo ""
echo "File backup tersedia:"
echo ""

ls -lh "${BACKUP_DIR}"

echo ""
read -rp "Masukkan path file backup: " BACKUP_FILE

[ -f "$BACKUP_FILE" ] || {
    echo "ERROR: File tidak ditemukan"
    exit 1
}

confirm_action "Restore database"

cat "$BACKUP_FILE" | sudo docker exec -i ${DB_CONTAINER} psql \
    -U ${DB_USER} \
    -d ${DB_NAME}

echo "Restore selesai"

}

# ======================================================

# LIST BACKUP

# ======================================================

list_backups() {

echo ""
echo "Daftar backup:"
echo ""

ls -lh "${BACKUP_DIR}"

}

# ======================================================

# MENU

# ======================================================

main_menu() {

load_config
check_requirements

echo ""
echo "================================================="
echo " PostgreSQL Global Maintenance v2"
echo "================================================="
echo "1. Setup Permission"
echo "2. Backup Data Only"
echo "3. Full Backup SQL"
echo "4. Full Backup Custom (.dump)"
echo "5. Restore latest SQL"
echo "6. Restore latest Dump"
echo "7. Restore pilih file"
echo "8. Reset Database"
echo "9. List Backup Files"
echo "================================================="

read -rp "Pilih menu (1-9): " pilihan

case $pilihan in
    1) setup_permissions ;;
    2) backup_data ;;
    3) backup_full_sql ;;
    4) backup_full_dump ;;
    5) restore_latest_sql ;;
    6) restore_latest_dump ;;
    7) restore_file ;;
    8) reset_database ;;
    9) list_backups ;;
    *) echo "Pilihan tidak valid" ;;
esac
}

main_menu
