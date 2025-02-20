from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError
from project.decorators import menu_access_required, set_submenu_session
from django.contrib import messages
from jadwal import models, tables, forms
from django.urls import reverse

Model = models.Jadwal
Tabel_jadwal = tables.JadwalTable
Form_jadwal = forms.JadwalForm

lokasitemplate = "list.html"
lokasiform = "form.html"

link_list = 'jadwal:list'
link_simpan = 'jadwal:simpan'
link_update = 'jadwal:edit'
link_delete = 'jadwal:delete'

@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    tahun = request.session.get('tahun')
    try:
        data = Model.objects.filter(jadwal_tahun=tahun)
    except Model.DoesNotExist:
        data = None
    
    table = Tabel_jadwal(data, request=request)

    context = {
        "judul": "Jadwal Posting Kegiatan",
        "tombol" : "Tambah",
        "table": table,
        "link_simpan": reverse(link_simpan),
    }
    return render(request, lokasitemplate, context) 

@set_submenu_session
@menu_access_required('simpan')
def simpan(request):
    if request.method == 'POST':
        form = Form_jadwal(request.POST or None, tahun=request.session.get('tahun'))
        if form.is_valid():
            form.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect(link_list)
    else:
        form = Form_jadwal(tahun=request.session.get('tahun'))
    
    context = {
        "judul": "Jadwal Posting Kegiatan",
        "btntombol" : "Simpan",
        "form": form,
        "link_simpan": reverse(link_simpan),
    }
    return render(request, lokasiform, context)

@set_submenu_session
@menu_access_required('update')
def update(request, pk):
    instance = Model.objects.get(pk=pk)
    if request.method == 'POST':
        form = Form_jadwal(request.POST or None, instance=instance, tahun=request.session.get('tahun'))
        if form.is_valid():
            form.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect(link_list)
    else:
        form = Form_jadwal(instance=instance, tahun=request.session.get('tahun'))
    
    context = {
        "judul": "Ubah Posting Kegiatan",
        "btntombol" : "Simpan",
        "form": form,
        "link_simpan": reverse(link_update, kwargs={'pk': pk}),
    }
    return render(request, lokasiform, context)

@set_submenu_session
@menu_access_required('delete')
def delete(request, pk):
    try:
        data = Model.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(link_list)
