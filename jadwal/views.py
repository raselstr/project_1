from django.shortcuts import redirect, render
from project.decorators import menu_access_required, set_submenu_session
from django.contrib import messages
from jadwal import models, tables, forms
from django.urls import reverse

Model = models.Jadwal
Tabel_jadwal = tables.JadwalTable
Form_jadwal = forms.JadwalForm

lokasitemplate = "list.html"
lokasiform = "form.html"

link_simpan = 'jadwal:simpan'
link_update = 'jadwal:update'
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
        form = Form_jadwal(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data berhasil disimpan')
            return redirect('list')
    else:
        form = Form_jadwal()
    return render(request, lokasiform, {'form': form})

def update(request, pk):
    pass

def delete(request,pk):
    pass
