from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from dana.utils import datasubrinc
from project.decorators import menu_access_required, set_submenu_session


from ...models import DausgpuProg
from ...forms.form_dausgpu import DausgpuProgForm

Form_data = DausgpuProgForm
Nilai_data = DausgpuProg
tag_url = 'list_dausgpuprog'

@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    data = (Nilai_data.objects
            .select_related('dausgpu_dana', 'dausgpu_subrinc')
            .prefetch_related('dausgpukegs__dausgpusubs')
            .all())
    form = Form_data()
    context = {
        "judul": "Daftar Program DAU SG Pekerjaan Umum", 
        "tombol" : "Tambah Program DAUSG Pekerjaan Umum",
        "form": form, 
        "datas": data
    }
    return render(request, "dausgpu/dausgpuprog/dausgpuprog_list.html", context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan(request):
    request.session['next'] = request.get_full_path()
    data = Nilai_data.objects.all()
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
        'datas': data
    }
    return render(request, "dausgpu/dausgpuprog/dausgpuprog_list.html", context)

@set_submenu_session
@menu_access_required('update')
def update(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(Nilai_data, id=pk)
    formupdate = Form_data(request.POST or None, instance=data)
    if request.method == "POST":
        if formupdate.is_valid():
            formupdate.save()
            messages.success(request, "Data Berhasil diupdate")
            return redirect(tag_url)
    else:
        formupdate = Form_data(instance=data)

    context = {"form": formupdate, "datas": data, "judul": "Update dausgpuprog"}
    return render(request, "dausgpu/dausgpuprog/dausgpuprog_edit.html", context)

@set_submenu_session
@menu_access_required('delete')
def delete(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Nilai_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Nilai_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url)

def load(request):
    kwargs = {
        'nama_app'  : 'dana',
        'model_name' : 'Subrinc',
        'fieldsmodel' : ['subrinc_dana'],
        'template_name' : 'load/load_subrinckeg.html',
        'fieldget' : 'dausgpu_dana',
        
    }
    return datasubrinc(request, **kwargs)

    