from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Djpk
from core.services.djpk_service import DjpkService


def djpk_list(request):

    # ==============================
    # HANDLE UPLOAD
    # ==============================

    if request.method == "POST":

        tahun = request.POST.get("tahun")
        dana_id = request.POST.get("dana_id")
        tahap_id = request.POST.get("tahap_id")
        file = request.FILES.get("file")

        tahun = int(str(tahun).replace(".", "").replace(",", ""))

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

    for row in rekap_data:
        row["djpk"] = djpk_map.get(
            (row["tahun"], row["dana_id"], row["tahap_id"])
        )


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

    for (tahun, dana_id, dana_nama), items in grouped.items():

        rowspan = len(items)

        for i, item in enumerate(items):

            item["show_group"] = i == 0
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
