import csv
import threading
import uuid
from pathlib import Path
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.db.models import Sum, Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django_tables2 import RequestConfig
from openpyxl import Workbook
from decimal import Decimal

from .forms import RegisterSP2DUploadForm
from .models import RegisterSP2D
from .tables import RegisterSP2DTable
from .utils.importer import import_register_sp2d_excel


# =========================================================
# 🔧 HELPERS
# =========================================================
def _handle_uploaded_file(file):
    upload_dir = Path(settings.MEDIA_ROOT) / "register_sp2d"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.name
    with open(file_path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)
    return file_path


def _apply_pagination(request, table):
    per_page = request.GET.get("per_page", "25")
    if per_page != "all":
        try:
            per_page = int(per_page)
        except ValueError:
            per_page = 25
        RequestConfig(request, paginate={"per_page": per_page}).configure(table)


# =========================================================
# 📥 UPLOAD & LIST
# =========================================================
def upload_register_sp2d(request):
    tahun_session = request.session.get("tahun") or datetime.now().year
    try:
        tahun = int(str(tahun_session).strip())
    except (ValueError, TypeError):
        tahun = datetime.now().year

    form = RegisterSP2DUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if not form.is_valid():
            return JsonResponse({"error": form.errors}, status=400)

        file_path = _handle_uploaded_file(form.cleaned_data["file"])
        task_id = str(uuid.uuid4())
        cache_key = f"register_sp2d_{task_id}"
        cache.set(cache_key, {"current": 0, "total": 1, "done": False}, 3600)

        # Jalankan import di background thread agar tidak bergantung pada celery image
        thread = threading.Thread(
            target=import_register_sp2d_excel,
            args=(str(file_path), tahun, cache_key),
            daemon=True
        )
        thread.start()

        return JsonResponse({"task_id": task_id})

    # --- Bangun queryset dengan filter ---
    q_search = request.GET.get("q", "").strip()
    q_jenis  = request.GET.get("jenis", "").strip()
    q_bulan  = request.GET.get("bulan", "").strip()

    qs = RegisterSP2D.objects.filter(tahun=tahun)

    if q_search:
        qs = qs.filter(
            Q(nomor_sp2d__icontains=q_search) |
            Q(unit_skpd__icontains=q_search)  |
            Q(nama_penerima__icontains=q_search)
        )
    if q_jenis:
        qs = qs.filter(jenis_sp2d=q_jenis)
    if q_bulan:
        qs = qs.filter(bulan=q_bulan)

    qs = qs.order_by("tanggal_pembuatan", "nomor_sp2d")

    # --- Statistik ringkasan ---
    agg = qs.aggregate(
        total_bruto=Sum("nilai_bruto"),
        total_potongan=Sum("nilai_potongan"),
        total_neto=Sum("nilai_neto"),
    )
    total_bruto    = agg["total_bruto"]    or Decimal(0)
    total_potongan = agg["total_potongan"] or Decimal(0)
    total_neto     = agg["total_neto"]     or Decimal(0)

    # --- Jenis SP2D untuk filter ---
    jenis_choices = (
        RegisterSP2D.objects
        .filter(tahun=tahun)
        .exclude(jenis_sp2d__isnull=True)
        .exclude(jenis_sp2d="")
        .values_list("jenis_sp2d", flat=True)
        .distinct()
        .order_by("jenis_sp2d")
    )

    # Bulan pilihan
    BULAN_CHOICES = [
        (1,"Januari"),(2,"Februari"),(3,"Maret"),(4,"April"),
        (5,"Mei"),(6,"Juni"),(7,"Juli"),(8,"Agustus"),
        (9,"September"),(10,"Oktober"),(11,"November"),(12,"Desember"),
    ]

    table = RegisterSP2DTable(qs)
    _apply_pagination(request, table)

    context = {
        "judul"         : "Register SP2D",
        "form"          : form,
        "table"         : table,
        "total_bruto"   : total_bruto,
        "total_potongan": total_potongan,
        "total_neto"    : total_neto,
        "total_items"   : qs.count(),
        "tahun"         : tahun,
        "jenis_choices" : list(jenis_choices),
        "bulan_choices" : BULAN_CHOICES,
        "q_search"      : q_search,
        "q_jenis"       : q_jenis,
        "q_bulan"       : q_bulan,

        # URL untuk template komponen upload
        "url_upload"    : "/master/register-sp2d/",
        "url_progress"  : "/master/register-sp2d/progress/TASK_ID/",
        "url_list"      : "/master/register-sp2d/",
        "url_export"    : "/master/register-sp2d/export/",
        "url_log"       : "/master/register-sp2d/log/",
        "table_template": "components/partials/register_sp2d_table.html",
    }

    if request.htmx:
        return render(request, "components/partials/register_sp2d_table.html", context)

    return render(request, "register_sp2d/upload.html", context)


# =========================================================
# 📊 PROGRESS
# =========================================================
def register_sp2d_progress(request, task_id):
    data = cache.get(f"register_sp2d_{task_id}") or {"current": 0, "total": 1}
    return JsonResponse(data)


# =========================================================
# 📋 LOG RINCIAN UPLOAD (DIPERBAHARUI & DILEWATI)
# =========================================================
def register_sp2d_log_view(request):
    tahun_session = request.session.get("tahun") or datetime.now().year
    try:
        tahun = int(str(tahun_session).strip())
    except (ValueError, TypeError):
        tahun = datetime.now().year

    log_path = Path(settings.MEDIA_ROOT) / "import" / f"register_sp2d_log_{tahun}.csv"

    rows = []
    if log_path.exists():
        with open(log_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [
                {k.strip(): (v.strip() if v else "") for k, v in row.items()}
                for row in reader
            ]

    # Filter status: SEMUA, DIPERBARUI, DILEWATI, BARU
    status_filter = request.GET.get("status", "").strip().upper()
    if status_filter:
        rows = [r for r in rows if r.get("status", "").upper() == status_filter]

    context = {
        "tahun": tahun,
        "rows": rows,
        "total_rows": len(rows),
        "status_filter": status_filter,
    }
    return render(request, "register_sp2d/partials/log_list.html", context)


# =========================================================
# 📤 EXPORT EXCEL
# =========================================================
def export_register_sp2d(request):
    tahun = request.session.get("tahun")
    qs = RegisterSP2D.objects.filter(tahun=tahun).order_by("tanggal_pembuatan", "nomor_sp2d")

    wb = Workbook()
    ws = wb.active
    ws.title = f"Register SP2D {tahun}"

    # Header
    ws.append([
        "No.", "Tgl Pembuatan", "Tgl Pencairan", "Nomor SP2D",
        "Unit SKPD", "Nama Penerima", "Keterangan", "Jenis SP2D",
        "Nilai Bruto", "Potongan", "Nilai Neto",
    ])

    for i, obj in enumerate(qs, 1):
        ws.append([
            i,
            str(obj.tanggal_pembuatan) if obj.tanggal_pembuatan else "",
            str(obj.tanggal_pencairan) if obj.tanggal_pencairan else "",
            obj.nomor_sp2d,
            obj.unit_skpd or "",
            obj.nama_penerima or "",
            obj.keterangan or "",
            obj.jenis_sp2d or "",
            float(obj.nilai_bruto),
            float(obj.nilai_potongan),
            float(obj.nilai_neto),
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="register_sp2d_{tahun}.xlsx"'
    wb.save(response)
    return response
