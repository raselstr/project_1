from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from dana.utils import datasubrinc
from project.decorators import menu_access_required, set_submenu_session

from ...models import DankelKeg,Dankelsub
from ...forms.form_dankel import DankelSubForm

Form_data = DankelSubForm
Model_data = Dankelsub
Model_induk = DankelKeg
lokasitemplate = 'dankel/dankelsub/dankelsub_list.html'
lokasiupdate = 'dankel/dankelsub/dankelsub_edit.html'
tag_url = 'list_dankelsub'

@set_submenu_session
@menu_access_required('list')
def list(request, number, sub):
    request.session['next'] = request.get_full_path()
    
    dankel_keg = get_object_or_404(Model_induk, id=sub)
    data = dankel_keg.dankelsubs.all()
    # data = Model_data.objects.all()
    form = Form_data(request.POST or None, sub=sub)
    
    context = {
        "judul": "Daftar Sub Kegiatan Dana Kelurahan", 
        'dankel_keg': dankel_keg,
        "tombol" : "Tambah Sub Kegiatan Dana Kelurahan",
        "form": form, 
        "datas": data,
        "number":number,
        "sub":sub,
        
    }
    return render(request, lokasitemplate, context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan(request, number, sub):
    request.session['next'] = request.get_full_path()
    if request.method == "POST":
        form = Form_data(request.POST or None,  sub=sub)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect(tag_url, number=number, sub=sub)
    else:
        form = Form_data(sub=sub)
    context = {
        'form'  : form,
        'datas': data,
        'sub':sub,
    }
    return render(request, lokasitemplate, context)

@set_submenu_session
@menu_access_required('update')
def update(request, number, sub, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Model_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect(tag_url, number=number, sub=sub)
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data, "number": number, "sub": sub, "judul": "Update Kegiatan"}
    return render(request, lokasiupdate, context)

@set_submenu_session
@menu_access_required('delete')
def delete(request, number, sub, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url, number=number, sub=sub)


