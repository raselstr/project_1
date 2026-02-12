from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Menu, Submenu
from project.context_processors import menu_context_processor
from project.decorators import menu_access_required  # decorator akses menu

from core.forms.filters import RekapRealisasiFilterForm
from core.services.realisasi_service import RealisasiService


@login_required
@menu_access_required("dashboard")
def index(request):
    # Ambil context menu (header/sidebar)
    context = menu_context_processor(request)

    # Ambil form filter
    form = RekapRealisasiFilterForm(request.GET or None)

    # Default filter
    tahun = dana = tahap = None
    if form.is_valid():
        tahun = form.cleaned_data.get("tahun")
        dana = form.cleaned_data.get("dana")
        tahap = form.cleaned_data.get("tahap")

    # ================= HITUNG TOTAL & REKAP =================
    total_pagu = RealisasiService.get_total_pagu(tahun, dana)
    total_realisasi = RealisasiService.get_total_realisasi(tahun, dana, tahap)
    total_sisa = total_pagu - total_realisasi

    rekap_tahap = RealisasiService.get_rekap_per_tahap(tahun, dana)
    rekap_opd = RealisasiService.get_rekap_per_opd(tahun, dana, tahap)

    # ================= UPDATE CONTEXT =================
    context.update({
        "judul": "Dashboard Realisasi",
        "form": form,
        "total_pagu": total_pagu,
        "total_realisasi": total_realisasi,
        "total_sisa": total_sisa,
        "rekap_tahap": rekap_tahap,
        "rekap_opd": rekap_opd,
    })

    return render(request, "dashboard/dashboard.html", context)
