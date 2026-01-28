import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.management import call_command
from django_tables2 import RequestConfig
from project.decorators import menu_access_required, set_submenu_session

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
        "nama_sub_skpd",
        "kode_sub_kegiatan",
        "nama_sub_kegiatan",
        "kode_rekening",
        "nama_rekening",
        "nomor_dokumen",
        "nomor_sp2d",
        "nilai_realisasi",
    ]
    ws.append(headers)

    # ================= DATA =================
    for obj in qs:
        ws.append([
            obj.tahun,
            obj.nama_sub_skpd,
            obj.kode_sub_kegiatan,
            obj.nama_sub_kegiatan,
            obj.kode_rekening,
            obj.nama_rekening,
            obj.nomor_dokumen,
            obj.nomor_sp2d,
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

from django.db.models import Q
from django.contrib import messages
from sipd.models import Sipd
from pendidikan.models import Realisasi
from pendidikan.models import Rencanaposting
from datetime import date

model_rencana = Rencanaposting
model_sipd = Sipd


@set_submenu_session
@menu_access_required('list')
def view_sipd(request, pk):
    request.session['next'] = request.get_full_path()

    # =============================
    # AMBIL RENCANA
    # =============================
    rencana = model_rencana.objects.select_related(
        'posting_subopd',
        'posting_subkegiatan',
        'posting_dana'
    ).filter(pk=pk).first()

    if not rencana:
        messages.error(request, 'Data rencana tidak ditemukan')
        return redirect('url_list_rencana')

    # =============================
    # FILTER SIPD SESUAI RENCANA
    # =============================
    filters = Q(
        tahun=rencana.posting_tahun,
        kode_sub_kegiatan=rencana.posting_ket,
        kode_sub_skpd=rencana.posting_subopd.sub_opd_kode
    )

    sipd_qs = Sipd.objects.filter(filters).order_by(
        'tanggal_sp2d',
        'nomor_sp2d'
    )

    # =============================
    # SP2D YANG SUDAH MASUK REALISASI
    # =============================
    sp2d_sudah_realisasi = set(
        Realisasi.objects.filter(
            realisasi_rencanaposting=rencana
        ).values_list('realisasi_sp2d', flat=True)
    )

    # =============================
    # SIMPAN DATA TERPILIH
    # =============================
    if request.method == "POST":
        selected_sp2d = request.POST.getlist('sp2d')

        sipd_terpilih = sipd_qs.filter(
            nomor_sp2d__in=selected_sp2d
        ).exclude(
            nomor_sp2d__in=sp2d_sudah_realisasi
        )

        data_realisasi = []

        for row in sipd_terpilih:
            data_realisasi.append(
                Realisasi(
                    realisasi_dana_id=request.session.get('realisasi_dana'),
                    realisasi_tahap_id=request.session.get('realisasi_tahap'),
                    realisasi_subopd_id=request.session.get('realisasi_subopd'),

                    realisasi_rencanaposting=rencana,
                    realisasi_rencana=rencana.posting_rencanaid,
                    realisasi_subkegiatan=rencana.posting_subkegiatan,

                    realisasi_tahun=request.session.get('realisasi_tahun'),
                    realisasi_output=0,
                    realisasi_sp2d=row.nomor_sp2d,
                    realisasi_tgl=row.tanggal_sp2d or date.today(),
                    realisasi_nilai=row.nilai_realisasi,
                )
            )

        Realisasi.objects.bulk_create(data_realisasi)

        messages.success(
            request,
            f'{len(data_realisasi)} SP2D berhasil disimpan ke Realisasi'
        )
        return redirect(request.path)

    # =============================
    # CONTEXT
    # =============================
    context = {
        'judul': 'Realisasi SIPD',
        'subjudul': rencana.posting_subkegiatan.dausgpendidikansub_nama,
        'rencana': rencana,
        'data': sipd_qs,
        'sp2d_sudah_realisasi': sp2d_sudah_realisasi,
    }

    return render(request, 'sipd/view_sipd.html', context)
