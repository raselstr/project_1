from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session
import logging

from kesehatan.models import Rencanakesehatansisa
from kesehatan.forms.formssisa import RencanakesehatanFilterForm, RencanakesehatanForm
from dausg.models import Subkegiatan

form_filter = RencanakesehatanFilterForm
form_data = RencanakesehatanForm

model_data = Rencanakesehatansisa
model_pagu = Subkegiatan

url_home = 'rencana_kesehatan_home'
url_filter = 'rencana_kesehatan_filtersisa'
url_list = 'rencana_kesehatan_listsisa'
url_simpan = 'rencana_kesehatan_simpansisa'
url_update = 'rencana_kesehatan_updatesisa'
url_delete = 'rencana_kesehatan_deletesisa'

template_form = 'kesehatan/rencana/form.html'
template_home = 'kesehatan/rencana/home.html'
template_list = 'kesehatan/rencana/list.html'
template_modal = 'kesehatan/rencana/modal.html'

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
            try:
                form.save()
                messages.success(request, 'Data Berhasil Simpan')
                return redirect(reverse(url_list))  # Ganti dengan URL redirect setelah berhasil
            except Exception as e:
                messages.error(request, 'Data gagal disimpan: {}'.format(str(e)))
        else:
            messages.error(request, 'Ada kesalahan dalam form, silakan periksa kembali.')
    else:
        form = form_data(initial=initial_data)

    context = {
        'form': form,
        'judul': 'Form Rencana Kegiatan Sisa',
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
        'judul': 'Daftar Kegiatan Sisa DAU Bidang Kesehatan',
        'tombol': 'Tambah Perencanaan Sisa',
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
        form = form_filter(request.GET or None, tahun=tahunrencana, sesidana=sesidanasisa, sesisubopd=sesisubopd)

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
        'judul': 'Rencana Kegiatan Sisa',
        'isi_modal': 'Ini adalah isi modal Rencana Kegiatan.',
        'btntombol': 'Filter',
        'form': form,
        'link_url': reverse(url_filter),
    }
    return render(request, template_modal, context)
