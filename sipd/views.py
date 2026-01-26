import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.management import call_command
from django_tables2 import RequestConfig

from .forms import SipdUploadForm
from .models import Sipd
from .tables import SipdTable
from .filters import SipdFilter

from openpyxl import Workbook
from django.http import HttpResponse


def upload_sipd(request):
    tahun = request.session.get("tahun")

    # =======================
    # UPLOAD & IMPORT
    # =======================
    if request.method == "POST":
        form = SipdUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data["file"]
            upload_dir = settings.MEDIA_ROOT / "import"
            os.makedirs(upload_dir, exist_ok=True)

            file_path = upload_dir / file.name
            with open(file_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            try:
                call_command(
                    "import_sipd_excel",
                    str(file_path),
                    tahun=tahun,
                )
                messages.success(
                    request,
                    f"Import SIPD berhasil untuk Tahun Anggaran {tahun}"
                )
                return redirect("upload_sipd")

            except Exception as e:
                messages.error(request, f"Gagal import data: {e}")
    else:
        form = SipdUploadForm()

    # =======================
    # QUERYSET
    # =======================
    qs = Sipd.objects.all()
    if tahun:
        qs = qs.filter(tahun=tahun)

    # =======================
    # SEARCH (django-filter)
    # =======================
    sipd_filter = SipdFilter(request.GET, queryset=qs)
    qs = sipd_filter.qs

    # =======================
    # TABLE + PAGINATION
    # =======================
    table = SipdTable(qs)

    per_page = request.GET.get("per_page", "10")
    if per_page == "all":
        table.paginate = False
        # RequestConfig(request).configure(table)   # ⛔ TANPA paginate
    else:
        RequestConfig(
        request,
        paginate={"per_page": int(per_page)}
    ).configure(table)
        
    context = {
        "form": form,
        "table": table,
        "filter": sipd_filter,
        "judul": "Upload Excel SIPD",
        "btntombol": "Upload",
        "tahun": tahun,
    }
    
    # 🔥 kalau HTMX → render table saja
    
    if request.htmx:
        return render(request, "sipd/partials/table.html", context)

    return render(request, "sipd/upload.html", context)

def export_sipd_excel(request):
    tahun = request.session.get("tahun")
    q = request.GET.get("q")

    qs = Sipd.objects.all()

    if tahun:
        qs = qs.filter(tahun=tahun)

    if q:
        qs = qs.filter(
            nama_sub_skpd__icontains=q
            | qs.filter(nama_program__icontains=q)
            | qs.filter(nama_kegiatan__icontains=q)
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Data SIPD"

    # ================= HEADER =================
    headers = [
        "Tahun",
        "Kode Sub SKPD",
        "Nama Sub SKPD",
        "Kode Program",
        "Nama Program",
        "Kode Kegiatan",
        "Nama Kegiatan",
        "Nilai Realisasi",
    ]
    ws.append(headers)

    # ================= DATA =================
    for obj in qs:
        ws.append([
            obj.tahun,
            obj.kode_sub_skpd,
            obj.nama_sub_skpd,
            obj.kode_program,
            obj.nama_program,
            obj.kode_kegiatan,
            obj.nama_kegiatan,
            obj.nilai_realisasi,
        ])

    # ================= RESPONSE =================
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="sipd_{tahun or "all"}.xlsx"'
    )

    wb.save(response)
    return response