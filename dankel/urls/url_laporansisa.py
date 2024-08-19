from django.urls import path

from ..views import view_laporansisa

urlpatterns = [
    path('laporansisaapip/', view_laporansisa.apip, name="laporansisa_apip"),
    path('laporansisapdf/', view_laporansisa.pdf, name="laporansisa_pdf"),
    path('laporanlistsisa/', view_laporansisa.list, name="laporansisa_list"),
    path('laporanfiltersisa/', view_laporansisa.filter, name="laporansisa_filter"),
]