from django.shortcuts import render
from project.decorators import menu_access_required, set_submenu_session
from jadwal.models import Jadwal
from jadwal.tables import JadwalTable as tabel_jadwal



Model = Jadwal
lokasitemplate = "list.html"

@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    tahun = request.session.get('tahun')
    try:
        data = Model.objects.filter(jadwal_tahun=tahun)
    except Model.DoesNotExist:
        data = None
    
    table = tabel_jadwal(data, request=request)

    context = {
        "judul": "Jadwal Posting Kegiatan",
        "tombol" : "Tambah",
        "table": table,
    }
    return render(request, lokasitemplate, context) 

def simpan(request):
    pass

def update(request, pk):
    pass

def delete(request,pk):
    pass
