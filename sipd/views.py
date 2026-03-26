# views.py
import csv
from pathlib import Path
from datetime import date

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, Min
from django.core.exceptions import ValidationError

from django_tables2 import RequestConfig
from openpyxl import Workbook

from project.decorators import menu_access_required, set_submenu_session

from sipd.registry import (
    SIPD_REGISTRY,
    get_rencana_by_pk,
    get_sp2d_sudah_realisasi_global
)

from .models import Sipd, TBP
from .forms import SipdUploadForm, TBPUploadForm
from .tables import SipdTable, TBPTable
from .filters import SipdFilter
from .tasks import import_sipd_task, import_tbp_task


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
    tahun = request.session.get("tahun")
    form = SipdUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if not form.is_valid():
            return JsonResponse({"error": form.errors}, status=400)

        file_path = handle_uploaded_file(form.cleaned_data["file"], "sipd")
        task = import_sipd_task.delay(str(file_path), tahun)

        return JsonResponse({"task_id": task.id})

    qs = Sipd.objects.all()
    if tahun:
        qs = qs.filter(tahun=tahun)

    sipd_filter = SipdFilter(request.GET, queryset=qs)
    table = SipdTable(sipd_filter.qs)
    apply_pagination(request, table)

    context = {
        "form": form,
        "table": table,
        "judul": "Upload Excel SIPD",
        "judulskip": "Data yang dilewati",
        "tahun": tahun,

        # 🔥 dynamic config
        "url_upload": "/sipd/",
        "url_progress": "/sipd/progress/TASK_ID/",
        "url_list": "/sipd/",
        "url_export": "/sipd/export/",
        "url_skipped": f"/sipd/skipped/{tahun}/" if tahun else None,

        "table_template": "components/partials/table.html",
    }

    template = "components/partials/table.html" if request.htmx else "components/upload.html"
    return render(request, template, context)


def sipd_import_progress(request, task_id):
    return import_progress(request, task_id, "sipd")


def skipped_sipd_view(request, tahun):
    return skipped_view(request, tahun, "sipd")


def export_sipd_excel(request):
    tahun = request.session.get("tahun")

    qs = Sipd.objects.all()
    if tahun:
        qs = qs.filter(tahun=tahun)

    qs = SipdFilter(request.GET, queryset=qs).qs

    wb = Workbook()
    ws = wb.active
    ws.title = "Data SIPD"

    headers = [
        "Tahun", "Nama Sub SKPD", "Kode Sub Kegiatan",
        "Kode Rekening", "Nomor SP2D", "Nilai Realisasi"
    ]
    ws.append(headers)

    for row in qs.values_list(
        "tahun", "nama_sub_skpd", "kode_sub_kegiatan",
        "kode_rekening", "nomor_sp2d", "nilai_realisasi"
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
    tahun = request.session.get("tahun")
    form = TBPUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if not form.is_valid():
            return JsonResponse({"error": form.errors}, status=400)

        file_path = handle_uploaded_file(form.cleaned_data["file"], "tbp")
        task = import_tbp_task.delay(str(file_path), tahun)

        return JsonResponse({"task_id": task.id})

    qs = TBP.objects.all().order_by("-tanggal_tbp")
    table = TBPTable(qs)
    apply_pagination(request, table)

    context = {
        "form": form,
        "table": table,
        "judul": "Upload TBP",

        "url_upload": "/sipd/tbp/",
        "url_progress": "/sipd/tbp/progress/TASK_ID/",
        "url_list": "/sipd/tbp/",
        "url_export": "/sipd/tbp/export/",
        "url_skipped": None,

        "table_template": "components/partials/table.html",
    }

    template = "components/partials/table.html" if request.htmx else "components/upload.html"
    return render(request, template, context)


def tbp_import_progress(request, task_id):
    return import_progress(request, task_id, "tbp")


def export_tbp_excel(request):
    qs = TBP.objects.all().order_by("-tanggal_tbp")

    wb = Workbook()
    ws = wb.active
    ws.title = "Data TBP"

    ws.append(["Tahun", "Tanggal", "Nomor", "Nilai"])

    for row in qs.values_list("tahun", "tanggal_tbp", "nomor_tbp", "nilai_tbp"):
        ws.append(row)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="tbp.xlsx"'

    wb.save(response)
    return response

import re
from datetime import date

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

    base_filter = Q(
        tahun=rencana.posting_tahun,
        kode_sub_kegiatan=rencana.posting_ket,
        kode_sub_skpd=rencana.posting_subopd.sub_opd_kode
    )

    sipd_qs_raw = Sipd.objects.filter(base_filter)

    # =========================================
    # 🔥 AMBIL DATA TBP SEKALI
    # =========================================
    tbp_map = {}

    tbp_docs = sipd_qs_raw.filter(
        jenis_dokumen="TBP"
    ).values_list("nomor_dokumen", flat=True)

    tbp_qs = TBP.objects.filter(
        tahun=rencana.posting_tahun,
        nomor_tbp__in=tbp_docs
    )

    for tbp in tbp_qs:
        if tbp.status_tbp:
            match = re.search(r"SP2D nomor:\s*(.*)", tbp.status_tbp)
            if match:
                tbp_map[tbp.nomor_tbp] = match.group(1).strip()

    # =========================================
    # DATA SUDAH REALISASI
    # =========================================
    sp2d_done = get_sp2d_sudah_realisasi_global(
        rencana,
        model_rencana,
        model_realisasi,
        model_rencana_sisa,
        model_realisasi_sisa,
    )

    # =========================================
    # AGREGASI SIPD
    # =========================================
    sipd_qs = (
        sipd_qs_raw
        .values('nomor_sp2d', 'nomor_dokumen', 'jenis_dokumen')
        .annotate(
            tanggal_sp2d=Min('tanggal_sp2d'),
            nilai_realisasi=Sum('nilai_realisasi'),
        )
        .order_by('tanggal_sp2d', 'nomor_sp2d')
    )

    # =========================================
    # 🔥 BUILD FINAL DATA + MAP UNTUK POST
    # =========================================
    data_final = []
    sp2d_mapping = {}  # 🔥 penting untuk POST

    for row in sipd_qs:
        if row["jenis_dokumen"] == "TBP":
            nomor_sp2d_final = tbp_map.get(row["nomor_dokumen"], "")
        else:
            nomor_sp2d_final = row["nomor_sp2d"]

        # skip jika sudah direalisasi
        if nomor_sp2d_final in sp2d_done:
            continue

        row["nomor_sp2d_final"] = nomor_sp2d_final
        data_final.append(row)

        # mapping untuk POST
        sp2d_mapping[nomor_sp2d_final] = row

    # =========================================
    # 🔥 SIMPAN KE REALISASI (PAKAI SP2D FINAL)
    # =========================================
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
                    realisasi_sp2d=sp2d,  # 🔥 pakai hasil TBP
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

    return render(request, 'sipd/view_sipd.html', {
        'rencana': rencana,
        'data': data_final,
        'sp2d_sudah_realisasi': sp2d_done,
    })