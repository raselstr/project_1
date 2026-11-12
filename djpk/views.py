from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest

from .models import Djpk
from core.services.djpk_service import DjpkService
from core.services.pagu_service import PaguService
from core.services.realisasi_service import RealisasiService
from dana.models import Subkegiatan, TahapDana


def djpk_list(request):

    # ==============================
    # HANDLE UPLOAD
    # ==============================

    if request.method == "POST":

        tahun = request.POST.get("tahun")
        dana_id = request.POST.get("dana_id")
        tahap_id = request.POST.get("tahap_id")
        file = request.FILES.get("file")

        try:
            tahun = int(str(tahun).replace(".", "").replace(",", ""))
        except (TypeError, ValueError):
            messages.error(request, "Tahun tidak valid.")
            return redirect("djpk_list")

        if not file:
            messages.error(request, "File tidak ditemukan.")
            return redirect("djpk_list")

        Djpk.objects.update_or_create(
            tahun=tahun,
            jenis_dana_id=dana_id,
            tahap_id=tahap_id,
            defaults={"file": file}
        )

        messages.success(request, "File DJPK berhasil diupload.")
        return redirect("djpk_list")

    # ==============================
    # AMBIL DATA REKAP
    # ==============================

    rekap_data = DjpkService.get_rekap()

    # Map DJPK
    djpk_map = {
        (d.tahun, d.jenis_dana_id, d.tahap_id): d
        for d in Djpk.objects.all()
    }

    total_realisasi_all = Decimal(0)
    for row in rekap_data:
        row["djpk"] = djpk_map.get(
            (row["tahun"], row["dana_id"], row["tahap_id"])
        )
        total_realisasi_all += (row.get("realisasi") or Decimal(0))

    # ==============================
    # GROUP ROWSPAN
    # ==============================

    grouped = {}

    for row in rekap_data:

        key = (
            row["tahun"],
            row["dana_id"],
            row["dana_nama"]
        )

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(row)

    final_data = []
    total_pagu_all = Decimal(0)

    for (tahun, dana_id, dana_nama), items in grouped.items():

        rowspan = len(items)
        if items and items[0].get("pagu"):
            total_pagu_all += (items[0]["pagu"] or Decimal(0))

        for i, item in enumerate(items):

            item["show_group"] = i == 0
            item["rowspan"] = rowspan

            final_data.append(item)

    files_uploaded_count = sum(1 for d in djpk_map.values() if d and d.file)

    context = {
        "rekap_data": final_data,
        "total_pagu_all": total_pagu_all,
        "total_realisasi_all": total_realisasi_all,
        "total_files_uploaded": files_uploaded_count,
        "total_tahap_count": len(final_data),
    }

    return render(request, "djpk/djpk_list.html", context)


def djpk_detail(request):
    """
    Menampilkan data detail DJPK per tahap dalam Modal
    Mendukung Tab HTML (Rincian realisasi & per OPD) dan Tab PDF (File DJPK yang diupload).
    """
    tahun = request.GET.get("tahun")
    dana_id = request.GET.get("dana_id")
    tahap_id = request.GET.get("tahap_id")
    active_tab = request.GET.get("tab", "html")

    if not tahun or not dana_id or not tahap_id:
        return HttpResponse("<div class='alert alert-danger mb-0'>Parameter tahun, jenis dana, dan tahap harus disertakan.</div>")

    try:
        tahun = int(str(tahun).replace(".", "").replace(",", ""))
        dana_id = int(dana_id)
        tahap_id = int(tahap_id)
    except (TypeError, ValueError):
        return HttpResponse("<div class='alert alert-danger mb-0'>Format parameter tidak valid.</div>")

    dana_obj = Subkegiatan.objects.filter(id=dana_id).first()
    tahap_obj = TahapDana.objects.filter(id=tahap_id).first()

    dana_nama = dana_obj.sub_nama if dana_obj else f"Dana ID {dana_id}"
    tahap_nama = tahap_obj.tahap_dana if tahap_obj else f"Tahap {tahap_id}"

    djpk_obj = Djpk.objects.filter(tahun=tahun, jenis_dana_id=dana_id, tahap_id=tahap_id).first()

    pagu = PaguService.get_total_pagu(tahun=tahun, dana=dana_id) or Decimal(0)
    opd_rekap = RealisasiService.get_rekap_per_opd(tahun=tahun, dana=dana_id, tahap=tahap_id)

    # Ambil rincian transaksi realisasi
    transactions = []
    total_realisasi = Decimal(0)

    for model, field in RealisasiService.REALISASI_MODELS.items():
        qs = model.objects.filter(**{
            field["tahun"]: tahun,
            field["dana"]: dana_id,
            field["tahap"]: tahap_id
        }).select_related(
            field["subopd"].replace("_id", ""),
            field["tahap"].replace("_id", "")
        )

        for item in qs:
            subopd_name = ""
            if hasattr(item, "realisasi_subopd") and item.realisasi_subopd:
                subopd_name = getattr(item.realisasi_subopd, "sub_nama", str(item.realisasi_subopd))
            elif hasattr(item, "realisasidankel_subopd") and item.realisasidankel_subopd:
                subopd_name = getattr(item.realisasidankel_subopd, "sub_nama", str(item.realisasidankel_subopd))

            subkeg_name = ""
            if hasattr(item, "realisasi_subkegiatan") and item.realisasi_subkegiatan:
                subkeg_name = str(item.realisasi_subkegiatan)
            elif hasattr(item, "realisasidankel_rencana") and item.realisasidankel_rencana:
                subkeg_name = str(item.realisasidankel_rencana)

            sp2d = (
                getattr(item, "realisasi_sp2d", "")
                or getattr(item, "realisasidankel_sp2d", "")
                or getattr(item, "realisasidankel_sp2dtu", "")
            )
            tgl = getattr(item, "realisasi_tgl", None) or getattr(item, "realisasidankel_tgl", None)
            nilai = (
                getattr(item, "realisasi_nilai", Decimal(0))
                or getattr(item, "realisasidankel_lpjnilai", Decimal(0))
            )

            val = nilai or Decimal(0)
            total_realisasi += val
            transactions.append({
                "subopd": subopd_name,
                "subkegiatan": subkeg_name,
                "sp2d": sp2d,
                "tgl": tgl,
                "nilai": val,
            })

    transactions.sort(key=lambda x: str(x["tgl"] or ""))

    sisa = pagu - total_realisasi
    persen = (total_realisasi / pagu * 100) if pagu and pagu > 0 else Decimal(0)

    # Tambahkan persen kontribusi pada opd_rekap
    for opd in opd_rekap:
        opd_total = opd.get("total", Decimal(0))
        opd["persen"] = (opd_total / total_realisasi * 100) if total_realisasi and total_realisasi > 0 else Decimal(0)

    context = {
        "tahun": tahun,
        "dana_id": dana_id,
        "dana_nama": dana_nama,
        "tahap_id": tahap_id,
        "tahap_nama": tahap_nama,
        "pagu": pagu,
        "total_realisasi": total_realisasi,
        "sisa": sisa,
        "persen": persen,
        "opd_rekap": opd_rekap,
        "transactions": transactions,
        "djpk_obj": djpk_obj,
        "active_tab": active_tab,
    }

    return render(request, "djpk/partials/djpk_detail_modal.html", context)


def djpk_print(request, pk):
    djpk = get_object_or_404(Djpk, pk=pk)

    return render(request, "djpk/djpk_print.html", {
        "djpk": djpk
    })
