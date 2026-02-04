from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session

from django_tables2 import RequestConfig
from ..tables import RealisasipuTablesisa,RencanapupostingsisaTable

from sipd.registry import SIPD_REGISTRY

import logging

from pu.models import Rencanapupostingsisa, Rencanapusisa, Realisasipusisa
from dausg.models import Subkegiatan


from pu.forms.sisa import RealisasipuFilterForm, RealisasipuForm
from penerimaan.models import Penerimaan

tabel_realisasi = RealisasipuTablesisa
tabel_rencana = RencanapupostingsisaTable

form_filter = RealisasipuFilterForm
form_data = RealisasipuForm

model_data = Rencanapupostingsisa
model_pagu = Rencanapusisa
model_dana = Subkegiatan
model_realisasi = Realisasipusisa
model_penerimaan = Penerimaan
model_rencana = Rencanapupostingsisa

url_home = 'realisasi_pu_home'
url_filter = 'realisasi_pu_filtersisa'
url_list = 'realisasi_pu_listsisa'
url_simpan = 'realisasi_pu_simpansisa'
url_update = 'realisasi_pusisa_update'
url_delete = 'realisasi_pusisa_delete'
url_verif = 'realisasi_pu_verifsisa'
url_sipd = 'data_sipd'

template_form = 'pu/realisasi/form.html'
template_home = 'pu/realisasi/home.html'
template_list = 'pu/realisasi/list.html'
template_sp2d = 'pu/realisasi/sp2d.html'
template_modal = 'pu/realisasi/modal.html'
template_modal_verif = 'pu/realisasi/modal_verif.html'

sesidana = 'sisa-dana-alokasi-umum-dukungan-bidang-pekerjaan-umum'

logger = logging.getLogger(__name__)

def safe_reverse(name, args=None, kwargs=None):
    try:
        if name and (args or kwargs):
            return reverse(name, args=args, kwargs=kwargs)
        elif name:
            return reverse(name)
    except Exception as e:
        print(f"⚠️ reverse gagal [{name}]:", e)
    return '#'


def modal(request, pk):
    data = get_object_or_404(model_realisasi, pk=pk)
    context = {
        'data': data,
        'verifurl' : url_verif
    }
    return render(request, template_modal_verif, context)

@set_submenu_session
@menu_access_required('update')
def verif(request, pk):
    realisasi = get_object_or_404(model_realisasi, pk=pk)
    verif_status = request.GET.get('verif')
    
    if verif_status not in ('0', '1'):
        return HttpResponseBadRequest("Parameter 'verif' tidak valid.")

    realisasi.realisasi_verif = int(verif_status)
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
def simpan(request, pk=None):
    request.session['next'] = request.get_full_path()
    try:
        rencana_posting = model_realisasi.objects.get(pk=pk)
    except model_realisasi.DoesNotExist:
        messages.error(request, "Data tidak ditemukan.")
        return redirect(reverse(url_list))
    
    initial_data = dict(
        realisasi_tahun=request.session.get('realisasi_tahun'),
        realisasi_dana=request.session.get('realisasi_dana'),
        realisasi_subopd=request.session.get('realisasi_subopd'),
        realisasi_tahap=request.session.get('realisasi_tahap'),
        jadwal = request.session.get('jadwal'),
        realisasi_rencanaposting=rencana_posting.id
    )
    if request.method == 'POST':
        form = form_data(request.POST or None, initial_data=initial_data)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Simpan')
            return redirect(reverse(url_sp2d,args=[pk]))  # Ganti dengan URL redirect setelah berhasil
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
def sp2d(request, pk=None):
    request.session['next'] = request.get_full_path()
    realisasi_tahun=request.session.get('realisasi_tahun')
    realisasi_dana=request.session.get('realisasi_dana')
    realisasi_subopd=request.session.get('realisasi_subopd')
    realisasi_tahap=request.session.get('realisasi_tahap')
     # Buat filter query
    filters = Q(realisasi_rencanaposting_id=pk)
    if realisasi_tahun:
        filters &= Q(realisasi_tahun=realisasi_tahun)
    if realisasi_dana:
        filters &= Q(realisasi_dana_id=realisasi_dana)
    if realisasi_tahap:
        if realisasi_tahap == 1:
            filters &= Q(realisasi_tahap_id=1)
        elif realisasi_tahap == 2:
            filters &= Q(realisasi_tahap_id__in=[1, 2])
        elif realisasi_tahap == 3:
            filters &= Q(realisasi_tahap_id__in=[1, 2, 3])
    if realisasi_subopd not in [124]:
        filters &= Q(realisasi_subopd_id=realisasi_subopd)
    
    filterkeg = Q(pk=pk)
    if realisasi_tahun:
        filterkeg &= Q(posting_tahun=realisasi_tahun)
    if realisasi_dana:
        filterkeg &= Q(posting_dana_id=realisasi_dana)
    # if realisasi_tahap:
    #     filterkeg &= Q(realisasi_tahap_id=realisasi_tahap)
    if realisasi_subopd not in [124]:
        filterkeg &= Q(posting_subopd_id=realisasi_subopd)
        
    try:
        data = model_realisasi.objects.filter(filters)
        datarencana = model_rencana.objects.filter(filterkeg)
    except (model_realisasi.DoesNotExist, model_rencana.DoesNotExist):
        data = None
        datarencana = None
    
    table = tabel_realisasi(data, request=request)
    tabelrencana = tabel_rencana(datarencana, request=request)
    
    SIPD_REGISTRY = 'realisasi_pu_sisa'
    
    context = {
        'judul': 'Daftar Realisasi DAU Bidang PU Sisa Tahun Lalu',
        'subjudul': 'Daftar Kegiatan Realisasi Sisa Tahun Lalu',
        'tombol': 'Tambah Realisasi',
        'kembali' : 'Kembali',
        'link_url': safe_reverse(url_simpan, args=[pk]) if pk else '#',
        'link_url_kembali': safe_reverse(url_list),
        'link_url_sipd': (safe_reverse(url_sipd, args=[SIPD_REGISTRY, pk]) if pk else '#'),
        'link_url_update': url_update,
        'link_url_delete': url_delete,
        'data' : data,
        'table':table,
        'datarencana' : datarencana,
        'tabelrencana':tabelrencana,
        'sipd':'SIPD',
    }
    return render(request, template_sp2d, context)

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
        filters &= Q(posting_tahun=realisasi_tahun)
    if realisasi_dana:
        filters &= Q(posting_dana_id=realisasi_dana)
    # if realisasi_tahap:
    #     filters &= Q(realisasi_tahap_id=realisasi_tahap)
    if realisasi_subopd not in [124]:
        filters &= Q(posting_subopd_id=realisasi_subopd)
    
    try:
        # data = model_realisasi.objects.filter(filters)
        datarencana = model_rencana.objects.filter(filters)
    except model_rencana.DoesNotExist:
        # data = None
        datarencana = None
    
    tabelrencana = tabel_rencana(datarencana, request=request, show_aksi=True)

    context = {
        'judul': 'Daftar Realisasi Sisa DAU Bidang Pekerjaan Umum Tahun Lalu',
        'tombol': 'Tambah Realisasi Sisa Tahun Lalu',
        'kembali' : 'Kembali',
        # 'link_url': reverse(url_simpan),
        'link_url_kembali': reverse(url_home),
        'link_url_update': url_update,
        'link_url_delete': url_delete,
        'datarencana' : datarencana,
        'tabelrencana':tabelrencana,
    }
    return render(request, template_list, context)


def filter(request):
    if request.method == 'GET':
        logger.debug(f"Received GET data: {request.GET}")
        tahunposting = request.session.get('tahun')
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
        'judul': 'Realisasi Kegiatan Sisa Tahun Lalu',
        'isi_modal': 'Ini adalah isi modal Realisasi Kegiatan.',
        'btntombol': 'Filter',
        'form': form,
        'link_url_filter': reverse(url_filter),
    }
    return render(request, template_modal, context)
