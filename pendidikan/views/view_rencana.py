from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session
import logging

from pendidikan.models import Rencana
from pendidikan.forms import RencanaFilterForm, RencanaForm

form_filter = RencanaFilterForm
form_data = RencanaForm

model_data = Rencana

url_home = 'rencana_pendidikan_home'
url_filter = 'rencana_pendidikan_filter'
url_list = 'rencana_pendidikan_list'
url_simpan = 'rencana_pendidikan_simpan'
url_update = 'rencana_pendidikan_update'
url_delete = 'rencana_pendidikan_delete'

template_form = 'pendidikan/form.html'
template_home = 'pendidikan/home.html'
template_list = 'pendidikan/list.html'
template_modal = 'pendidikan/modal.html'

sesidana = 'dau-dukungan-bidang-pendidikan'

logger = logging.getLogger(__name__)


@set_submenu_session
@menu_access_required('delete')
def delete(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(url_list)

@set_submenu_session
@menu_access_required('update')
def update(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(model_data, id=pk)
    if request.method == 'POST':
        form = form_data(request.POST or None, instance=data)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Update')
            return redirect(url_list)
    else:
        form = form_data(instance=data)
    context = {
        'form': form,
        'judul': 'Update Rencana Kegiatan',
        'btntombol' : 'Update',
        'link_url': reverse(url_list),
    }
    return render(request, template_form, context)

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
        initial_data = dict(rencana_tahun=request.session.get('rencana_tahun'),
                            rencana_dana=request.session.get('rencana_dana'),
                            rencana_subopd=request.session.get('rencana_subopd'))
        form = form_data(initial=initial_data)

    context = {
        'form': form,
        'judul': 'Form Rencana Kegiatan',
        'btntombol': 'Simpan',
        'link_url': reverse(url_list),
    }
    return render(request, template_form, context)


@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    
     # Buat filter query
    filters = Q()
    if tahunrealisasi:
        filters &= Q(realisasidankel_tahun=tahunrealisasi)
    if danarealisasi_id:
        filters &= Q(realisasidankel_dana_id=danarealisasi_id)
    if tahaprealisasi_id:
        filters &= Q(realisasidankel_tahap_id=tahaprealisasi_id)
    if subopdrealisasi_id != 124 and subopdrealisasi_id != 70 and subopdrealisasi_id != 67:
        filters &= Q(realisasidankel_subopd_id=subopdrealisasi_id)
    
    try:
        data = model_data.objects.filter(filters)
    except model_data.DoesNotExist:
        data = None

    context = {
        'judul': 'Daftar Kegiatan DAU Bidang Pendidikan',
        'tombol': 'Tambah Perencanaan',
        'kembali' : 'Kembali',
        'link_url': reverse(url_simpan),
        'link_url_kembali': reverse(url_home),
        'link_url_update': url_update,
        'link_url_delete': url_delete,
        'data' : data,
    }
    return render(request, template_list, context)


def filter(request):
    if request.method == 'GET':
        logger.debug(f"Received GET data: {request.GET}")
        tahunrencana = model_data.objects.values_list('rencana_tahun', flat=True).distinct()
        sesisubopd = request.session.get('idsubopd')
        form = form_filter(request.GET or None, tahun=tahunrencana, sesidana=sesidana, sesisubopd=sesisubopd)

        if form.is_valid():
            logger.debug(f"Form is valid: {form.cleaned_data}")
            request.session['rencana_tahun'] = form.cleaned_data.get('rencana_tahun')
            request.session['rencana_dana'] = form.cleaned_data.get('rencana_dana').id if form.cleaned_data.get(
                'rencana_dana') else None
            request.session['rencana_subopd'] = form.cleaned_data.get('rencana_subopd').id if form.cleaned_data.get(
                'rencana_subopd') else None
            return redirect(url_list)
        else:
            logger.debug(f"Form errors: {form.errors}")
    else:
        form = form_filter()

    context = {
        'judul': 'Rencana Kegiatan',
        'isi_modal': 'Ini adalah isi modal Rencana Kegiatan.',
        'btntombol': 'Filter',
        'form': form,
        'link_url': reverse(url_filter),
    }
    return render(request, template_modal, context)


@set_submenu_session
@menu_access_required('list')
def home(request):
    context = {
        'judul': 'Rencana Kegiatan DAU Bidang Pendidikan',
        'tab1': 'Rencana Kegiatan Tahun Berjalan',
        'link_url': reverse(url_filter),
    }
    return render(request, template_home, context)
