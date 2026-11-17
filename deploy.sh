#!/bin/bash
# =============================================================================
# deploy.sh — Script Deployment Otomatis untuk TKDD
# =============================================================================
# Penggunaan:
#   ./deploy.sh            → Pull + Auto-Build jika perlu (atau Restart) + Migrate + Static + Clear Cache + Verifikasi
#   ./deploy.sh --build    → Paksa build image docker baru + recreate containers
#   ./deploy.sh --no-pull  → Deploy tanpa git pull (jalankan migrate + static + restart dari kode saat ini)
#   ./deploy.sh --static   → Hanya jalankan collectstatic + bersihkan cache NPM
#   ./deploy.sh --migrate  → Hanya jalankan migrasi database Django
#   ./deploy.sh --help     → Tampilkan bantuan ini
# =============================================================================

set -euo pipefail

# --- Konfigurasi ---
CONTAINER_WEB="tkdd"
CONTAINER_CELERY="project_celery"
CONTAINER_FLOWER="project_flower"
CONTAINER_NPM="npm"
NPM_CACHE_DIR="/var/lib/nginx/cache/public"
HEALTH_TIMEOUT=120   # detik maksimal menunggu container healthy
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Warna Output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

log()    { echo -e "${GREEN}[✔]${NC} $1"; }
info()   { echo -e "${BLUE}[i]${NC} $1"; }
warn()   { echo -e "${YELLOW}[!]${NC} $1"; }
error()  { echo -e "${RED}[✘]${NC} $1"; }
header() { echo -e "\n${CYAN}========== $1 ==========${NC}"; }

# =============================================================================
# FUNGSI: Tampilkan Bantuan
# =============================================================================
show_help() {
    echo ""
    echo -e "${BOLD}deploy.sh${NC} — Script deployment otomatis untuk TKDD"
    echo ""
    echo "Penggunaan:"
    echo "  ./deploy.sh            Tarik dari git, migrate, collectstatic, restart/build otomatis, clear cache"
    echo "  ./deploy.sh --build    Paksa docker compose build + up -d (image baru)"
    echo "  ./deploy.sh --no-pull  Deploy kode lokal tanpa git pull (migrate + static + restart)"
    echo "  ./deploy.sh --static   Hanya collectstatic + bersihkan cache NPM + reload Nginx"
    echo "  ./deploy.sh --migrate  Hanya jalankan migrasi database Django"
    echo "  ./deploy.sh --help     Tampilkan bantuan ini"
    echo ""
    echo "Otomatisasi:"
    echo "  - Jika requirements.txt, Dockerfile, atau docker-compose.yml berubah saat pull,"
    echo "    script akan OTOMATIS melakukan build image baru tanpa perlu flag --build manual."
    echo ""
}

# =============================================================================
# FUNGSI: Cek status container & dependencies
# =============================================================================
ensure_containers_running() {
    header "Memeriksa Status Container"
    cd "$PROJECT_DIR"

    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_WEB}$"; then
        warn "Container ${CONTAINER_WEB} belum berjalan. Menjalankan docker compose up -d..."
        docker compose up -d
        sleep 5
    else
        log "Container ${CONTAINER_WEB} sedang berjalan."
    fi
}

# =============================================================================
# FUNGSI: Git Pull dari remote
# =============================================================================
AUTO_BUILD_TRIGGERED=false

git_pull() {
    header "Git Pull"
    cd "$PROJECT_DIR"

    local current_branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    info "Branch aktif: ${BOLD}${current_branch}${NC}"

    # Simpan hash sebelum pull
    BEFORE_HASH=$(git rev-parse HEAD)

    # Cek apakah ada uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        warn "Ada perubahan file lokal yang belum di-commit."
        git status -s
    fi

    info "Menarik pembaruan dari origin/${current_branch}..."
    git pull origin "$current_branch"

    AFTER_HASH=$(git rev-parse HEAD)

    if [ "$BEFORE_HASH" = "$AFTER_HASH" ]; then
        info "Kode sudah paling mutakhir (tidak ada commit baru dari remote)."
    else
        log "Pull berhasil: ${BEFORE_HASH:0:7} → ${AFTER_HASH:0:7}"
        
        # Cek apakah ada file infrastruktur yang berubah
        local changed_files
        changed_files=$(git diff --name-only "$BEFORE_HASH" "$AFTER_HASH" 2>/dev/null || echo "")
        if echo "$changed_files" | grep -qE "^(Dockerfile|Dockerfile-flower|requirements\.txt|wait_for_db\.sh|docker-compose\.yml)$"; then
            warn "Terdeteksi perubahan infrastruktur/dependensi:"
            echo "$changed_files" | grep -E "^(Dockerfile|Dockerfile-flower|requirements\.txt|wait_for_db\.sh|docker-compose\.yml)$" | while read -r f; do
                echo -e "    - ${YELLOW}$f${NC}"
            done
            info "Mengaktifkan build image otomatis..."
            AUTO_BUILD_TRIGGERED=true
        fi
    fi
}

# =============================================================================
# FUNGSI: Migrasi Database (Django migrate)
# =============================================================================
run_migrate() {
    header "Migrasi Database (Django migrate)"
    info "Menjalankan python manage.py migrate..."
    docker exec "$CONTAINER_WEB" python manage.py migrate --noinput
    log "Migrasi database selesai."
}

# =============================================================================
# FUNGSI: Kumpulkan File Statis (collectstatic)
# =============================================================================
run_collectstatic() {
    header "Kumpulkan File Statis (collectstatic)"
    info "Menjalankan python manage.py collectstatic di container ${CONTAINER_WEB}..."
    docker exec "$CONTAINER_WEB" python manage.py collectstatic --noinput
    log "Collectstatic selesai."
}

# =============================================================================
# FUNGSI: Bersihkan Cache NPM & Reload Nginx
# =============================================================================
clear_npm_cache() {
    header "Membersihkan Cache Proxy (NPM)"

    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NPM}$"; then
        if docker exec "$CONTAINER_NPM" test -d "$NPM_CACHE_DIR" 2>/dev/null; then
            local count
            count=$(docker exec "$CONTAINER_NPM" sh -c "find $NPM_CACHE_DIR -type f 2>/dev/null | wc -l" || echo "0")
            if [ "$count" -gt 0 ]; then
                docker exec "$CONTAINER_NPM" sh -c "find $NPM_CACHE_DIR -type f -delete 2>/dev/null" || true
                log "File cache NPM dibersihkan (${count} file dihapus)."
            else
                info "Cache disk NPM sudah kosong."
            fi
        fi

        # RELOAD NGINX agar cache di memory RAM (keys_zone) juga ter-reset
        info "Me-reload Nginx Proxy Manager..."
        if docker exec "$CONTAINER_NPM" nginx -s reload 2>/dev/null; then
            log "Nginx Proxy Manager berhasil di-reload."
        else
            warn "Gagal reload Nginx di NPM (mungkin sedang sibuk)."
        fi
    else
        warn "Container ${CONTAINER_NPM} tidak berjalan — cache proxy dilewati."
    fi
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
            log "Container ${container} → running ✔"
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
# FUNGSI: Verifikasi Respon Web
# =============================================================================
verify_web() {
    header "Verifikasi Layanan Web"

    local container_ip
    container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$CONTAINER_WEB" 2>/dev/null | head -1)

    if [ -n "$container_ip" ]; then
        if curl -sf --max-time 10 "http://${container_ip}:80" -o /dev/null 2>/dev/null; then
            log "Layanan web internal merespons HTTP OK di http://${container_ip}:80 ✔"
        fi
    fi

    local domain="tkdd.bkadasahan.dedyn.io"
    local http_code
    http_code=$(curl -sk -o /dev/null -w "%{http_code}" --max-time 10 "https://${domain}/auth/login/" 2>/dev/null || echo "000")

    if [ "$http_code" = "200" ]; then
        log "Layanan publik merespons HTTP ${http_code} di https://${domain}/auth/login/ ✔"
    elif [ "$http_code" = "302" ] || [ "$http_code" = "301" ]; then
        log "Layanan publik merespons redirect ${http_code} di https://${domain} ✔"
    else
        warn "Status respon publik https://${domain}/auth/login/ : HTTP ${http_code}"
    fi
}

# =============================================================================
# FUNGSI: Restart Normal
# =============================================================================
run_restart() {
    header "Restart Container Web & Worker"

    info "Merestart container web: ${CONTAINER_WEB}..."
    docker restart "$CONTAINER_WEB"

    info "Merestart container celery: ${CONTAINER_CELERY}..."
    docker restart "$CONTAINER_CELERY" 2>/dev/null || warn "Container ${CONTAINER_CELERY} tidak ditemukan — dilewati."

    wait_healthy "$CONTAINER_WEB"

    run_migrate
    run_collectstatic
    clear_npm_cache
    verify_web

    log "Deployment selesai dengan sukses! 🚀"
}

# =============================================================================
# FUNGSI: Build Ulang Image Docker
# =============================================================================
run_build() {
    header "Build Image Docker Baru"

    info "Menjalankan docker compose build..."
    docker compose build
    log "Build image Docker selesai."

    header "Recreate Container"
    info "Menjalankan docker compose up -d..."
    docker compose up -d
    log "Container berhasil diperbarui."

    sleep 5
    wait_healthy "$CONTAINER_WEB"

    run_migrate
    run_collectstatic
    clear_npm_cache
    verify_web

    log "Deployment dengan build selesai dengan sukses! 🚀"
}

# =============================================================================
# MAIN ENTRYPOINT
# =============================================================================
main() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║             TKDD DEPLOYMENT AUTOMATION               ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
    echo -e "  Waktu   : $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo -e "  Lokasi  : ${PROJECT_DIR}"
    echo ""

    local mode="${1:-}"

    case "$mode" in
        --help|-h)
            show_help
            exit 0
            ;;
        --static)
            ensure_containers_running
            run_collectstatic
            clear_npm_cache
            verify_web
            log "Pembaruan static selesai!"
            ;;
        --migrate)
            ensure_containers_running
            run_migrate
            log "Migrasi selesai!"
            ;;
        --build)
            ensure_containers_running
            git_pull
            run_build
            ;;
        --no-pull)
            ensure_containers_running
            run_restart
            ;;
        "")
            ensure_containers_running
            git_pull
            if [ "$AUTO_BUILD_TRIGGERED" = true ]; then
                run_build
            else
                run_restart
            fi
            ;;
        *)
            error "Opsi tidak dikenal: ${mode}"
            show_help
            exit 1
            ;;
    esac

    echo ""
    echo -e "${GREEN}Tips:${NC} Tekan ${BOLD}Ctrl + F5${NC} (Hard Refresh) di browser jika perubahan tampilan belum terlihat."
    echo ""
}

main "$@"
