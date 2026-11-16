#!/bin/bash
# =============================================================================
# deploy.sh — Script deployment otomatis untuk TKDD
# =============================================================================
# Penggunaan:
#   ./deploy.sh           → pull + restart container (perubahan kode Python)
#   ./deploy.sh --build   → pull + build image baru + recreate container
#                           (pakai ini jika requirements.txt atau Dockerfile berubah)
#   ./deploy.sh --static  → collectstatic saja + bersihkan cache NPM
#   ./deploy.sh --help    → tampilkan bantuan ini
# =============================================================================

set -euo pipefail

# --- Konfigurasi ---
CONTAINER_WEB="tkdd"
CONTAINER_CELERY="project_celery"
CONTAINER_FLOWER="project_flower"
CONTAINER_NPM="npm"
NPM_CACHE_DIR="/var/lib/nginx/cache/public"
BRANCH="main"
HEALTH_TIMEOUT=120   # detik maksimal menunggu container healthy
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Warna output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log()    { echo -e "${GREEN}[✔]${NC} $1"; }
info()   { echo -e "${BLUE}[i]${NC} $1"; }
warn()   { echo -e "${YELLOW}[!]${NC} $1"; }
error()  { echo -e "${RED}[✘]${NC} $1"; }
header() { echo -e "\n${CYAN}========== $1 ==========${NC}"; }

# =============================================================================
# FUNGSI: Tampilkan bantuan
# =============================================================================
show_help() {
    echo ""
    echo "  deploy.sh — Script deployment TKDD"
    echo ""
    echo "  Penggunaan:"
    echo "    ./deploy.sh           → pull + restart (perubahan kode Python biasa)"
    echo "    ./deploy.sh --build   → pull + docker build + recreate container"
    echo "    ./deploy.sh --static  → collectstatic + bersihkan cache NPM saja"
    echo "    ./deploy.sh --help    → tampilkan bantuan ini"
    echo ""
    echo "  Kapan pakai --build:"
    echo "    - requirements.txt berubah (ada package baru)"
    echo "    - Dockerfile atau Dockerfile-flower berubah"
    echo "    - Ada perubahan pada entrypoint/script sistem"
    echo ""
}

# =============================================================================
# FUNGSI: Git pull dari remote
# =============================================================================
git_pull() {
    header "Git Pull"
    cd "$PROJECT_DIR"

    local current_branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    info "Branch aktif: ${current_branch}"

    # Simpan hash sebelum pull untuk deteksi perubahan
    BEFORE_HASH=$(git rev-parse HEAD)

    info "Menarik perubahan dari origin/${current_branch}..."
    git pull origin "$current_branch"

    AFTER_HASH=$(git rev-parse HEAD)

    if [ "$BEFORE_HASH" = "$AFTER_HASH" ]; then
        warn "Tidak ada perubahan baru dari remote."
    else
        log "Pull berhasil: ${BEFORE_HASH:0:7} → ${AFTER_HASH:0:7}"
    fi
}

# =============================================================================
# FUNGSI: Periksa apakah Dockerfile/requirements berubah (peringatkan user)
# =============================================================================
check_build_needed() {
    header "Memeriksa Kebutuhan Build"

    local changed_files
    changed_files=$(git diff --name-only "$BEFORE_HASH" "$AFTER_HASH" 2>/dev/null || echo "")

    local need_build=0

    if echo "$changed_files" | grep -qE "^(Dockerfile|Dockerfile-flower|requirements\.txt|wait_for_db\.sh)$"; then
        warn "File berikut berubah dan mungkin membutuhkan --build:"
        echo "$changed_files" | grep -E "^(Dockerfile|Dockerfile-flower|requirements\.txt|wait_for_db\.sh)$" | while read -r f; do
            warn "  - $f"
        done
        warn "Jalankan: ./deploy.sh --build"
        warn "Melanjutkan dengan restart biasa (tanpa build)..."
        need_build=1
    else
        log "Tidak ada perubahan pada Dockerfile/requirements. Build tidak diperlukan."
    fi

    return $need_build 2>/dev/null || true
}

# =============================================================================
# FUNGSI: Tunggu container menjadi healthy/running
# =============================================================================
wait_healthy() {
    local container="$1"
    local timeout="$HEALTH_TIMEOUT"
    local elapsed=0

    info "Menunggu container ${container} siap..."

    while [ $elapsed -lt $timeout ]; do
        local status
        status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
        local health
        health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no_healthcheck{{end}}' "$container" 2>/dev/null || echo "unknown")

        if [ "$status" = "running" ] && [ "$health" = "healthy" ]; then
            log "Container ${container} → healthy ✔"
            return 0
        elif [ "$status" = "running" ] && [ "$health" = "no_healthcheck" ]; then
            log "Container ${container} → running (no healthcheck) ✔"
            return 0
        elif [ "$status" = "exited" ] || [ "$status" = "dead" ]; then
            error "Container ${container} berhenti! Status: ${status}"
            docker logs "$container" --tail 20
            return 1
        fi

        sleep 3
        elapsed=$((elapsed + 3))
        printf "."
    done

    echo ""
    error "Timeout ${timeout}s menunggu ${container}. Status terakhir: ${status}"
    return 1
}

# =============================================================================
# FUNGSI: Bersihkan cache NPM (Nginx Proxy Manager)
# =============================================================================
clear_npm_cache() {
    header "Membersihkan Cache NPM"

    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NPM}$"; then
        if docker exec "$CONTAINER_NPM" test -d "$NPM_CACHE_DIR" 2>/dev/null; then
            local cache_size
            cache_size=$(docker exec "$CONTAINER_NPM" du -sh "$NPM_CACHE_DIR" 2>/dev/null | cut -f1 || echo "?")
            info "Ukuran cache: ${cache_size}"
            docker exec "$CONTAINER_NPM" find "$NPM_CACHE_DIR" -type f -delete 2>/dev/null || true
            log "Cache NPM dibersihkan."
        else
            info "Direktori cache NPM tidak ditemukan — dilewati."
        fi
    else
        warn "Container NPM tidak berjalan — cache tidak dibersihkan."
    fi
}

# =============================================================================
# FUNGSI: Verifikasi HTTP response web
# =============================================================================
verify_web() {
    header "Verifikasi Web"

    local url
    url=$(docker exec "$CONTAINER_WEB" sh -c 'echo ${ALLOWED_HOSTS:-localhost}' 2>/dev/null | tr ',' '\n' | grep "\." | head -1 || echo "")

    if [ -z "$url" ]; then
        # Coba langsung ke container
        local container_ip
        container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$CONTAINER_WEB" 2>/dev/null | head -1)
        if curl -sf --max-time 10 "http://${container_ip}:80" -o /dev/null; then
            log "Web merespons HTTP 200 di ${container_ip}:80 ✔"
        else
            warn "Web tidak merespons di ${container_ip}:80 — periksa logs: docker logs ${CONTAINER_WEB} --tail 30"
        fi
    else
        if curl -sf --max-time 10 "https://${url}/auth/login/" -o /dev/null 2>/dev/null || \
           curl -skf --max-time 10 "https://${url}/auth/login/" -o /dev/null 2>/dev/null; then
            log "Web merespons di https://${url}/auth/login/ ✔"
        else
            warn "Tidak bisa verifikasi https://${url} — cek manual atau DNS belum propagasi."
        fi
    fi
}

# =============================================================================
# FUNGSI: Collectstatic saja
# =============================================================================
run_static_only() {
    header "Collectstatic"
    info "Menjalankan collectstatic di dalam container ${CONTAINER_WEB}..."
    docker exec "$CONTAINER_WEB" python manage.py collectstatic --noinput
    log "Collectstatic selesai."
    clear_npm_cache
    log "Selesai. Cache static diperbarui."
}

# =============================================================================
# FUNGSI: Restart container (tanpa build ulang)
# =============================================================================
run_restart() {
    header "Restart Container"

    info "Merestart container web: ${CONTAINER_WEB}..."
    docker restart "$CONTAINER_WEB"

    info "Merestart container celery: ${CONTAINER_CELERY}..."
    docker restart "$CONTAINER_CELERY" 2>/dev/null || warn "Container ${CONTAINER_CELERY} tidak ditemukan — dilewati."

    wait_healthy "$CONTAINER_WEB"

    clear_npm_cache
    verify_web

    log "Deploy selesai! 🚀"
}

# =============================================================================
# FUNGSI: Build ulang + recreate container (pakai --build)
# =============================================================================
run_build() {
    header "Build Image Docker"

    info "Menjalankan docker compose build..."
    docker compose build
    log "Build image selesai."

    header "Recreate Container"
    info "Menjalankan docker compose up -d (recreate container dengan image baru)..."
    docker compose up -d
    log "Container direcreate."

    sleep 5  # Beri waktu container mulai

    wait_healthy "$CONTAINER_WEB"

    clear_npm_cache
    verify_web

    log "Deploy dengan build selesai! 🚀"
}

# =============================================================================
# MAIN
# =============================================================================
main() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║      TKDD Deployment Script          ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════╝${NC}"
    echo -e "  Waktu: $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo -e "  Dir  : ${PROJECT_DIR}"
    echo ""

    local mode="${1:-}"

    case "$mode" in
        --help|-h)
            show_help
            exit 0
            ;;
        --static)
            run_static_only
            ;;
        --build)
            git_pull
            run_build
            ;;
        "")
            git_pull
            check_build_needed || true
            run_restart
            ;;
        *)
            error "Opsi tidak dikenal: ${mode}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
