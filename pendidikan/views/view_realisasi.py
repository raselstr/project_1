from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session

from django_tables2 import RequestConfig
from ..tables import RealisasiTable

import logging

from pendidikan.models import Rencanaposting, Rencana, Realisasi
from dausg.models import Subkegiatan


from pendidikan.forms import RealisasiFilterForm, RealisasiForm
from penerimaan.models import Penerimaan

tabel_realisasi = RealisasiTable

form_filter = RealisasiFilterForm
form_data = RealisasiForm

model_data = Rencanaposting
model_pagu = Rencana
model_dana = Subkegiatan
model_realisasi = Realisasi
model_penerimaan = Penerimaan

url_home = 'realisasi_pendidikan_home'
url_filter = 'realisasi_pendidikan_filter'
url_list = 'realisasi_pendidikan_list'
url_simpan = 'realisasi_pendidikan_simpan'
url_update = 'realisasi_pendidikan_update'
url_delete = 'realisasi_pendidikan_delete'
url_verif = 'realisasi_pendidikan_delete'

template_form = 'pendidikan/realisasi/form.html'
template_home = 'pendidikan/realisasi/home.html'
template_list = 'pendidikan/realisasi/list.html'
template_modal = 'pendidikan/realisasi/modal.html'
template_modal_verif = 'pendidikan/realisasi/modal_verif.html'

sesidana = 'dau-dukungan-bidang-pendidikan'

logger = logging.getLogger(__name__)

def modal(request, pk):
    data = get_object_or_404(model_realisasi, pk=pk)
    return render(request, template_modal_verif, {'data': data})

@set_submenu_session
@menu_access_required('update')
def verif(request, pk):
    realisasi = get_object_or_404(model_realisasi, pk=pk)
    verif = request.GET.get('verif')
    
    if verif == '1':
        realisasi.realisasi_verif = 1
    elif verif == '0':
        realisasi.realisasi_verif = 0
    
    realisasi.save()
    return redirect(url_list)


@set_submenu_session
@menu_access_required('delete')
def delete(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = model_realisasi.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except model_realisasi.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(url_list)

@set_submenu_session
@menu_access_required('update')
def update(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(model_realisasi, id=pk)
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
    initial_data = dict(
        realisasi_tahun=request.session.get('realisasi_tahun'),
        realisasi_dana=request.session.get('realisasi_dana'),
        realisasi_subopd=request.session.get('realisasi_subopd'),
        realisasi_tahap=request.session.get('realisasi_tahap'),
        jadwal = request.session.get('jadwal')
    )
    if request.method == 'POST':
        form = form_data(request.POST or None, initial_data=initial_data)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Simpan')
            return redirect(reverse(url_list))  # Ganti dengan URL redirect setelah berhasil
    else:
        form = form_data(initial=initial_data, initial_data=initial_data)

    context = {
        'form': form,
        'judul': 'Form Realisasi Kegiatan',
        'btntombol': 'Simpan',
        'link_url': reverse(url_list),
    }
    return render(request, template_form, context)


@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    realisasi_tahun=request.session.get('realisasi_tahun')
    realisasi_dana=request.session.get('realisasi_dana')
    realisasi_subopd=request.session.get('realisasi_subopd')
    realisasi_tahap=request.session.get('realisasi_tahap')
     # Buat filter query
    filters = Q()
    if realisasi_tahun:
        filters &= Q(realisasi_tahun=realisasi_tahun)
    if realisasi_dana:
        filters &= Q(realisasi_dana_id=realisasi_dana)
    if realisasi_tahap:
        filters &= Q(realisasi_tahap_id=realisasi_tahap)
    if realisasi_subopd not in [124]:
        filters &= Q(realisasi_subopd_id=realisasi_subopd)
    
    try:
        data = model_realisasi.objects.filter(filters)
    except model_realisasi.DoesNotExist:
        data = None
    
    table = tabel_realisasi(data)
    RequestConfig(request, paginate={"per_page": 25}).configure(table)

    context = {
        'judul': 'Daftar Realisasi DAU Bidang Pendidikan',
        'tombol': 'Tambah Realisasi',
        'kembali' : 'Kembali',
        'link_url': reverse(url_simpan),
        'link_url_kembali': reverse(url_home),
        'link_url_update': url_update,
        'link_url_delete': url_delete,
        'data' : data,
        'table':table,
    }
    return render(request, template_list, context)


def filter(request):
    if request.method == 'GET':
        logger.debug(f"Received GET data: {request.GET}")
        tahunposting = model_data.objects.values_list('posting_tahun', flat=True).distinct()
        sesisubopd = request.session.get('idsubopd')
        form = form_filter(request.GET or None, tahun=tahunposting, sesidana=sesidana, sesisubopd=sesisubopd)

        if form.is_valid():
            logger.debug(f"Form is valid: {form.cleaned_data}")
            request.session['realisasi_tahun'] = form.cleaned_data.get('realisasi_tahun')
            request.session['realisasi_dana'] = form.cleaned_data.get('realisasi_dana').id if form.cleaned_data.get('realisasi_dana') else None
            request.session['realisasi_subopd'] = form.cleaned_data.get('realisasi_subopd').id if form.cleaned_data.get('realisasi_subopd') else None
            request.session['realisasi_tahap'] = form.cleaned_data.get('realisasi_tahap').id if form.cleaned_data.get('realisasi_tahap') else None
            return redirect(url_list)
        else:
            logger.debug(f"Form errors: {form.errors}")
    else:
        form = form_filter()

    context = {
        'judul': 'Realisasi Kegiatan',
        'isi_modal': 'Ini adalah isi modal Realisasi Kegiatan.',
        'btntombol': 'Filter',
        'form': form,
        'link_url_filter': reverse(url_filter),
    }
    return render(request, template_modal, context)


@set_submenu_session
@menu_access_required('list')
def home(request):
    tahun = request.session.get('tahun')
    sesisubopd = request.session.get('idsubopd')
    
    try:
        dana = model_dana.objects.get(sub_slug=sesidana)
    except model_dana.DoesNotExist:
        dana = None
    
    if dana:
        pagu = model_pagu().get_pagu(tahun=tahun, opd=sesisubopd, dana=dana)
        rencana = model_data().get_total_rencana(tahun=tahun, opd=sesisubopd, dana=dana)
        penerimaan = model_penerimaan().totalpenerimaan(tahun=tahun, dana=dana)
        realisasi = model_realisasi().get_realisasi_total(tahun=tahun, opd=sesisubopd, dana=dana)
        persendana = model_realisasi().get_persendana(tahun=tahun, opd=sesisubopd, dana=dana)
        persenpagu = model_realisasi().get_persenpagu(tahun=tahun, opd=sesisubopd, dana=dana)
    else:
        pagu = 0
        rencana = 0
        penerimaan = 0
        realisasi = 0
        persendana = 0
        persenpagu = 0
        
        
    
    context = {
        'judul': 'Realisasi Kegiatan DAU Bidang Pendidikan',
        'tab1': 'Realisasi Kegiatan Tahun Berjalan',
        'datapagu': pagu,
        'datarencana' : rencana,
        'penerimaan' : penerimaan,
        'realisasi' : realisasi,
        'persendana' : persendana,
        'persenpagu' : persenpagu,
        
        'link_url': reverse(url_filter),
    }
    return render(request, template_home, context)
