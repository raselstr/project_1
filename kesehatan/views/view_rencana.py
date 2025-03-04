from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session
import logging
from datetime import datetime

from kesehatan.models import Rencanakesehatan, Rencanakesehatansisa
from kesehatan.forms.forms import RencanakesehatanFilterForm, RencanakesehatanForm
from dausg.models import Subkegiatan
from dausg.models import DausgkesehatanSub
from kesehatan.tables import RencanaTable
from opd.models import Pejabat, Subopd

form_filter = RencanakesehatanFilterForm
form_data = RencanakesehatanForm

tabel_rencana = RencanaTable

model_data = Rencanakesehatan
model_datasisa = Rencanakesehatansisa
model_pagu = Subkegiatan
model_kegiatan = DausgkesehatanSub
model_pejabat = Pejabat
model_subopd = Subopd

url_home = 'rencana_kesehatan_home'
url_filter = 'rencana_kesehatan_filter'
url_filtersisa = 'rencana_kesehatan_filtersisa'
url_list = 'rencana_kesehatan_list'
url_simpan = 'rencana_kesehatan_simpan'
url_update = 'rencana_kesehatan_update'
url_delete = 'rencana_kesehatan_delete'
url_cetak = 'rencana_kesehatan_cetak'

template_form = 'kesehatan/rencana/form.html'
template_home = 'kesehatan/rencana/home.html'
template_list = 'kesehatan/rencana/list.html'
template_modal = 'kesehatan/rencana/modal.html'
template_pdf = 'kesehatan/rencana/pdf.html'

sesidana = 'dau-dukungan-bidang-kesehatan'
sesidanasisa = 'sisa-dana-alokasi-umum-dukungan-bidang-kesehatan'

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
    tahun = data.rencana_tahun
    if request.method == 'POST':
        form = form_data(request.POST or None, instance=data, tahun=tahun)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Data Berhasil Update')
                return redirect(url_list)
            except ValidationError as e:
                # Menambahkan pesan error global ke form
                form.add_error(None, e.message)
    else:
        form = form_data(instance=data, tahun=tahun)
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
        rencana_tahun=request.session.get('rencana_tahun'),
        rencana_dana=request.session.get('rencana_dana'),
        rencana_subopd=request.session.get('rencana_subopd')
    )
    tahun = request.session.get('tahun')
    if request.method == 'POST':
        form = form_data(request.POST or None, tahun=tahun)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Simpan')
            return redirect(reverse(url_list))  # Ganti dengan URL redirect setelah berhasil
    else:
        form = form_data(initial=initial_data, tahun=tahun)

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
    rencana_tahun=request.session.get('rencana_tahun')
    rencana_dana=request.session.get('rencana_dana')
    rencana_subopd=request.session.get('rencana_subopd')
     # Buat filter query
    filters = Q()
    if rencana_tahun:
        filters &= Q(rencana_tahun=rencana_tahun)
    if rencana_dana:
        filters &= Q(rencana_dana_id=rencana_dana)
    if rencana_subopd is not None and rencana_subopd not in [124]:
        filters &= Q(rencana_subopd_id=rencana_subopd)
    
    try:
        data = model_data.objects.filter(filters)
    except model_data.DoesNotExist:
        data = None

    context = {
        'judul': 'Daftar Kegiatan DAU Bidang Kesehatan',
        'tombol': 'Tambah Perencanaan',
        'kembali' : 'Kembali',
        'link_url': reverse(url_simpan),
        'link_url_kembali': reverse(url_home),
        'link_url_update': url_update,
        'link_url_delete': url_delete,
        'link_url_cetak': reverse(url_cetak),
        'data' : data,
    }
    return render(request, template_list, context)


def filter(request):
    if request.method == 'GET':
        logger.debug(f"Received GET data: {request.GET}")
        tahunrencana = request.session.get('tahun')
        sesisubopd = request.session.get('idsubopd')
        form = form_filter(request.GET or None, tahun=tahunrencana, sesidana=sesidana, sesisubopd=sesisubopd)

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
        'btntombol': 'Filter',
        'form': form,
        'link_url': reverse(url_filter),
    }
    return render(request, template_modal, context)


@set_submenu_session
@menu_access_required('list')
def home(request):
    tahun = request.session.get('tahun')
    sesisubopd = request.session.get('idsubopd')
    
    try:
        dana = model_pagu.objects.get(sub_slug=sesidana)
        danasisa = model_pagu.objects.get(sub_slug=sesidanasisa)
    except model_pagu.DoesNotExist:
        dana = None
        danasisa = None
    
    if dana:
        pagu = model_data().get_pagu(tahun=tahun, opd=sesisubopd, dana=dana)
        rencana = model_data().get_total_rencana(tahun=tahun, opd=sesisubopd, dana=dana)
        sisa = model_data().get_sisa(tahun=tahun, opd=sesisubopd, dana=dana)
        
        pagusisa = model_datasisa().get_pagu(tahun=tahun, opd=sesisubopd, dana=danasisa)
        rencanasisa = model_datasisa().get_total_rencana(tahun=tahun, opd=sesisubopd, dana=danasisa)
        nilaisisa = pagusisa-rencanasisa
        
    else:
        pagu = 0
        rencana = 0
        sisa = 0
        pagusisa = 0
        rencanasisa = 0
        nilaisisa = 0
    
    context = {
        'judul': 'Rencana Kegiatan DAU Bidang Kesehatan',
        'tab1': 'Rencana Kegiatan Tahun Berjalan',
        'tab2': 'Rencana Kegiatan Sisa Tahun Lalu',
        'datapagu': pagu,
        'datarencana' : rencana,
        'datasisa' : sisa,
        'pagusisa': pagusisa,
        'rencanasisa' : rencanasisa,
        'nilaisisa' : nilaisisa,
        
        
        'link_url': reverse(url_filter),
        'link_urlsisa': reverse(url_filtersisa),
    }
    return render(request, template_home, context)

@set_submenu_session
@menu_access_required('list')
def cetak(request):
    request.session['next'] = request.get_full_path()
    rencana_tahun=request.session.get('rencana_tahun')
    rencana_dana=request.session.get('rencana_dana')
    rencana_subopd=request.session.get('rencana_subopd')
     # Buat filter query
    filters = Q()
    if rencana_tahun:
        filters &= Q(rencana_tahun=rencana_tahun)
    if rencana_dana:
        filters &= Q(rencana_dana_id=rencana_dana)
    if rencana_subopd is not None and rencana_subopd not in [124]:
        filters &= Q(rencana_subopd_id=rencana_subopd)
    
    try:
        data = model_data.objects.filter(filters)
    except model_data.DoesNotExist:
        data = None
        
   
    if rencana_subopd:
        ttd = model_pejabat.objects.filter(pejabat_sub=rencana_subopd)
    else:
        ttd = None
        
    tabel = tabel_rencana(data)
    
    subopd_laporan = model_subopd.objects.filter(id=rencana_subopd).first().sub_nama
    dana_laporan = model_pagu.objects.filter(id=rencana_dana).first().sub_nama

    context = {
        'judul': 'Daftar Kegiatan DAU Bidang Kesehatan',
        'tombol': 'Tambah Perencanaan',
        'kembali' : 'Kembali',
        'link_url': reverse(url_simpan),
        'link_url_kembali': reverse(url_home),
        'link_url_update': url_update,
        'link_url_delete': url_delete,
        'data' : data,
        'tabel' : tabel,
        'ttd' : ttd,
        'rencana_tahun' : rencana_tahun,
        'rencana_dana' : dana_laporan,
        'rencana_subopd' : subopd_laporan,
    }
    return render(request, template_pdf, context)
