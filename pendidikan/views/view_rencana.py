from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from project.decorators import menu_access_required, set_submenu_session
import logging

from pendidikan.models import Rencana
from pendidikan.forms import RencanaForm

form_filter = RencanaForm

url_list = 'rencana_pendidikan_daftar'

rencana_home = 'pendidikan/rencana/home.html'
rencana_list = 'pendidikan/rencana/list.html'
rencana_modal = 'pendidikan/rencana/modal.html'

logger = logging.getLogger(__name__)

@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    rencana_tahun = request.session.get('rencana_tahun')
    rencana_dana = request.session.get('rencana_dana')
    rencana_subopd = request.session.get('rencana_subopd')
    context = {
        'judul' : 'Daftar Kegiatan DAU Bidang Pendidikan',
        'tombol' : 'Tambah Perencanaan',
    }
    return render(request, rencana_list, context)

def filter(request):
    if request.method == 'GET':
        form = form_filter(request.GET or None)
        logger.debug(f"Received GET data: {request.GET}")
        
        if form.is_valid():
            logger.debug(f"Form is valid: {form.cleaned_data}")
            request.session['rencana_tahun'] = form.cleaned_data.get('rencana_tahun')
            request.session['rencana_dana'] = form.cleaned_data.get('rencana_dana').id if form.cleaned_data.get('rencana_dana') else None
            request.session['rencana_subopd'] = form.cleaned_data.get('rencana_subopd').id if form.cleaned_data.get('rencana_subopd') else None
            return redirect(url_list)
        else:
            logger.debug(f"Form errors: {form.errors}")
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