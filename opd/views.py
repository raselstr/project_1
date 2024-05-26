from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Opd
from .forms import OpdForm

# Create your views here.
def opd_list(request):
    opd = Opd.objects.all()
    form = OpdForm()
    context = {
        "judul": "Daftar OPD", 
        "form": form, 
        "opds": opd
    }
    return render(request, "opd/opd_list.html", context)

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
    context = {
        'form'  : form,
        'opds'  : opd
    }
    return render(request, "opd/opd_list.html", context)


# View untuk mengedit data OPD
def update_opd(request, pk):
    opd = Opd.objects.get(id=pk)
    form = OpdForm(request.POST or None, instance=opd)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("opd_list")
    else:
        form = OpdForm(instance=opd)

    opd = Opd.objects.all()
    context = {"form": form, "opds": opd, "judul": "Update OPD"}
    return render(request, "opd/edit_opd.html", context)


def delete_opd(request, pk):
    opd = Opd.objects.get(id=pk)
    opd.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect("opd_list")
