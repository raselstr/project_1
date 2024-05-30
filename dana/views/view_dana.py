from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from ..models import Dana
from ..forms import DanaForm

def list_dana(request):
    data = Dana.objects.all()
    form = DanaForm()
    context = {
        "judul": "Daftar Jenis Dana", 
        "tombol" : "Tambah Jenis Dana",
        "form": form, 
        "datas": data
    }
    return render(request, "dana/dana_list.html", context) 

def simpan_dana(request):
    data = Dana.objects.all()
    if request.method == "POST":
        form = DanaForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect('list_dana')
    else:
        form = DanaForm()
    context = {
        'form'  : form,
        'datas': data
    }
    return render(request, "dana/dana_list.html", context)

def update_dana(request, pk):
    data = get_object_or_404(Dana, id=pk)
    formupdate = DanaForm(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect("list_dana")
    else:
        formupdate = DanaForm(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update dana"}
    return render(request, "dana/dana_edit.html", context)

def delete_dana(request, pk):
    data = Dana.objects.get(id=pk)
    data.delete()
    messages.warning(request, "Data Berhasil dihapus")
    return redirect("list_dana")