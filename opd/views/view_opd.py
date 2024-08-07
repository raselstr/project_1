from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from dana.utils import datasubrinc
from project.decorators import menu_access_required, set_submenu_session



from ..models import Opd
from ..forms import OpdForm

Form_data = OpdForm
Model_data = Opd    
lokasitemplate = 'opd/opd_list.html'
lokasiupdate = 'opd/opd_edit.html'
tag_url = 'list_opd'

@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    
    # dankel_keg = get_object_or_404(Model_data or None)
    # data = dankel_keg.dankelsubs.all()
    data = Model_data.objects.all().order_by('-kode_opd')
    form = Form_data(request.POST or None)
    
    context = {
        "judul": "Daftar OPD", 
        "tombol" : "Tambah OPD",
        "form": form, 
        "datas": data,
        
    }
    return render(request, lokasitemplate, context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan(request):
    request.session['next'] = request.get_full_path()
    if request.method == "POST":
        form = Form_data(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect(tag_url)
    else:
        form = Form_data()
    context = {
        'form'  : form,
    }
    return render(request, lokasitemplate, context)

@set_submenu_session
@menu_access_required('update')
def update(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Model_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect(tag_url)
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update Kegiatan"}
    return render(request, lokasiupdate, context)

@set_submenu_session
@menu_access_required('delete')
def delete(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url)


