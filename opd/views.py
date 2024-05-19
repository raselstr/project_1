from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Opd

# Create your views here.
def opd_list(request):
    opd = Opd.objects.all()
    return render(request, "opd/opd_list.html", {"opds": opd})


def simpan_opd(request):
    if request.method == "POST":
        kode_opd = request.POST.get('kodeOPD')
        nama_opd = request.POST.get('namaOPD')
        opd_baru = Opd(kode_opd=kode_opd, nama_opd=nama_opd)
        opd_baru.simpan_opd()
        return HttpResponseRedirect(reverse('opd_list'))


