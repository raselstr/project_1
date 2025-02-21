from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session
import logging

from pendidikan.models import Rencana, Rencanasisa
from pendidikan.forms.form_pendidikan import RencanaFilterForm, RencanaForm
from dana.models import Subkegiatan
from dausg.models import DausgpendidikanSub

form_filter = RencanaFilterForm
form_data = RencanaForm

model_data = Rencana
model_datasisa = Rencanasisa
model_pagu = Subkegiatan
model_kegiatan = DausgpendidikanSub

url_home = 'rencana_pendidikan_home'
url_filter = 'rencana_pendidikan_filter'
url_filtersisa = 'rencana_pendidikansisa_filter'
url_list = 'rencana_pendidikan_list'
url_simpan = 'rencana_pendidikan_simpan'
url_update = 'rencana_pendidikan_update'
url_delete = 'rencana_pendidikan_delete'

template_form = 'pendidikan/rencana/form.html'
template_home = 'pendidikan/rencana/home.html'
template_list = 'pendidikan/rencana/list.html'
template_modal = 'pendidikan/rencana/modal.html'

sesidana = 'dau-dukungan-bidang-pendidikan'
sesidanasisa = 'sisa-dana-alokasi-umum-dukungan-bidang-pendidikan'

logger = logging.getLogger(__name__)

def satuan(request):
    pk = request.GET.get("pk")
    if not pk:
        return HttpResponse("")
    data = get_object_or_404(model_kegiatan, id=pk)
    satuan = data.dausgpendidikansub_satuan
    print(f"Satuan Ditemukan: {satuan}")
    return HttpResponse(
        f'<input type="text" id="id_rencana_satuan" name="rencana_satuan" class="form-control" value="{satuan}" readonly>'
    )


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
        form = form_filter(request.GET or None, tahun=tahunrencana, sesidana=sesidana, sesisubopd=sesisubopd)

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
        sisa = pagu-rencana
        
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
        'judul': 'Rencana Kegiatan DAU Bidang Pendidikan',
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

