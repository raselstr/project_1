from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Opd
from .forms import OpdForm

# Create your views here.
def opd_list(request):
    opd = Opd.objects.all()
    form = OpdForm()
    return render(request, "opd/opd_list.html", {"opds": opd, "form": form})

def simpan_opd(request):
    opd = Opd.objects.all()
    if request.method == "POST":
        form = OpdForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('opd_list')
    else:
        form = OpdForm()
    return render(request, "opd/opd_list.html", {"form": form,'opds':opd})


# View untuk mengedit data OPD
def edit_opd(request, opd_id):
    if request.method == "POST":
        kode_opd = request.POST.get('kodeOPD')
        nama_opd = request.POST.get('namaOPD')
        Opd.edit_opd(opd_id, kode_opd, nama_opd)
        return HttpResponseRedirect(reverse('opd_list'))
    else:
        opd = Opd.objects.get(id=opd_id)
        return render(request, "opd/edit_opd.html", {"opd": opd})

def delete_opd(request, opd_id):
    opd = Opd.objects.get(id=opd_id)
    opd.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect("opd_list")
