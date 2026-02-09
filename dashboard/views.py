from django.shortcuts import render
from core.forms.filter import RekapRealisasiFilterForm
from core.services_realisasi import RealisasiService


def dashboard(request):
    form = RekapRealisasiFilterForm(request.GET or None)

    tahun = dana = tahap = None

    if form.is_valid():
        tahun = form.cleaned_data.get("tahun")
        dana = form.cleaned_data.get("dana")
        tahap = form.cleaned_data.get("tahap")

    context = {
        "judul": "Dashboard Realisasi",

        # form filter
        "form": form,

        # data dashboard
        "total_realisasi": RealisasiService.get_total_realisasi(tahun, dana, tahap),
        "rekap_dana": RealisasiService.get_rekap_per_dana(tahun, tahap),
        "rekap_tahap": RealisasiService.get_rekap_per_tahap(tahun, dana),
    }

    return render(request, "dashboard/dashboard/dashboard.html", context)
