from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session

from django_tables2 import RequestConfig
from ..tables import RealisasiTablesisa

import logging

from pendidikan.models import Rencanapostingsisa, Rencanasisa, Realisasisisa
from dausg.models import Subkegiatan


from pendidikan.forms.form_sisa import RealisasiFilterForm, RealisasiForm
from penerimaan.models import Penerimaan

tabel_realisasi = RealisasiTablesisa

form_filter = RealisasiFilterForm
form_data = RealisasiForm

model_data = Rencanapostingsisa
model_pagu = Rencanasisa
model_dana = Subkegiatan
model_realisasi = Realisasisisa
model_penerimaan = Penerimaan

url_home = 'realisasi_pendidikan_home'
url_filter = 'realisasi_pendidikan_filtersisa'
url_list = 'realisasi_pendidikan_listsisa'
url_simpan = 'realisasi_pendidikan_simpansisa'
url_update = 'realisasi_pendidikan_updatesisa'
url_delete = 'realisasi_pendidikan_deletesisa'
url_verif = 'realisasi_pendidikan_verifsisa'

template_form = 'pendidikan/realisasi/form.html'
template_home = 'pendidikan/realisasi/home.html'
template_list = 'pendidikan/realisasi/list.html'
template_modal = 'pendidikan/realisasi/modal.html'
template_modal_verif = 'pendidikan/realisasi/modal_verif.html'

sesidana = 'sisa-dana-alokasi-umum-dukungan-bidang-pendidikan'

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
        'judul': 'Form Realisasi Kegiatan Tahun Lalu',
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
    
    table = tabel_realisasi(data, request=request)
    # RequestConfig(request, paginate={"per_page": 25}).configure(table)

    context = {
        'judul': 'Daftar Realisasi DAU Bidang Pendidikan Tahun Lalu',
        'tombol': 'Tambah Realisasi Tahun Lalu',
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
        'judul': 'Realisasi Kegiatan Tahun Lalu',
        'isi_modal': 'Ini adalah isi modal Realisasi Kegiatan.',
        'btntombol': 'Filter',
        'form': form,
        'link_url_filter': reverse(url_filter),
    }
    return render(request, template_modal, context)

