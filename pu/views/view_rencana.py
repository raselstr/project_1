from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session
import logging

from pu.models import Rencanapu
from pu.forms import RencanapuFilterForm, RencanapuForm
from dausg.models import Subkegiatan

form_filter = RencanapuFilterForm
form_data = RencanapuForm

model_data = Rencanapu
model_pagu = Subkegiatan

url_home = 'rencana_pu_home'
url_filter = 'rencana_pu_filter'
url_list = 'rencana_pu_list'
url_simpan = 'rencana_pu_simpan'
url_update = 'rencana_pu_update'
url_delete = 'rencana_pu_delete'

template_form = 'pu/rencana/form.html'
template_home = 'pu/rencana/home.html'
template_list = 'pu/rencana/list.html'
template_modal = 'pu/rencana/modal.html'

sesidana = 'dau-dukungan-bidang-pekerjaan-umum'

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
            try:
                form.save()
                messages.success(request, 'Data Berhasil Update')
                return redirect(url_list)
            except ValidationError as e:
                # Menambahkan pesan error global ke form
                form.add_error(None, e.message)
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
        rencana_tahun=request.session.get('rencana_tahun'),
        rencana_dana=request.session.get('rencana_dana'),
        rencana_subopd=request.session.get('rencana_subopd')
    )
    if request.method == 'POST':
        form = form_data(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Simpan')
            return redirect(reverse(url_list))  # Ganti dengan URL redirect setelah berhasil
    else:
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
        'judul': 'Daftar Kegiatan DAU Bidang Pekerjaan  Umum',
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
    except model_pagu.DoesNotExist:
        dana = None
    
    if dana:
        pagu = model_data().get_pagu(tahun=tahun, opd=sesisubopd, dana=dana)
        rencana = model_data().get_total_rencana(tahun=tahun, opd=sesisubopd, dana=dana)
        sisa = model_data().get_sisa(tahun=tahun, opd=sesisubopd, dana=dana)
    else:
        pagu = 0
        rencana = 0
        sisa = 0
    
    context = {
        'judul': 'Rencana Kegiatan DAU Bidang Pekerjaan  Umum',
        'tab1': 'Rencana Kegiatan Tahun Berjalan',
        'datapagu': pagu,
        'datarencana' : rencana,
        'datasisa' : sisa,
        
        'link_url': reverse(url_filter),
    }
    return render(request, template_home, context)
