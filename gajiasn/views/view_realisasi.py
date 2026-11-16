from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session
import logging

from gajiasn.models import (
    Rencanagajiasnposting,
    Rencanagajiasn,
    Realisasigajiasn,
    Rencanagajiasnpostingsisa,
    Rencanagajiasnsisa,
    Realisasigajiasnsisa,
)
from dausg.models import Subkegiatan
from gajiasn.forms.forms import RealisasigajiasnFilterForm, RealisasigajiasnForm
from gajiasn.tables import RealisasigajiasnTable, RencanagajiasnpostingTable
from penerimaan.models import Penerimaan
from core.forms.budget_opd import scoped_opd_id
from core.services.home_rekap_service import HomeRekapService

tabel_realisasi = RealisasigajiasnTable
tabel_rencana = RencanagajiasnpostingTable

form_filter = RealisasigajiasnFilterForm
form_data = RealisasigajiasnForm

model_data = Rencanagajiasnposting
model_datasisa = Rencanagajiasnpostingsisa
model_pagu = Rencanagajiasn
model_dana = Subkegiatan
model_realisasi = Realisasigajiasn
model_realisasisisa = Realisasigajiasnsisa
model_penerimaan = Penerimaan

url_home = 'realisasi_gajiasn_home'
url_filter = 'realisasi_gajiasn_filter'
url_filtersisa = 'realisasi_gajiasn_filtersisa'
url_list = 'realisasi_gajiasn_list'
url_simpan = 'realisasi_gajiasn_simpan'
url_update = 'realisasi_gajiasn_update'
url_delete = 'realisasi_gajiasn_delete'
url_verif = 'realisasi_gajiasn_verif'
url_sp2d = 'realisasi_gajiasn_sp2d'
url_sipd = 'data_sipd'

template_form = 'gajiasn/realisasi/form.html'
template_home = 'gajiasn/realisasi/home.html'
template_list = 'gajiasn/realisasi/list.html'
template_sp2d = 'gajiasn/realisasi/sp2d.html'
template_modal = 'gajiasn/realisasi/modal.html'
template_modal_verif = 'gajiasn/realisasi/modal_verif.html'

sesidana = 'dukungan-pemenuhan-kebutuhan-penggajian-aparatur-sipil-negara-daerah'
sesidanasisa = 'sisa-dukungan-pemenuhan-kebutuhan-penggajian-aparatur-sipil-negara-daerah'

logger = logging.getLogger(__name__)


def safe_reverse(name, args=None, kwargs=None):
    try:
        if name and (args or kwargs):
            return reverse(name, args=args, kwargs=kwargs)
        elif name:
            return reverse(name)
    except Exception as e:
        logger.warning(f"⚠️ reverse gagal [{name}]: {e}")
    return '#'


def modal(request, pk):
    data = get_object_or_404(model_realisasi, pk=pk)
    context = {
        'data': data,
        'verifurl': url_verif
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
    next_url = request.session.get('next') or reverse(url_list)
    return redirect(next_url)


@set_submenu_session
@menu_access_required('delete')
def delete(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = model_realisasi.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except model_realisasi.DoesNotExist:
        messages.error(request, "Data tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(url_list)


@set_submenu_session
@menu_access_required('update')
def update(request, pk):
    request.session['next'] = request.get_full_path()
    data = get_object_or_404(model_realisasi, id=pk)
    rencana_posting = getattr(data, 'realisasi_rencanaposting', None)
    satuan = rencana_posting.get_satuan_kegiatan() if rencana_posting and hasattr(rencana_posting, 'get_satuan_kegiatan') else None
    if request.method == 'POST':
        form = form_data(request.POST or None, instance=data, satuan=satuan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Update')
            return redirect(url_list)
    else:
        form = form_data(instance=data, satuan=satuan)
    context = {
        'form': form,
        'judul': 'Update Realisasi Kegiatan',
        'btntombol': 'Update',
        'link_url': reverse(url_list),
        'satuan': satuan,
        'rencana_posting': rencana_posting,
    }
    return render(request, template_form, context)


@set_submenu_session
@menu_access_required('simpan')
def simpan(request, pk=None):
    request.session['next'] = request.get_full_path()
    rencana_posting = None
    satuan = None
    if pk:
        try:
            rencana_posting = model_data.objects.get(pk=pk)
            satuan = rencana_posting.get_satuan_kegiatan() if hasattr(rencana_posting, 'get_satuan_kegiatan') else None
        except model_data.DoesNotExist:
            pass
    initial_data = dict(
        realisasi_tahun=request.session.get('realisasi_tahun'),
        realisasi_dana=request.session.get('realisasi_dana'),
        realisasi_subopd=request.session.get('realisasi_subopd'),
        realisasi_tahap=request.session.get('realisasi_tahap'),
        jadwal=request.session.get('jadwal'),
    )
    if pk and rencana_posting:
        initial_data['realisasi_rencanaposting'] = rencana_posting.id
    if request.method == 'POST':
        form = form_data(request.POST or None, initial_data=initial_data, satuan=satuan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Simpan')
            return redirect(reverse(url_list))
    else:
        form = form_data(initial=initial_data, initial_data=initial_data, satuan=satuan)

    context = {
        'form': form,
        'judul': 'Form Realisasi Kegiatan',
        'btntombol': 'Simpan',
        'link_url': reverse(url_list),
        'satuan': satuan,
        'rencana_posting': rencana_posting,
    }
    return render(request, template_form, context)


@set_submenu_session
@menu_access_required('list')
def sp2d(request, pk=None):
    request.session['next'] = request.get_full_path()
    realisasi_tahun = request.session.get('realisasi_tahun')
    realisasi_dana = request.session.get('realisasi_dana')
    realisasi_subopd = request.session.get('realisasi_subopd')
    realisasi_tahap = request.session.get('realisasi_tahap')

    posting_obj = model_data.objects.filter(pk=pk).first()
    filters = Q()
    if posting_obj:
        filters &= Q(realisasi_subkegiatan_id=posting_obj.posting_subkegiatan_id)
        filters &= Q(realisasi_subopd_id=posting_obj.posting_subopd_id)
    else:
        filters &= Q(realisasi_rencanaposting_id=pk)

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
    scoped_subopd = scoped_opd_id(realisasi_subopd)
    if scoped_subopd:
        filters &= Q(realisasi_subopd_id=scoped_subopd)

    filterkeg = Q(pk=pk)
    if realisasi_tahun:
        filterkeg &= Q(posting_tahun=realisasi_tahun)
    if realisasi_dana:
        filterkeg &= Q(posting_dana_id=realisasi_dana)
    if scoped_subopd:
        filterkeg &= Q(posting_subopd_id=scoped_subopd)

    try:
        data = model_realisasi.objects.filter(filters)
        datarencana = model_data.objects.filter(filterkeg)
    except (model_realisasi.DoesNotExist, model_data.DoesNotExist):
        data = None
        datarencana = None

    table = tabel_realisasi(data, request=request)
    tabelrencana = tabel_rencana(datarencana, request=request)

    sipd_registry_key = 'realisasi_gajiasn'

    context = {
        'judul': 'Daftar Realisasi DAU SG Gaji ASN',
        'subjudul': 'Daftar Kegiatan',
        'tombol': 'Tambah Realisasi',
        'kembali': 'Kembali',
        'link_url': safe_reverse(url_simpan, args=[pk]) if pk else '#',
        'link_url_kembali': safe_reverse(url_list),
        'link_url_sipd': (safe_reverse(url_sipd, args=[sipd_registry_key, pk]) if pk else '#'),
        'link_url_update': url_update,
        'link_url_delete': url_delete,
        'data': data,
        'table': table,
        'datarencana': datarencana,
        'tabelrencana': tabelrencana,
        'sipd': 'SIPD',
    }
    return render(request, template_sp2d, context)


@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    jadwal = request.session.get('jadwal')
    realisasi_tahun = request.session.get('realisasi_tahun')
    realisasi_dana = request.session.get('realisasi_dana')
    realisasi_subopd = request.session.get('realisasi_subopd')

    filters = Q(posting_jadwal_id=jadwal)
    if realisasi_tahun:
        filters &= Q(posting_tahun=realisasi_tahun)
    if realisasi_dana:
        filters &= Q(posting_dana_id=realisasi_dana)
    realisasi_subopd = scoped_opd_id(realisasi_subopd)
    if realisasi_subopd:
        filters &= Q(posting_subopd_id=realisasi_subopd)

    try:
        datarencana = model_data.objects.filter(filters)
    except model_data.DoesNotExist:
        datarencana = None

    tabelrencana = tabel_rencana(datarencana, show_aksi=True)
    tabelrencana.paginate = False

    context = {
        'judul': 'Daftar Realisasi DAU SG Gaji ASN',
        'tombol': 'Tambah Realisasi',
        'kembali': 'Kembali',
        'link_url_kembali': reverse(url_home),
        'link_url_update': url_update,
        'link_url_delete': url_delete,
        'datarencana': datarencana,
        'tabelrencana': tabelrencana,
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
    except model_dana.DoesNotExist:
        dana = None

    try:
        danasisa = model_dana.objects.get(sub_slug=sesidanasisa)
    except model_dana.DoesNotExist:
        danasisa = None

    if dana:
        rencana = model_data().get_total_rencana(tahun=tahun, opd=sesisubopd, dana=dana, posting=jadwal)
        penerimaan = model_penerimaan().totalpenerimaan(tahun=tahun, dana=dana)
        realisasi = model_realisasi().get_realisasi_total(tahun=tahun, opd=sesisubopd, dana=dana)
        persendana = model_realisasi().get_persendana(tahun=tahun, opd=sesisubopd, dana=dana)
        persenpagu = model_realisasi().get_persenpagu(tahun=tahun, opd=sesisubopd, dana=dana, posting=jadwal)

        rencanasisa = model_datasisa().get_total_rencana(tahun=tahun, opd=sesisubopd, dana=danasisa, posting=jadwal) if danasisa else 0
        penerimaansisa = model_penerimaan().totalpenerimaan(tahun=tahun, dana=danasisa) if danasisa else 0
        realisasisisa = model_realisasisisa().get_realisasi_total(tahun=tahun, opd=sesisubopd, dana=danasisa) if danasisa else 0
        persendanasisa = model_realisasisisa().get_persendana(tahun=tahun, opd=sesisubopd, dana=danasisa) if danasisa else 0
        persenpagusisa = model_realisasisisa().get_persenpagu(tahun=tahun, opd=sesisubopd, dana=danasisa, posting=jadwal) if danasisa else 0
    else:
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
        'judul': 'Realisasi Kegiatan DAU SG Gaji ASN',
        'tab1': 'Realisasi Kegiatan Tahun Berjalan',
        'tab2': 'Realisasi Kegiatan Sisa Tahun Lalu',
        'datarencana': rencana,
        'penerimaan': penerimaan,
        'realisasi': realisasi,
        'persendana': persendana,
        'persenpagu': persenpagu,

        'rencanasisa': rencanasisa,
        'penerimaansisa': penerimaansisa,
        'realisasisisa': realisasisisa,
        'persendanasisa': persendanasisa,
        'persenpagusisa': persenpagusisa,

        'link_url': reverse(url_filter),
        'link_urlsisa': reverse(url_filtersisa),
    }
    try:
        rekap_ctx = HomeRekapService.get_rekap_realisasi_sp2d('gajiasn', tahun, sesisubopd)
        context.update(rekap_ctx)
    except Exception:
        pass
    return render(request, template_home, context)
