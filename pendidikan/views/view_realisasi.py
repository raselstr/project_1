from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session

from django_tables2 import RequestConfig
from ..tables import RealisasiTable, RencanapendidikanpostingTable

import logging

from pendidikan.models import Rencanaposting, Rencana, Realisasi, Rencanasisa, Rencanapostingsisa, Realisasisisa
from dausg.models import Subkegiatan


from pendidikan.forms.form_pendidikan import RealisasiFilterForm, RealisasiForm
from penerimaan.models import Penerimaan

tabel_realisasi = RealisasiTable
tabel_rencana = RencanapendidikanpostingTable

form_filter = RealisasiFilterForm
form_data = RealisasiForm

model_data = Rencanaposting
model_pagu = Rencana
model_datasisa = Rencanapostingsisa
model_pagusisa = Rencanasisa
model_dana = Subkegiatan
model_realisasi = Realisasi
model_realisasisisa = Realisasisisa
model_penerimaan = Penerimaan

url_home = 'realisasi_pendidikan_home'
url_filter = 'realisasi_pendidikan_filter'
url_filtersisa = 'realisasi_pendidikan_filtersisa'
url_list = 'realisasi_pendidikan_list'
url_simpan = 'realisasi_pendidikan_simpan'
url_update = 'realisasi_pendidikan_update'
url_delete = 'realisasi_pendidikan_delete'
url_verif = 'realisasi_pendidikan_verif'
url_sp2d = 'realisasi_pendidikan_sp2d'

template_form = 'pendidikan/realisasi/form.html'
template_home = 'pendidikan/realisasi/home.html'
template_list = 'pendidikan/realisasi/list.html'
template_sp2d = 'pendidikan/realisasi/sp2d.html'
template_modal = 'pendidikan/realisasi/modal.html'
template_modal_verif = 'pendidikan/realisasi/modal_verif.html'

sesidana = 'dau-dukungan-bidang-pendidikan'
sesidanasisa = 'sisa-dana-alokasi-umum-dukungan-bidang-pendidikan'

logger = logging.getLogger(__name__)

def modal(request, pk):
    data = get_object_or_404(model_realisasi, pk=pk)
    context  = {
        'data':data,
        'verifurl' : url_verif,
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
        rencana_posting = model_data.objects.get(pk=pk)
    except model_data.DoesNotExist:
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
        'link_url': reverse(url_sp2d,args=[pk]),
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
        datarencana = model_data.objects.filter(filterkeg)
    except (model_realisasi.DoesNotExist, model_data.DoesNotExist):
        data = None
        datarencana = None
    
    table = tabel_realisasi(data, request=request)
    tabelrencana = tabel_rencana(datarencana, request=request)
    
    
    context = {
        'judul': 'Daftar Realisasi DAU Bidang Pendidikan',
        'subjudul': 'Daftar Kegiatan',
        'tombol': 'Tambah Realisasi',
        'kembali' : 'Kembali',
        'link_url': reverse(url_simpan, args=[pk]),
        'link_url_kembali': reverse(url_list),
        'link_url_update': url_update,
        'link_url_delete': url_delete,
        'data' : data,
        'table':table,
        'datarencana' : datarencana,
        'tabelrencana':tabelrencana,
    }
    return render(request, template_sp2d, context)

@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    realisasi_tahun=request.session.get('realisasi_tahun')
    realisasi_dana=request.session.get('realisasi_dana')
    realisasi_subopd=request.session.get('realisasi_subopd')
     # Buat filter query
    filters = Q()
    if realisasi_tahun:
        filters &= Q(posting_tahun=realisasi_tahun)
    if realisasi_dana:
        filters &= Q(posting_dana_id=realisasi_dana)
    if realisasi_subopd not in [124]:
        filters &= Q(posting_subopd_id=realisasi_subopd)
    
    try:
        data = model_data.objects.filter(filters)
    except model_data.DoesNotExist:
        data = None
    
    table = tabel_rencana(data, show_aksi=True)
    table.paginate=False

    context = {
        'judul': 'Daftar Realisasi DAU Bidang Pendidikan',
        'tombol': 'Tambah Realisasi',
        'kembali' : 'Kembali',
        'link_url_kembali': reverse(url_home),
        'link_url_update': url_update,
        'link_url_delete': url_delete,
        'data' : data,
        'table': table,
        
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
        form = form_filter(request.GET or None, tahun=tahunposting, sesidana=sesidana, sesisubopd=sesisubopd)

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
    jadwal = request.session.get('jadwal')
    
    try:
        dana = model_dana.objects.get(sub_slug=sesidana)
        danasisa = model_dana.objects.get(sub_slug=sesidanasisa)
    except model_dana.DoesNotExist:
        dana = None
        danasisa = None
    
    if dana:
        pagu = model_pagu().get_pagu(tahun=tahun, opd=sesisubopd, dana=dana)
        rencana = model_data().get_total_rencana(tahun=tahun, opd=sesisubopd, dana=dana, posting=jadwal)
        penerimaan = model_penerimaan().totalpenerimaan(tahun=tahun, dana=dana)
        realisasi = model_realisasi().get_realisasi_total(tahun=tahun, opd=sesisubopd, dana=dana)
        persendana = model_realisasi().get_persendana(tahun=tahun, opd=sesisubopd, dana=dana)
        persenpagu = model_realisasi().get_persenpagu(tahun=tahun, opd=sesisubopd, dana=dana, posting=jadwal)
        
        rencanasisa = model_datasisa().get_total_rencana(tahun=tahun, opd=sesisubopd, dana=danasisa, posting=jadwal)
        penerimaansisa = model_penerimaan().totalpenerimaan(tahun=tahun, dana=danasisa)
        realisasisisa = model_realisasisisa().get_realisasi_total(tahun=tahun, opd=sesisubopd, dana=danasisa)
        persendanasisa = model_realisasisisa().get_persendana(tahun=tahun, opd=sesisubopd, dana=danasisa)
        persenpagusisa = model_realisasisisa().get_persenpagu(tahun=tahun, opd=sesisubopd, dana=danasisa, posting=jadwal)
    else:
        pagu = 0
        rencana = 0
        penerimaan = 0
        realisasi = 0
        persendana = 0
        persenpagu = 0
        
        rencanasisa = 0
        penerimaansisa = 0
        realisasisisa = 0
        persendanasisa = 0
        persenpagusisa = 0
        
        
    
    context = {
        'judul': 'Realisasi Kegiatan DAU Bidang Pendidikan',
        'tab1': 'Realisasi Kegiatan Tahun Berjalan',
        'tab2': 'Realisasi Kegiatan Tahun Lalu',
        'datapagu': pagu,
        
        'datarencana' : rencana,
        'penerimaan' : penerimaan,
        
        'realisasi' : realisasi,
        'persendana' : persendana,
        'persenpagu' : persenpagu,
        'penerimaansisa' : penerimaansisa,
        'rencanasisa' : rencanasisa,
        
        'realisasisisa' : realisasisisa,
        'persendanasisa' : persendanasisa,
        'persenpagusisa' : persenpagusisa,
        
        'link_url': reverse(url_filter),
        'link_urlsisa': reverse(url_filtersisa),
    }
    return render(request, template_home, context)
