from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from project.decorators import menu_access_required, set_submenu_session

from ..models import Dana
from ..forms import DanaForm

@set_submenu_session
@menu_access_required('list')
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

@set_submenu_session
@menu_access_required('simpan')
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

@menu_access_required('update')
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

@menu_access_required('delete')
def delete_dana(request, pk):
    try:
        data = Dana.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Dana.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect("list_dana")