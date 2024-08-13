from django.urls import path

from ..views import view_laporansisa

urlpatterns = [
    path('laporansisapdf/', view_laporansisa.pdf, name="laporansisa_pdf"),
    path('laporanlistsisa/', view_laporansisa.list, name="laporansisa_list"),
    path('laporanfiltersisa/', view_laporansisa.filter, name="laporansisa_filter"),
]