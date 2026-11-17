#!/bin/bash
# =============================================================================
# deploy_static.sh
# Script untuk sinkronisasi file static (CSS/JS/gambar) ke server.
# Jalankan script ini setelah melakukan perubahan pada file static.
#
# Usage:
#   ./deploy_static.sh              → collectstatic + bersihkan cache NPM + reload Nginx
#   ./deploy_static.sh --full       → collectstatic + restart container + bersihkan cache NPM + reload Nginx
#   ./deploy_static.sh --cache-only → hanya bersihkan cache NPM + reload Nginx
#   ./deploy_static.sh --help       → tampilkan bantuan
# =============================================================================

set -e

# ─── Konfigurasi ──────────────────────────────────────────────────────────────
WEB_CONTAINER="tkdd"
NPM_CONTAINER="npm"
NPM_CACHE_DIR="/var/lib/nginx/cache/public"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# ─────────────────────────────────────────────────────────────────────────────

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

info()    { echo -e "${CYAN}[INFO]${NC}  $1"; }
success() { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ─── Cek container berjalan ───────────────────────────────────────────────────
check_containers() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${WEB_CONTAINER}$"; then
        error "Container '${WEB_CONTAINER}' tidak berjalan. Jalankan: docker compose up -d"
    fi
    if ! docker ps --format '{{.Names}}' | grep -q "^${NPM_CONTAINER}$"; then
        warn "Container NPM '${NPM_CONTAINER}' tidak berjalan. Pembersihan cache proxy dilewati."
        NPM_AVAILABLE=false
    else
        NPM_AVAILABLE=true
    fi
}

# ─── Jalankan collectstatic ───────────────────────────────────────────────────
run_collectstatic() {
    info "Menjalankan collectstatic di container '${WEB_CONTAINER}'..."
    docker exec "${WEB_CONTAINER}" python manage.py collectstatic --noinput
    docker exec "${WEB_CONTAINER}" kill -HUP 1 2>/dev/null || true
    success "collectstatic selesai."
}

# ─── Bersihkan cache NPM & reload Nginx ───────────────────────────────────────
clear_npm_cache() {
    if [ "$NPM_AVAILABLE" = false ]; then
        warn "NPM tidak berjalan, cache tidak dibersihkan."
        return
    fi

    info "Membersihkan cache static NPM (Nginx Proxy Manager)..."
    local COUNT
    COUNT=$(docker exec "${NPM_CONTAINER}" bash -c "find ${NPM_CACHE_DIR} -type f 2>/dev/null | wc -l" || echo "0")

    if [ "$COUNT" -eq 0 ]; then
        info "Cache disk NPM sudah kosong (0 file)."
    else
        docker exec "${NPM_CONTAINER}" bash -c "find ${NPM_CACHE_DIR} -type f -delete 2>/dev/null" || true
        success "Cache disk NPM dibersihkan (${COUNT} file dihapus)."
    fi

    # RELOAD NGINX di NPM untuk me-reset in-memory proxy cache keys
    info "Me-reload Nginx di NPM proxy..."
    if docker exec "${NPM_CONTAINER}" nginx -s reload 2>/dev/null; then
        success "Nginx proxy manager berhasil di-reload."
    else
        warn "Gagal reload Nginx di NPM."
    fi
}

# ─── Restart container web ───────────────────────────────────────────────────
restart_web() {
    info "Merestart container '${WEB_CONTAINER}'..."
    cd "${PROJECT_DIR}"
    docker restart "${WEB_CONTAINER}"
    info "Menunggu container siap..."
    sleep 5
    if docker ps --format '{{.Names}}' | grep -q "^${WEB_CONTAINER}$"; then
        success "Container '${WEB_CONTAINER}' berjalan kembali."
    else
        error "Container gagal restart. Cek: docker logs ${WEB_CONTAINER}"
    fi
}

# ─── Verifikasi akses file static ────────────────────────────────────────────
verify_static() {
    info "Memverifikasi akses file static dari dalam container..."

    local FILES=(
        "static/assets/css/tech_modern.css"
        "static/assets/css/custom.css"
        "static/assets/js/custom.js"
        "static/assets/css/style.css"
        "static/assets/css/components.css"
    )

    local ALL_OK=true
    for FILE in "${FILES[@]}"; do
        local STATUS
        STATUS=$(docker exec "${WEB_CONTAINER}" curl -s -o /dev/null -w "%{http_code}" "http://localhost:80/${FILE}" 2>/dev/null || echo "000")
        if [ "$STATUS" = "200" ]; then
            success "HTTP ${STATUS} → /${FILE}"
        else
            warn "HTTP ${STATUS} → /${FILE}"
            ALL_OK=false
        fi
    done

    if [ "$ALL_OK" = true ]; then
        success "Semua file static utama dapat diakses."
    else
        warn "Beberapa file static belum dapat diakses. Cek: docker logs ${WEB_CONTAINER}"
    fi
}

# ─── Main ─────────────────────────────────────────────────────────────────────
MODE="${1:-}"

case "$MODE" in
    --help|-h)
        echo ""
        echo "Usage: ./deploy_static.sh [OPTION]"
        echo ""
        echo "Options:"
        echo "  (tanpa opsi)    collectstatic + bersihkan cache NPM + reload Nginx"
        echo "  --full          collectstatic + restart container web + bersihkan cache NPM + reload Nginx"
        echo "  --cache-only    Hanya bersihkan cache disk NPM + reload Nginx"
        echo "  --help          Tampilkan bantuan ini"
        echo ""
        exit 0
        ;;
esac

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  Deploy Static - BKAD TKDD${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

check_containers

case "$MODE" in
    --full)
        info "Mode: FULL (collectstatic + restart + bersihkan cache + reload nginx)"
        run_collectstatic
        restart_web
        clear_npm_cache
        verify_static
        ;;
    --cache-only)
        info "Mode: CACHE ONLY (hanya bersihkan cache NPM + reload nginx)"
        clear_npm_cache
        ;;
    *)
        info "Mode: DEFAULT (collectstatic + bersihkan cache + reload nginx)"
        run_collectstatic
        clear_npm_cache
        verify_static
        ;;
esac

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Selesai! File statis sudah diperbarui.${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  Tips: Tekan ${BOLD}Ctrl + F5${NC} (Hard Refresh) di browser"
echo -e "        jika tampilan belum berubah karena cache browser lokal."
echo ""
