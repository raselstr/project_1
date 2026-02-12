# djpk/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

from .models import Djpk
from core.services.realisasi_service import RealisasiService


def djpk_list(request):

    # ==============================
    # HANDLE UPLOAD
    # ==============================
    if request.method == "POST":
        # print("POST:", request.POST)
        # print("FILES:", request.FILES)

        tahun = request.POST.get("tahun")
        dana_id = request.POST.get("dana_id")
        tahap_id = request.POST.get("tahap_id")
        file = request.FILES.get("file")

        tahun = int(str(tahun).replace(".", "").replace(",", ""))
        
        if not file:
            messages.error(request, "File tidak ditemukan.")
            # print("FILE TIDAK ADA!")
            return redirect("djpk_list")

        try:
            Djpk.objects.update_or_create(
                tahun=tahun,
                jenis_dana_id=dana_id,
                tahap_id=tahap_id,
                defaults={"file": file}
            )

            messages.success(request, "File DJPK berhasil diupload.")

        except Exception as e:
            messages.error(request, f"Gagal upload: {str(e)}")

        return redirect("djpk_list")

    # ==============================
    # AMBIL DATA REKAP
    # ==============================
    rekap_data = RealisasiService.get_rekap_per_tahap_djpk()

    # Map DJPK
    djpk_map = {
        (d.tahun, d.jenis_dana_id, d.tahap_id): d
        for d in Djpk.objects.all()
    }

    for row in rekap_data:
        row["djpk"] = djpk_map.get(
            (row["tahun"], row["dana_id"], row["tahap_id"])
        )

    # ==============================
    # GROUP BY TAHUN + DANA
    # ==============================
    grouped = {}

    for row in rekap_data:
        key = (row["tahun"], row["dana_id"], row["dana_nama"])

        if key not in grouped:
            grouped[key] = []

        grouped[key].append(row)

    final_data = []

    for (tahun, dana_id, dana_nama), items in grouped.items():
        rowspan = len(items)

        for i, item in enumerate(items):
            item["show_dana"] = i == 0
            item["rowspan"] = rowspan
            final_data.append(item)

    context = {
        "rekap_data": final_data,
    }

    return render(request, "djpk/djpk_list.html", context)


def djpk_print(request, pk):
    djpk = get_object_or_404(Djpk, pk=pk)

    return render(request, "djpk/djpk_print.html", {
        "djpk": djpk
    })
