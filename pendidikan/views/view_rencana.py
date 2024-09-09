from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session
import logging

from pendidikan.models import Rencana
from pendidikan.forms import RencanaFilterForm, RencanaForm

form_filter = RencanaFilterForm
form_data = RencanaForm

url_filter = 'rencana_pendidikan_filter'
url_list = 'rencana_pendidikan_list'
url_simpan = 'rencana_pendidikan_simpan'
url_update = 'rencana_pendidikan_update'
url_delete = 'rencana_pendidikan_delete'

template_form = 'pendidikan/form.html'
template_home = 'pendidikan/home.html'
template_list = 'pendidikan/list.html'
template_modal = 'pendidikan/modal.html'

logger = logging.getLogger(__name__)

# @set_submenu_session
# @menu_access_required('delete')
# def delete(request, pk):
#     sesiidopd = session_data.get('idsubopd')
#     sesitahun = session_data.get('sesitahun')
#     request.session['next'] = request.get_full_path()
#     try:
#         data = Model_data.objects.get(id=pk)
#         data.delete()
#         messages.warning(request, "Data Berhasil dihapus")
#     except Model_data.DoesNotExist:
#         messages.error(request,"Dana tidak ditemukan")
#     except ValidationError as e:
#         messages.error(request, str(e))
#     return redirect(tag_url)

# @set_submenu_session
# @menu_access_required('update')
# def update(request, pk):
#     session_data = get_from_sessions(request)
#     sesiidopd = session_data.get('idsubopd')
#     sesitahun = session_data.get('sesitahun')
#     request.session['next'] = request.get_full_path()
#     data = get_object_or_404(Model_data, id=pk)

#     if request.method == 'POST':
#         form = Form_data(request.POST or None, instance=data, sesiidopd=sesiidopd, sesidana=sesidana)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Data Berhasil Update')
#             return redirect(tag_url)
#     else:
#         form = Form_data(instance=data, sesiidopd=sesiidopd, sesidana=sesidana)
#     context = {
#         'form': form,
#         'judul': 'Update Rencana Kegiatan',
#         'btntombol' : 'Update',
#     }
#     return render(request, template, context)

@set_submenu_session
@menu_access_required('simpan')
def simpan(request):
    request.session['next'] = request.get_full_path()
    
    if request.method == 'POST':
        form = form_data(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Simpan')
            return redirect(url_list)  # Ganti dengan URL redirect setelah berhasil
    else:
        initial_data = {
            'rencana_tahun' : request.session.get('rencana_tahun'),
            'rencana_dana' : request.session.get('rencana_dana'),
            'rencana_subopd' : request.session.get('rencana_subopd')
        }
        form = form_data(initial=initial_data)
        
    context = {
        'form': form,
        'judul': 'Form Rencana Kegiatan',
        'btntombol' : 'Simpan',
        'link_url' : reverse(url_list),
    }
    return render(request, template_form, context)

@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    
    context = {
        'judul' : 'Daftar Kegiatan DAU Bidang Pendidikan',
        'tombol' : 'Tambah Perencanaan',
        'link_url' : reverse(url_simpan)
    }
    return render(request, template_list, context)

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
        'btntombol' : 'Filter',
        'form':form,
        'link_url' : reverse(url_filter),
    }
    return render(request, template_modal, context)

@set_submenu_session
@menu_access_required('list')
def home(request):
    context = {
        'judul' : 'Rencana Kegiatan DAU Bidang Pendidikan',
        'tab1'      : 'Rencana Kegiatan Tahun Berjalan',
        'link_url' : reverse(url_filter),
    }
    return render(request, template_home, context)