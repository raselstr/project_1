import csv
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.core.cache import cache
from django_tables2 import RequestConfig
from openpyxl import Workbook
from django.http import HttpResponse

from .tasks import import_sipd_task

from .forms import SipdUploadForm
from .models import Sipd
from .tables import SipdTable
from .filters import SipdFilter

model_sipd = Sipd

url_upload_sipd = "upload_sipd"


def upload_sipd(request):
    tahun = request.session.get("tahun")
    form = SipdUploadForm()

    if request.method == "POST":
        form = SipdUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            request.session["tahun"] = tahun     # ← SIMPAN KE SESSION

            upload_dir = Path(settings.MEDIA_ROOT) / "import"
            upload_dir.mkdir(parents=True, exist_ok=True)

            file_path = upload_dir / file.name
            with open(file_path, "wb+") as f:
                for chunk in file.chunks():
                    f.write(chunk)

            task = import_sipd_task.delay(str(file_path), tahun)
            return JsonResponse({"task_id": task.id})

        return JsonResponse({"error": form.errors}, status=400)

    # ================= TABLE + FILTER =================
    qs = Sipd.objects.all()
    if tahun:
        qs = qs.filter(tahun=tahun)
    sipd_filter = SipdFilter(request.GET, queryset=qs)
    qs = sipd_filter.qs

    table = SipdTable(qs)
    per_page = request.GET.get("per_page", "10")
    if per_page != "all":
        RequestConfig(request, paginate={"per_page": int(per_page)}).configure(table)
    
    context = {
        "form": form,
        "table": table,
        "filter": sipd_filter,
        "judul": "Upload Excel SIPD",
        "judulskip" : "Daftar yang di lewati",
        "tahun": tahun,
    }
    if request.htmx:
        return render(request, "sipd/partials/table.html", context)

    return render(request, "sipd/upload.html", context)


def sipd_import_progress(request, task_id):
    return JsonResponse(cache.get(f"sipd_{task_id}", {"current": 0, "total": 1}))



def skipped_sipd_view(request, tahun):
    skipped_path = Path(settings.MEDIA_ROOT) / "import" / f"sipd_skipped_{tahun}.csv"
    rows = []

    if skipped_path.exists():
        with open(skipped_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # pastikan semua key ada, strip whitespace
                clean_row = {k.strip(): v.strip() if v else "" for k, v in row.items()}
                rows.append(clean_row)

    context = {
        "tahun": tahun,
        "rows": rows,
    }
    return render(request, "sipd/skipped_list.html", context)




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
        "Tahun",
        "Nama Sub SKPD",
        "Kode Sub Kegiatan",
        "Nama Sub Kegiatan",
        "Kode Rekening",
        "Nama Rekening",
        "Nomor Dokumen",
        "Nomor SP2D",
        "Tanggal SP2D",
        "Nilai Realisasi",
    ]
    ws.append(headers)

    for row in qs.values_list(
        "tahun",
        "nama_sub_skpd",
        "kode_sub_kegiatan",
        "nama_sub_kegiatan",
        "kode_rekening",
        "nama_rekening",
        "nomor_dokumen",
        "nomor_sp2d",
        "tanggal_sp2d",
        "nilai_realisasi",
    ):
        ws.append(row)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="sipd_{tahun or "all"}.xlsx"'
    wb.save(response)

    return response

from sipd.registry import SIPD_REGISTRY, get_rencana_by_pk, get_sp2d_sudah_realisasi_global
from django.http import HttpResponseBadRequest
from django.db.models import Q, Sum, Min
from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import date
from django.shortcuts import render
from project.decorators import menu_access_required, set_submenu_session


@set_submenu_session
@menu_access_required('list')
def view_sipd(request, mode, pk):
    request.session['next'] = request.get_full_path()
    config = SIPD_REGISTRY.get(mode)
    if not config:
        return HttpResponseBadRequest('Mode SIPD tidak valid')
    
    model_rencanaposting = config['model_rencana']
    model_rencanaposting_sisa = config['model_rencana_sisa']
    model_realisasi = config['model_realisasi']
    model_realisasi_sisa = config.get('model_realisasi_sisa')
    # model_sipd = config['model_sipd']
    url_sp2d = config['url_sp2d']

    # =====================================================
    # AMBIL RENCANA
    # =====================================================
    # rencana = (
    #     model_rencanaposting.objects
    #     .select_related(
    #         'posting_subopd',
    #         'posting_subkegiatan',
    #         'posting_dana'
    #     )
    #     .filter(pk=pk)
    #     .first()
    # )
    # print(rencana)
    
    rencana = get_rencana_by_pk(
        pk,
        model_rencanaposting,
        model_rencanaposting_sisa
    )

    if not rencana:
        messages.error(request, 'Data rencana tidak ditemukan')
        return redirect('url_list_rencana')

    # =====================================================
    # FILTER DASAR SIPD SESUAI RENCANA
    # =====================================================
    filters = Q(
        tahun=rencana.posting_tahun,
        kode_sub_kegiatan=rencana.posting_ket,
        kode_sub_skpd=rencana.posting_subopd.sub_opd_kode
    )

    # =====================================================
    # QUERYSET SIPD ASLI (UNTUK POST)
    # =====================================================
    sipd_qs_raw = model_sipd.objects.filter(filters)

    # =====================================================
    # SP2D YANG SUDAH MASUK REALISASI
    # =====================================================
    sp2d_sudah_realisasi = set()

    sp2d_sudah_realisasi = get_sp2d_sudah_realisasi_global(
        rencana,
        model_rencanaposting,
        model_realisasi,
        model_rencanaposting_sisa,
        model_realisasi_sisa,
    )
    # =====================================================
    # QUERYSET SIPD UNTUK DITAMPILKAN (GROUP + SUM)
    # =====================================================
    sipd_qs = (
        sipd_qs_raw
        .exclude(nomor_sp2d__in=sp2d_sudah_realisasi)
        .values('nomor_sp2d')
        .annotate(
            tanggal_sp2d=Min('tanggal_sp2d'),
            nilai_realisasi=Sum('nilai_realisasi'),
        )
        .order_by('tanggal_sp2d', 'nomor_sp2d')
    )

    # =====================================================
    # SIMPAN DATA TERPILIH
    # =====================================================
    if request.method == "POST":
        selected_sp2d = request.POST.getlist('sp2d')

        if not selected_sp2d:
            messages.warning(request, 'Tidak ada SP2D yang dipilih')
            return redirect(request.path)

        # ambil data sipd asli lalu agregasi ulang
        agregat_sp2d = (
            sipd_qs_raw
            .filter(nomor_sp2d__in=selected_sp2d)
            .exclude(nomor_sp2d__in=sp2d_sudah_realisasi)
            .values('nomor_sp2d')
            .annotate(
                tgl=Min('tanggal_sp2d'),
                total=Sum('nilai_realisasi')
            )
        )

        data_realisasi = [
            model_realisasi(
                realisasi_dana_id=request.session.get('realisasi_dana'),
                realisasi_tahap_id=request.session.get('realisasi_tahap'),
                realisasi_subopd_id=request.session.get('realisasi_subopd'),

                realisasi_rencanaposting=rencana,
                realisasi_rencana=rencana.posting_rencanaid,
                realisasi_subkegiatan=rencana.posting_subkegiatan,

                realisasi_tahun=request.session.get('realisasi_tahun'),
                realisasi_output=0,
                realisasi_sp2d=row['nomor_sp2d'],
                realisasi_tgl=row['tgl'] or date.today(),
                realisasi_nilai=row['total'],
            )
            for row in agregat_sp2d
        ]

        try:
            with transaction.atomic():
                for obj in data_realisasi:
                    obj.save()  # 🔥 full_clean + clean otomatis

        except ValidationError as e:
            messages.error(
                request,
                f'Gagal menyimpan Realisasi: {e.messages}'
            )
            return redirect(url_sp2d, pk=rencana.pk)

        messages.success(
            request,
            f'{len(data_realisasi)} SP2D berhasil disimpan ke Realisasi'
        )

        return redirect(url_sp2d, pk=rencana.pk)

    # =====================================================
    # CONTEXT
    # =====================================================
    context = {
        'rencana': rencana,
        'data': sipd_qs,
        'sp2d_sudah_realisasi': sp2d_sudah_realisasi,
    }
    return render(request, 'sipd/view_sipd.html', context)