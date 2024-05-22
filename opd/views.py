from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Opd
from .forms import OpdForm

# Create your views here.
def opd_list(request):
    opd = Opd.objects.all()
    return render(request, "opd/opd_list.html", {"opds": opd})

def form_opd(request):
    form = OpdForm()
    
    return render(request, "opd/form.html", {"form": form})

def simpan_opd(request):
    if request.method == "POST":
        form = OpdForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('opd_list')
        else:
            kode_opd = request.POST.get('kodeOPD')
        
        return HttpResponseRedirect(reverse('opd_list'))
    
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
    return HttpResponseRedirect(reverse('opd_list'))




