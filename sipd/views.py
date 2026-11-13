# views.py
import csv
import threading
import uuid
from pathlib import Path
from datetime import date, datetime
import re
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, Min
from django.core.exceptions import ValidationError

from django_tables2 import RequestConfig
from openpyxl import Workbook

from collections import defaultdict
from decimal import Decimal
from itertools import chain

from project.decorators import menu_access_required, set_submenu_session
from core.helpers.filter_helper import FilterHelper

from sipd.registry import (
    SIPD_REGISTRY,
    get_rencana_by_pk,
    get_sp2d_sudah_realisasi_global
)

from .models import Sipd, TBP
from pendidikan.models import Realisasi
from .forms import SipdUploadForm, TBPUploadForm
from .tables import SipdTable, TBPTable
from .filters import SipdFilter
from .tasks import import_sipd_task, import_tbp_task
from .utils.importer import import_sipd_excel
from .utils.importer_tbp import import_tbp_excel


# =========================================================
# 🔧 GENERIC HELPERS
# =========================================================
def handle_uploaded_file(file, folder):
    upload_dir = Path(settings.MEDIA_ROOT) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.name
    with open(file_path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)

    return file_path


def apply_pagination(request, table):
    per_page = request.GET.get("per_page", "10")
    if per_page != "all":
        RequestConfig(request, paginate={"per_page": int(per_page)}).configure(table)


def import_progress(request, task_id, prefix):
    data = cache.get(f"{prefix}_{task_id}") or {"current": 0, "total": 1}
    return JsonResponse(data)


def skipped_view(request, tahun, prefix):
    path = Path(settings.MEDIA_ROOT) / "import" / f"{prefix}_skipped_{tahun}.csv"

    rows = []
    if path.exists():
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [{k.strip(): (v.strip() if v else "") for k, v in row.items()} for row in reader]

    return render(request, "components/skipped_list.html", {
        "tahun": tahun,
        "rows": rows,
    })


# =========================================================
# 📥 UPLOAD SIPD
# =========================================================
def upload_sipd(request):
    clean_tahun = str(request.session.get("tahun") or "2026").replace(".", "").replace(",", "").strip()
    try:
        tahun = int(clean_tahun)
    except (TypeError, ValueError):
        tahun = 2026

    form = SipdUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if not form.is_valid():
            return JsonResponse({"error": form.errors}, status=400)

        file_path = handle_uploaded_file(form.cleaned_data["file"], "sipd")
        task_id = str(uuid.uuid4())
        cache_key = f"sipd_{task_id}"
        cache.set(cache_key, {"current": 0, "total": 1, "done": False}, 3600)

        # Jalankan via threading agar independen dari image celery
        thread = threading.Thread(
            target=import_sipd_excel,
            args=(str(file_path), tahun, cache_key),
            daemon=True
        )
        thread.start()

        return JsonResponse({"task_id": task_id})

    qs = Sipd.objects.filter(tahun=tahun)

    # --- Ringkasan Statistik ---
    stats = qs.aggregate(total_realisasi=Sum("nilai_realisasi"))
    total_items = qs.count()
    total_realisasi = stats["total_realisasi"] or Decimal(0)
    total_sp2d = qs.exclude(nomor_sp2d="").values("nomor_sp2d").distinct().count()
    total_skpd = qs.exclude(nama_sub_skpd="").values("nama_sub_skpd").distinct().count()

    # --- Filter & Search ---
    q_search = request.GET.get("q", "").strip()
    if q_search:
        qs = qs.filter(
            Q(nama_sub_skpd__icontains=q_search) |
            Q(kode_sub_kegiatan__icontains=q_search) |
            Q(nama_sub_kegiatan__icontains=q_search) |
            Q(nomor_sp2d__icontains=q_search) |
            Q(nomor_dokumen__icontains=q_search) |
            Q(kode_rekening__icontains=q_search) |
            Q(nama_rekening__icontains=q_search)
        )

    table = SipdTable(qs.order_by("-tanggal_sp2d", "kode_sub_kegiatan"))
    apply_pagination(request, table)

    context = {
        "form": form,
        "table": table,
        "judul": "Data SIPD",
        "tahun": str(tahun),
        "q_search": q_search,
        "total_items": total_items,
        "total_realisasi": total_realisasi,
        "total_sp2d": total_sp2d,
        "total_skpd": total_skpd,
        "url_list": "/sipd/",
        "url_upload": "/sipd/",
        "url_progress": "/sipd/progress/TASK_ID/",
        "url_export": "/sipd/export/",
    }

    template = "sipd/partials/table_sipd.html" if request.htmx else "sipd/upload_sipd.html"
    return render(request, template, context)


def sipd_import_progress(request, task_id):
    return import_progress(request, task_id, "sipd")


def sipd_log_view(request):
    clean_tahun = str(request.session.get("tahun") or "2026").replace(".", "").replace(",", "").strip()
    log_path = Path(settings.MEDIA_ROOT) / "import" / f"sipd_log_{clean_tahun}.csv"
    rows = []
    if log_path.exists():
        try:
            with open(log_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    rows.append(r)
        except Exception:
            pass

    rows = rows[::-1][:200]
    return render(request, "sipd/partials/sipd_log_list.html", {
        "rows": rows,
        "tahun": str(clean_tahun),
    })


def skipped_sipd_view(request, tahun):
    return skipped_view(request, tahun, "sipd")


def export_sipd_excel(request):
    clean_tahun = str(request.session.get("tahun") or "2026").replace(".", "").replace(",", "").strip()
    try:
        tahun = int(clean_tahun)
    except (TypeError, ValueError):
        tahun = 2026

    qs = Sipd.objects.filter(tahun=tahun)

    q_search = request.GET.get("q", "").strip()
    if q_search:
        qs = qs.filter(
            Q(nama_sub_skpd__icontains=q_search) |
            Q(kode_sub_kegiatan__icontains=q_search) |
            Q(nama_sub_kegiatan__icontains=q_search) |
            Q(nomor_sp2d__icontains=q_search) |
            Q(nomor_dokumen__icontains=q_search)
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Data SIPD"

    headers = [
        "Tahun", "Nama Sub SKPD", "Kode Sub Kegiatan", "Nama Sub Kegiatan",
        "Kode Rekening", "Nama Rekening", "Nomor Dokumen", "Nomor SP2D",
        "Tanggal SP2D", "Nilai Realisasi"
    ]
    ws.append(headers)

    for row in qs.values_list(
        "tahun", "nama_sub_skpd", "kode_sub_kegiatan", "nama_sub_kegiatan",
        "kode_rekening", "nama_rekening", "nomor_dokumen", "nomor_sp2d",
        "tanggal_sp2d", "nilai_realisasi"
    ):
        ws.append(row)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="sipd_{tahun}.xlsx"'

    wb.save(response)
    return response


# =========================================================
# 📥 UPLOAD TBP
# =========================================================
def upload_tbp(request):
    clean_tahun = str(request.session.get("tahun") or "2026").replace(".", "").replace(",", "").strip()
    try:
        tahun = int(clean_tahun)
    except (TypeError, ValueError):
        tahun = 2026

    form = TBPUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if not form.is_valid():
            return JsonResponse({"error": form.errors}, status=400)

        file_path = handle_uploaded_file(form.cleaned_data["file"], "tbp")
        task_id = str(uuid.uuid4())
        cache_key = f"tbp_{task_id}"
        cache.set(cache_key, {"current": 0, "total": 1, "done": False}, 3600)

        # Jalankan via threading agar independen dari image celery
        thread = threading.Thread(
            target=import_tbp_excel,
            args=(str(file_path), tahun, cache_key),
            daemon=True
        )
        thread.start()

        return JsonResponse({"task_id": task_id})

    qs = TBP.objects.filter(tahun=tahun)

    # --- Ringkasan Statistik ---
    stats = qs.aggregate(total_nilai=Sum("nilai_tbp"))
    total_items = qs.count()
    total_nilai_tbp = stats["total_nilai"] or Decimal(0)
    total_tbp_unik = qs.exclude(nomor_tbp="").values("nomor_tbp").distinct().count()
    latest_tbp = qs.order_by("-tanggal_tbp").first()
    tbp_terakhir = latest_tbp.tanggal_tbp.strftime("%d-%m-%Y") if (latest_tbp and latest_tbp.tanggal_tbp) else "-"

    # --- Filter & Search ---
    q_search = request.GET.get("q", "").strip()
    if q_search:
        qs = qs.filter(
            Q(nomor_tbp__icontains=q_search) |
            Q(keterangan_tbp__icontains=q_search) |
            Q(status_tbp__icontains=q_search)
        )

    table = TBPTable(qs.order_by("-tanggal_tbp", "-id"))
    apply_pagination(request, table)

    context = {
        "form": form,
        "table": table,
        "judul": "Data TBP",
        "tahun": str(tahun),
        "q_search": q_search,
        "total_items": total_items,
        "total_nilai_tbp": total_nilai_tbp,
        "total_tbp_unik": total_tbp_unik,
        "tbp_terakhir": tbp_terakhir,
        "url_list": "/sipd/tbp/",
        "url_upload": "/sipd/tbp/",
        "url_progress": "/sipd/tbp/progress/TASK_ID/",
        "url_export": "/sipd/tbp/export/",
    }

    template = "sipd/partials/table_tbp.html" if request.htmx else "sipd/upload_tbp.html"
    return render(request, template, context)


def tbp_import_progress(request, task_id):
    return import_progress(request, task_id, "tbp")


def tbp_log_view(request):
    clean_tahun = str(request.session.get("tahun") or "2026").replace(".", "").replace(",", "").strip()
    log_path = Path(settings.MEDIA_ROOT) / "import" / f"tbp_log_{clean_tahun}.csv"
    rows = []
    if log_path.exists():
        try:
            with open(log_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    rows.append(r)
        except Exception:
            pass

    rows = rows[::-1][:200]
    return render(request, "sipd/partials/tbp_log_list.html", {
        "rows": rows,
        "tahun": str(clean_tahun),
    })


def export_tbp_excel(request):
    clean_tahun = str(request.session.get("tahun") or "2026").replace(".", "").replace(",", "").strip()
    try:
        tahun = int(clean_tahun)
    except (TypeError, ValueError):
        tahun = 2026

    qs = TBP.objects.filter(tahun=tahun).order_by("-tanggal_tbp")

    q_search = request.GET.get("q", "").strip()
    if q_search:
        qs = qs.filter(
            Q(nomor_tbp__icontains=q_search) |
            Q(keterangan_tbp__icontains=q_search) |
            Q(status_tbp__icontains=q_search)
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Data TBP"

    ws.append(["Tahun", "Tanggal TBP", "Nomor TBP", "Keterangan", "Status TBP", "Nilai TBP"])

    for row in qs.values_list("tahun", "tanggal_tbp", "nomor_tbp", "keterangan_tbp", "status_tbp", "nilai_tbp"):
        ws.append(row)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="tbp_{tahun}.xlsx"'

    wb.save(response)
    return response

# ================= HELPER =================
def clean(value):
    return str(value).strip() if value else ""


def extract_nomor_dari_status(status):
    """
    Ambil nomor setelah 'nomor:' dari teks seperti:
    - Telah Terbit SP2D nomor: xxx
    - Telah Terbit LPJ BP nomor: xxx
    """
    if not status:
        return ""

    match = re.search(r"nomor\s*:\s*([0-9./A-Z\-]+)", status, re.IGNORECASE)
    return clean(match.group(1)) if match else ""


def modal_output(request):
    key = request.POST.get('key') or request.GET.get('key')

    if key not in SIPD_REGISTRY:
        return HttpResponse("<div class='alert alert-danger'>Key tidak valid</div>")

    config = SIPD_REGISTRY[key]
    model_realisasi = config['model_realisasi']

    if request.method == "POST":
        try:
            pk = int(request.POST.get('id'))
        except (TypeError, ValueError):
            return HttpResponse("<div class='alert alert-danger'>ID tidak valid</div>")

        output = request.POST.get('realisasi_output')

        obj = get_object_or_404(model_realisasi, pk=pk)
        obj.realisasi_output = output

        try:
            obj.save()
        except Exception as e:
            return HttpResponse(f"<div class='alert alert-danger'>{e}</div>")

        return HttpResponse("""
            <script>
                location.reload();
            </script>
        """)

    # GET (load modal)
    pk = request.GET.get('id')
    obj = model_realisasi.objects.filter(pk=pk).first()

    return render(request, 'components/modal_output.html', {
        'obj': obj,
        'id': pk,
        'key': key,  # penting untuk dikirim balik ke POST
        
    })
    
    
# ================= VIEW =================
@set_submenu_session
@menu_access_required('list')
def view_sipd(request, mode, pk):
    request.session['next'] = request.get_full_path()

    config = SIPD_REGISTRY.get(mode)
    if not config:
        return HttpResponseBadRequest('Mode SIPD tidak valid')

    model_rencana = config['model_rencana']
    model_rencana_sisa = config['model_rencana_sisa']
    model_realisasi = config['model_realisasi']
    model_realisasi_sisa = config.get('model_realisasi_sisa')
    url_sp2d = config['url_sp2d']

    rencana = get_rencana_by_pk(pk, model_rencana, model_rencana_sisa)

    if not rencana:
        messages.error(request, 'Data rencana tidak ditemukan')
        return redirect('url_list_rencana')

    # ================= FILTER SIPD =================
    base_filter = Q(
        tahun=rencana.posting_tahun,
        kode_sub_kegiatan=rencana.posting_ket,
        kode_sub_skpd=rencana.posting_subopd.sub_opd_kode
    )

    sipd_qs_raw = Sipd.objects.filter(base_filter)

    # ================= TBP MAP =================
    tbp_map = {}

    tbp_docs = sipd_qs_raw.filter(
        jenis_dokumen="TBP"
    ).values_list("nomor_dokumen", flat=True)

    tbp_qs = TBP.objects.filter(
        tahun=rencana.posting_tahun,
        nomor_tbp__in=tbp_docs
    )

    for tbp in tbp_qs:
        nomor = extract_nomor_dari_status(tbp.status_tbp)

        if nomor:
            tbp_map[clean(tbp.nomor_tbp)] = nomor

    # ================= DATA SUDAH REALISASI =================
    sp2d_done = get_sp2d_sudah_realisasi_global(
        rencana,
        model_rencana,
        model_realisasi,
        model_rencana_sisa,
        model_realisasi_sisa,
    )

    # ================= AGREGASI SIPD =================
    sipd_qs = (
        sipd_qs_raw
        .values('nomor_sp2d', 'nomor_dokumen', 'jenis_dokumen')
        .annotate(
            tanggal_sp2d=Min('tanggal_sp2d'),
            nilai_realisasi=Sum('nilai_realisasi'),
        )
        .order_by('tanggal_sp2d', 'nomor_sp2d')
    )

    # ================= GROUP FINAL =================
    grouped_sp2d = {}

    for row in sipd_qs:

        # 🔥 tentukan nomor final
        if row["jenis_dokumen"] == "TBP":
            nomor_sp2d_final = tbp_map.get(clean(row["nomor_dokumen"]), "")
        else:
            nomor_sp2d_final = clean(row["nomor_sp2d"])

        if not nomor_sp2d_final:
            continue

        # skip jika sudah direalisasi
        if nomor_sp2d_final in sp2d_done:
            continue

        # ================= GROUP =================
        if nomor_sp2d_final not in grouped_sp2d:
            grouped_sp2d[nomor_sp2d_final] = {
                "nomor_sp2d_final": nomor_sp2d_final,
                "tanggal_sp2d": row["tanggal_sp2d"],
                "nilai_realisasi": Decimal(0),
            }

        grouped_sp2d[nomor_sp2d_final]["nilai_realisasi"] += (
            row["nilai_realisasi"] or Decimal(0)
        )

        # ambil tanggal paling awal
        if row["tanggal_sp2d"]:
            existing = grouped_sp2d[nomor_sp2d_final]["tanggal_sp2d"]
            if not existing or row["tanggal_sp2d"] < existing:
                grouped_sp2d[nomor_sp2d_final]["tanggal_sp2d"] = row["tanggal_sp2d"]

    # ================= FINAL DATA =================
    data_final = list(grouped_sp2d.values())

    # mapping untuk POST
    sp2d_mapping = {
        row["nomor_sp2d_final"]: row
        for row in data_final
    }

    # ================= POST =================
    if request.method == "POST":
        selected = request.POST.getlist('sp2d')

        if not selected:
            messages.warning(request, 'Tidak ada SP2D yang dipilih')
            return redirect(request.path)

        objs = []

        for sp2d in selected:
            row = sp2d_mapping.get(sp2d)

            if not row:
                continue

            objs.append(
                model_realisasi(
                    realisasi_dana_id=request.session.get('realisasi_dana'),
                    realisasi_tahap_id=request.session.get('realisasi_tahap'),
                    realisasi_subopd_id=request.session.get('realisasi_subopd'),

                    realisasi_rencanaposting=rencana,
                    realisasi_rencana=rencana.posting_rencanaid,
                    realisasi_subkegiatan=rencana.posting_subkegiatan,

                    realisasi_tahun=request.session.get('realisasi_tahun'),
                    realisasi_output=0,
                    realisasi_sp2d=sp2d,
                    realisasi_tgl=row['tanggal_sp2d'] or date.today(),
                    realisasi_nilai=row['nilai_realisasi'],
                )
            )

        try:
            with transaction.atomic():
                for obj in objs:
                    obj.save()
        except ValidationError as e:
            messages.error(request, f'Gagal menyimpan: {e.messages}')
            return redirect(url_sp2d, pk=rencana.pk)

        messages.success(request, f'{len(objs)} SP2D berhasil disimpan')
        return redirect(url_sp2d, pk=rencana.pk)

    # ================= RENDER =================
    return render(request, 'sipd/view_sipd.html', {
        'rencana': rencana,
        'data': data_final,
        'sp2d_sudah_realisasi': sp2d_done,
        
    })

def _get_monitor_sipd_dataset(tahun, jadwal=None, dana=None):
    # ================= AMBIL SEMUA RENCANA (OBJECT) =================
    all_rencana = []

    for key, config in SIPD_REGISTRY.items():
        model_rencana = config['model_rencana']

        filters = {
            'posting_tahun': tahun,
        }
        if jadwal:
            filters['posting_jadwal_id'] = jadwal

        if dana:
            filters['posting_dana_id'] = dana

        qs = (
            model_rencana.objects
            .select_related(
                'posting_subopd',
                'posting_subkegiatan'
            )
            .filter(**filters)
        )

        for obj in qs:
            item = {
                'posting_tahun': obj.posting_tahun,
                'posting_ket': obj.posting_ket,
                'subopd_kode': obj.posting_subopd.sub_opd_kode if obj.posting_subopd else '',
                'subopd_nama': obj.get_subopd(),
                'subkegiatan_nama': obj.get_subkegiatan(),
                'posting_pagu': obj.posting_pagu or Decimal(0),
            }
            all_rencana.append(item)

    # ================= GROUPING =================
    grouped = defaultdict(lambda: {
        'posting_pagu': Decimal(0),
        'subopd_nama': '',
        'subkegiatan_nama': ''
    })

    for item in all_rencana:
        key = (
            item['posting_tahun'],
            clean(item['posting_ket']),
            clean(item['subopd_kode'])
        )

        grouped[key]['posting_pagu'] += item['posting_pagu']

        # isi sekali saja (hindari overwrite kosong)
        if not grouped[key]['subopd_nama'] and item['subopd_nama']:
            grouped[key]['subopd_nama'] = item['subopd_nama']

        if not grouped[key]['subkegiatan_nama'] and item['subkegiatan_nama']:
            grouped[key]['subkegiatan_nama'] = item['subkegiatan_nama']

    # ================= FINAL LIST =================
    data_rencana = []

    for key, val in grouped.items():
        tahun_k, ket, opd = key

        data_rencana.append({
            'posting_tahun': tahun_k,
            'posting_ket': ket,
            'posting_subopd_kode': opd,
            'subopd_nama': val['subopd_nama'],
            'subkegiatan_nama': val['subkegiatan_nama'],
            'posting_pagu': val['posting_pagu'],
        })

    # ================= SIPD (AGGREGATE) =================
    sipd_qs = (
        Sipd.objects
        .filter(tahun=tahun)
        .values(
            'tahun',
            'kode_sub_kegiatan',
            'kode_sub_skpd'
        )
        .annotate(
            nilai_realisasi=Sum('nilai_realisasi')
        )
    )

    sipd_map = {
        (
            s['tahun'],
            clean(s['kode_sub_kegiatan']),
            clean(s['kode_sub_skpd'])
        ): s['nilai_realisasi']
        for s in sipd_qs
    }

    # ================= PROSES AKHIR =================
    hasil = []
    total_pagu = Decimal(0)
    total_sipd = Decimal(0)

    for item in data_rencana:
        key = (
            item['posting_tahun'],
            clean(item['posting_ket']),
            clean(item['posting_subopd_kode'])
        )

        nilai_sipd = sipd_map.get(key, Decimal(0))
        selisih = item['posting_pagu'] - nilai_sipd

        hasil.append({
            **item,
            'nilai_sipd': nilai_sipd,
            'selisih': selisih,
            'status': 'SESUAI' if selisih == 0 else ('BELUM ADA' if nilai_sipd == 0 else 'SELISIH')
        })

        total_pagu += item['posting_pagu']
        total_sipd += nilai_sipd

    total_selisih = total_pagu - total_sipd
    return hasil, total_pagu, total_sipd, total_selisih


def monitor_sipd(request):
    tahun_param = request.GET.get('tahun') or request.session.get('tahun') or datetime.now().year
    try:
        tahun = int(str(tahun_param).strip())
    except (TypeError, ValueError):
        tahun = datetime.now().year

    jadwal = request.session.get('jadwal')
    dana = request.GET.get('dana') or None
    if dana:
        try:
            dana = int(dana)
        except (TypeError, ValueError):
            dana = None

    hasil, total_pagu, total_sipd, total_selisih = _get_monitor_sipd_dataset(tahun, jadwal, dana)

    count_sesuai = sum(1 for item in hasil if item['status'] == 'SESUAI')
    count_selisih = sum(1 for item in hasil if item['status'] == 'SELISIH')
    count_belum = sum(1 for item in hasil if item['status'] == 'BELUM ADA')

    # ================= CONTEXT =================
    context = {
        'data': hasil,
        'total_pagu': total_pagu,
        'total_sipd': total_sipd,
        'total_selisih': total_selisih,
        'count_sesuai': count_sesuai,
        'count_selisih': count_selisih,
        'count_belum': count_belum,
        'total_items': len(hasil),
        'tahun': str(tahun),
        'dana': dana,
        'tahun_choices': FilterHelper.tahun_choices(),
        'dana_choices': FilterHelper.dana_choices(),
    }

    # ================= HTMX =================
    if request.headers.get('HX-Request'):
        return render(request, 'components/partials/table_monitor.html', context)

    return render(request, 'sipd/monitor_sipd.html', context)


def monitor_sipd_print(request):
    """
    Halaman cetak / preview PDF untuk laporan keseluruhan Monitoring SIPD.
    Dapat diakses langsung untuk dicetak fisik / save as PDF atau dimuat dalam Modal iframe.
    """
    tahun_param = request.GET.get('tahun') or request.session.get('tahun') or datetime.now().year
    try:
        tahun = int(str(tahun_param).strip())
    except (TypeError, ValueError):
        tahun = datetime.now().year

    jadwal = request.session.get('jadwal')
    dana = request.GET.get('dana') or None
    if dana:
        try:
            dana = int(dana)
        except (TypeError, ValueError):
            dana = None

    hasil, total_pagu, total_sipd, total_selisih = _get_monitor_sipd_dataset(tahun, jadwal, dana)

    dana_nama = "Semua Jenis Dana"
    if dana:
        for val, label in FilterHelper.dana_choices():
            if str(val) == str(dana):
                dana_nama = label
                break

    context = {
        'data': hasil,
        'total_pagu': total_pagu,
        'total_sipd': total_sipd,
        'total_selisih': total_selisih,
        'tahun': str(tahun),
        'dana': dana,
        'dana_nama': dana_nama,
        'tanggal_cetak': date.today(),
    }
    return render(request, 'sipd/monitor_print.html', context)


# =========================================================
# 🔍 MONITOR SIPD DETAIL  (konten Modal)
# =========================================================
def monitor_sipd_detail(request):
    """
    Menampilkan detail baris Monitor SIPD dalam Bootstrap Modal.
    Menampilkan data Upload Excel SIPD yang disinkronkan dengan data TBP:
    Kolom: No. SP2D, TBP, Tanggal SP2D, Tgl TBP, Nilai TBP.
    Total penjumlahan Nilai TBP sama persis dengan nilai SIPD pada baris sub kegiatan tersebut.
    """
    kode_ket    = clean(request.GET.get('kode_ket', ''))
    kode_opd    = clean(request.GET.get('kode_opd', ''))
    tahun_param = request.GET.get('tahun', '')

    if not kode_ket or not tahun_param:
        return HttpResponse(
            "<div class='alert alert-danger mb-0'>Parameter kode sub kegiatan dan tahun wajib diisi.</div>"
        )

    # Bersihkan format tahun (misal '2.026' atau '2,026' dari template humanize)
    clean_tahun = str(tahun_param).replace(".", "").replace(",", "").strip()
    try:
        tahun = int(clean_tahun)
    except (TypeError, ValueError):
        return HttpResponse(
            "<div class='alert alert-danger mb-0'>Format tahun tidak valid.</div>"
        )

    # --- Ambil data SIPD untuk sub kegiatan & sub OPD ini -----------------
    filters = {'tahun': tahun, 'kode_sub_kegiatan': kode_ket}
    if kode_opd:
        filters['kode_sub_skpd'] = kode_opd

    sipd_qs = Sipd.objects.filter(**filters).order_by('tanggal_sp2d', 'nomor_sp2d', 'nomor_dokumen')

    # Jika tidak ditemukan dengan kode_opd exact, coba tanpa kode_opd
    if not sipd_qs.exists() and kode_opd:
        sipd_qs = Sipd.objects.filter(tahun=tahun, kode_sub_kegiatan=kode_ket).order_by('tanggal_sp2d', 'nomor_sp2d', 'nomor_dokumen')

    # Ambil nama dari baris pertama (fallback jika tidak ada rencana)
    subopd_nama = sipd_qs.values_list('nama_sub_skpd', flat=True).first() or kode_opd
    subkeg_nama = sipd_qs.values_list('nama_sub_kegiatan', flat=True).first() or kode_ket

    # Total nilai SIPD langsung dari tabel Sipd (asal usul nilai monitor SIPD)
    total_sipd = sipd_qs.aggregate(
        total=Sum('nilai_realisasi')
    )['total'] or Decimal(0)

    # --- Ambil pagu dari rencana ------------------------------------------
    posting_pagu = Decimal(0)
    for _, config in SIPD_REGISTRY.items():
        model_rencana = config['model_rencana']
        rencana_qs = model_rencana.objects.filter(
            posting_tahun=tahun,
            posting_ket=kode_ket,
            posting_subopd__sub_opd_kode=kode_opd,
        )
        for r in rencana_qs:
            posting_pagu += (r.posting_pagu or Decimal(0))
            if r.posting_subopd and not subopd_nama:
                try:
                    subopd_nama = r.get_subopd()
                except Exception:
                    pass
            if r.posting_subkegiatan and not subkeg_nama:
                try:
                    subkeg_nama = r.get_subkegiatan()
                except Exception:
                    pass

    selisih = posting_pagu - total_sipd
    persen  = (total_sipd / posting_pagu * 100) if posting_pagu and posting_pagu > 0 else Decimal(0)
    status  = 'SESUAI' if selisih == 0 else ('BELUM ADA' if total_sipd == 0 else 'SELISIH')

    # --- SINKRONISASI SIPD DENGAN DATA TBP & REGISTER SP2D ----------------
    # Ambil nomor dokumen dari SIPD untuk dicocokkan dengan nomor_tbp di tabel TBP
    tbp_docs = [d for d in sipd_qs.values_list('nomor_dokumen', flat=True).distinct() if d]
    cleaned_docs = {clean(d) for d in tbp_docs if d}
    tbp_qs = TBP.objects.filter(tahun=tahun, nomor_tbp__in=list(cleaned_docs.union(set(tbp_docs))))
    tbp_map = {clean(t.nomor_tbp): t for t in tbp_qs}

    # Ambil pemetaan Tanggal SP2D dari Register SP2D
    from register_sp2d.models import RegisterSP2D
    all_sp2ds = set()
    for s in sipd_qs:
        if s.nomor_sp2d:
            all_sp2ds.add(clean(s.nomor_sp2d))
    for t in tbp_qs:
        if t.status_tbp:
            ext = extract_nomor_dari_status(t.status_tbp)
            if ext:
                all_sp2ds.add(clean(ext))

    register_map = {
        clean(r.nomor_sp2d): (r.tanggal_pembuatan or r.tanggal_pencairan)
        for r in RegisterSP2D.objects.filter(tahun=tahun, nomor_sp2d__in=list(all_sp2ds))
    }

    # Grouping data SIPD per TBP / Dokumen agar nilai TBP sesuai dengan rincian SIPD
    grouped = {}
    for s in sipd_qs:
        dok_clean = clean(s.nomor_dokumen)
        sp2d_clean = clean(s.nomor_sp2d)

        tbp_obj = tbp_map.get(dok_clean)
        sp2d_final = ""
        if tbp_obj and tbp_obj.status_tbp:
            sp2d_final = extract_nomor_dari_status(tbp_obj.status_tbp)
        if not sp2d_final:
            sp2d_final = sp2d_clean

        # Tanggal SP2D diambil dari Register SP2D (fallback ke s.tanggal_sp2d jika tidak ada di register)
        tgl_sp2d_val = register_map.get(clean(sp2d_final)) or register_map.get(clean(sp2d_clean)) or s.tanggal_sp2d

        # Kunci grouping per dokumen/TBP
        key = dok_clean if (tbp_obj or s.jenis_dokumen == "TBP") else f"{sp2d_final}_{dok_clean}"

        if key not in grouped:
            grouped[key] = {
                'nomor_sp2d': sp2d_final or "-",
                'nomor_tbp': dok_clean if dok_clean else "-",
                'tanggal_sp2d': tgl_sp2d_val,
                'tanggal_tbp': tbp_obj.tanggal_tbp if tbp_obj else None,
                'nilai_tbp': Decimal(0),
            }

        grouped[key]['nilai_tbp'] += (s.nilai_realisasi or Decimal(0))

        # Simpan tanggal SP2D yang valid dari Register SP2D
        if tgl_sp2d_val and not grouped[key]['tanggal_sp2d']:
            grouped[key]['tanggal_sp2d'] = tgl_sp2d_val

        # Update tanggal_tbp jika sebelumnya belum ada
        if not grouped[key].get('tanggal_tbp') and tbp_obj and tbp_obj.tanggal_tbp:
            grouped[key]['tanggal_tbp'] = tbp_obj.tanggal_tbp

    # Urutkan berdasarkan tanggal SP2D (atau tanggal TBP jika tanggal SP2D kosong), lalu nomor SP2D
    tbp_list = sorted(
        grouped.values(),
        key=lambda x: (
            str(x['tanggal_sp2d'] or x['tanggal_tbp'] or ''),
            x['nomor_sp2d'] or '',
            str(x['tanggal_tbp'] or ''),
            x['nomor_tbp'] or ''
        )
    )

    total_nilai_tbp = sum((item['nilai_tbp'] for item in tbp_list), Decimal(0))

    context = {
        'tahun'           : str(tahun),
        'kode_ket'        : kode_ket,
        'kode_opd'        : kode_opd,
        'subopd_nama'     : subopd_nama,
        'subkeg_nama'     : subkeg_nama,
        'posting_pagu'    : posting_pagu,
        'total_sipd'      : total_sipd,
        'total_nilai_tbp' : total_nilai_tbp,
        'selisih'         : selisih,
        'persen'          : persen,
        'status'          : status,
        'tbp_list'        : tbp_list,
        'item_count'      : len(tbp_list),
    }

    return render(request, 'sipd/partials/monitor_sipd_detail_modal.html', context)