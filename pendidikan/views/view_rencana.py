from django.shortcuts import render, get_object_or_404, redirect
from project.decorators import menu_access_required, set_submenu_session

from pendidikan.models import Rencana
from pendidikan.forms import RencanaForm

form_filter = RencanaForm

rencana_home = 'pendidikan/rencana/home.html'
rencana_list = 'pendidikan/rencana/list.html'
rencana_modal = 'pendidikan/rencana/modal.html'



@set_submenu_session
@menu_access_required('list')
def list(request):
    context = {
        'judul' : 'Daftar Kegiatan DAU Bidang Pendidikan',
        'tombol' : 'Tambah Perencanaan',
    }
    return render(request, rencana_list, context)

def filter(request):
    if request.method == 'GET':
        form = form_filter(request.GET)
        if form.is_valid():
            request.session['rencana_tahun'] = form.cleaned_data.get('rencana_tahun')
            request.session['rencana_dana'] = form.cleaned_data.get('rencana_dana').id if form.cleaned_data.get('rencana_dana') else None
            request.session['rencana_subopd'] = form.cleaned_data.get('rencana_subopd').id if form.cleaned_data.get('rencana_subopd') else None
            return redirect(rencana_list)
    else:
        form = form_filter()
    
    context = {
        'judul': 'Rencana Kegiatan',
        'isi_modal': 'Ini adalah isi modal Rencana Kegiatan.',
        'form':form,
    }
    return render(request, rencana_modal, context)

@set_submenu_session
@menu_access_required('list')
def home(request):
    context = {
        'judul' : 'Rencana Kegiatan DAU Bidang Pendidikan',
        'tab1'      : 'Rencana Kegiatan Tahun Berjalan',
    }
    return render(request, rencana_home, context)