from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from dana.utils import datasubrinc
from project.decorators import menu_access_required, set_submenu_session


from ...models import DausgkesehatanKeg, DausgkesehatanProg
from ...forms.form_dausgkesehatan import DausgkesehatanKegForm

Form_data = DausgkesehatanKegForm
Model_data = DausgkesehatanKeg
Model_induk = DausgkesehatanProg
lokasitemplate = 'dausgkesehatan/dausgkesehatankeg/dausgkesehatankeg_list.html'
lokasiupdate = 'dausgkesehatan/dausgkesehatankeg/dausgkesehatankeg_edit.html'
tag_url = 'list_dausgkesehatankeg'
lokasiload = 'load/load_subrinckeg.html'

@set_submenu_session
@menu_access_required('list')
def list(request, number):
    request.session['next'] = request.get_full_path()
    
    dankel_prog = get_object_or_404(Model_induk, id=number)
    data = dankel_prog.dausgkesehatankegs.prefetch_related('dausgkesehatansubs').all()
    # data = Model_data.objects.all()
    form = Form_data(request.POST or None, number=number)
    
    context = {
        "judul": "Daftar Kegiatan DAU SG kesehatan", 
        'dankel_prog': dankel_prog,
        "tombol" : "Tambah Kegiatan DAUSG kesehatan",
        "form": form, 
        "datas": data,
        "number":number,
        
    }
    return render(request, lokasitemplate, context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan(request, number):
    request.session['next'] = request.get_full_path()
    if request.method == "POST":
        form = Form_data(request.POST or None, number=number)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil disimpan')
            return redirect(tag_url, number=number)
    else:
        form = Form_data(number=number)
    context = {
        'form'  : form,
        'number' : number,
    }
    return render(request, lokasitemplate, context)

@set_submenu_session
@menu_access_required('update')
def update(request, number, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Model_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect(tag_url, number=number)
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data, "number": number, "judul": "Update Kegiatan"}
    return render(request, lokasiupdate, context)

@set_submenu_session
@menu_access_required('delete')
def delete(request, number, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url, number=number)


