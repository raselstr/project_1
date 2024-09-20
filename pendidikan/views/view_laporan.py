from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q,Sum, DecimalField
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session

from decimal import Decimal

from django_tables2 import RequestConfig
from ..tables import RealisasiTable

import logging
import string

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

url_home = 'laporan_pendidikan_home'
url_filter = 'laporan_pendidikan_filter'
url_list = 'laporan_pendidikan_list'

template_form = 'pendidikan/laporan/form.html'
template_home = 'pendidikan/laporan/home.html'
template_list = 'pendidikan/laporan/list.html'
template_modal = 'pendidikan/laporan/modal.html'
template_modal_verif = 'pendidikan/laporan/modal_verif.html'

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
        realisasi_tahap=request.session.get('realisasi_tahap')
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
        'judul': 'Laporan DAU Bidang Pendidikan',
        'tombol': 'Tambah Realisasi',
        'kembali' : 'Kembali',
        'link_url_kembali': reverse(url_home),
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
        'judul': 'Laporan Kegiatan',
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
        'judul': 'Laporan Kegiatan DAU Bidang Pendidikan',
        'tab1': 'Laporan Kegiatan Tahun Berjalan',
        'datapagu': pagu,
        'datarencana' : rencana,
        'penerimaan' : penerimaan,
        'realisasi' : realisasi,
        'persendana' : persendana,
        'persenpagu' : persenpagu,
        
        'link_url': reverse(url_filter),
    }
    return render(request, template_home, context)

def get_data_context(request):
    realisasi_tahun=request.session.get('realisasi_tahun')
    realisasi_dana=request.session.get('realisasi_dana')
    realisasi_subopd=request.session.get('realisasi_subopd')
    realisasi_tahap=request.session.get('realisasi_tahap')
    jadwal = request.session.get('jadwal')
    level = request.session.get('level')

    # Buat filter query
    filters = Q()
    if jadwal:
        filters &= Q(posting_jadwal=jadwal)
    if realisasi_tahun:
        filters &= Q(posting_tahun=realisasi_tahun)
    if realisasi_dana:
        filters &= Q(posting_dana_id=realisasi_dana)
    if realisasi_subopd not in [124,67,70]:
        filters &= Q(posting_subopd_id=realisasi_subopd)
    
    filterreals = Q()
    if level == 'APIP' :
        filterreals &= Q(realisasidankel_verif=1)
    if realisasi_tahun:
        filterreals &= Q(realisasi_tahun=realisasi_tahun)
    if realisasi_dana:
        filterreals &= Q(realisasi_dana_id=realisasi_dana)
    if realisasi_tahap:
        filterreals &= Q(realisasi_tahap_id=realisasi_tahap)
    if realisasi_subopd not in [124,67,70]:
        filterreals &= Q(realisasi_subopd_id=realisasi_subopd)
    
    progs = model_data.objects.filter(filters)
    rencanas = model_data.objects.filter(filters)
    realisasis = model_realisasi.objects.filter(filterreals)
    
    # Siapkan data untuk template
    prog_data = []
    total_pagu_keseluruhan = 0
    total_output_keseluruhan = 0
    total_realisasi_keseluruhan = 0
    total_realisasi_output_keseluruhan = 0

    # Tambahkan variabel untuk penomoran
    program_counter = 1  # Inisialisasi angka program (numerik)

    for prog in progs:
        total_pagu_prog = 0
        total_output_prog = 0
        total_realisasi_prog = 0
        total_realisasi_output_prog = 0
        prog_kegs = []

        # Tambahkan variabel untuk penomoran kegiatan
        kegiatan_counter = 0  # Inisialisasi huruf kegiatan
        alphabet_list = list(string.ascii_uppercase)  # Daftar alfabet A-Z

        for keg in prog.posting_subkegiatan.all():
            total_pagu_keg = 0
            total_output_keg = 0
            total_realisasi_keg = 0
            total_realisasi_output_keg = 0
            keg_subs = []
            for sub in keg.dankelsubs.all():
                related_rencanas = rencanas.filter(rencdankel_sub=sub)

                # Ambil data pagu dan output
                pagu = 0
                output = 0
                if related_rencanas.exists():
                    pagu_output = related_rencanas.aggregate(
                        total_pagu=Sum('rencdankel_pagu'),
                        total_output=Sum('rencdankel_output')
                    )
                    pagu = pagu_output['total_pagu'] or 0
                    output = pagu_output['total_output'] or 0

                total_pagu_keg += pagu
                total_output_keg += output

                # Ambil realisasi terkait dengan `realisasidankel_idrencana`
                total_sp2d = 0
                total_output_realisasi = 0
                for rencana in related_rencanas:
                    realisasi_rencana = realisasis.filter(realisasidankel_rencana=rencana.id)
                    total_sp2d += realisasi_rencana.aggregate(total_sp2d=Sum('realisasidankel_sp2dnilai'))['total_sp2d'] or 0
                    total_output_realisasi += realisasi_rencana.aggregate(total_output=Sum('realisasidankel_output'))['total_output'] or 0
                keg_subs.append({
                    'sub': sub,
                    'pagu': pagu,
                    'output': output,
                    'realisasi': {
                        'total_sp2d': total_sp2d,
                        'total_output': total_output_realisasi
                    }
                })

                total_realisasi_output_keg += total_output_realisasi
                total_realisasi_keg += total_sp2d

            # Gunakan huruf alphabet untuk kegiatan
            kegiatan_number = alphabet_list[kegiatan_counter]
            kegiatan_counter += 1

            prog_kegs.append({
                'kegiatan_number': kegiatan_number,  # Nomor kegiatan dengan huruf
                'keg': keg,
                'subs': keg_subs,
                'total_pagu_keg': total_pagu_keg,
                'total_output_keg': total_output_keg,
                'total_realisasi_keg': total_realisasi_keg,
                'total_realisasi_output_keg': total_realisasi_output_keg
            })
            total_pagu_prog += total_pagu_keg
            total_output_prog += total_output_keg
            total_realisasi_prog += total_realisasi_keg
            total_realisasi_output_prog += total_realisasi_output_keg

        total_pagu_keseluruhan += total_pagu_prog
        total_output_keseluruhan += total_output_prog
        total_realisasi_keseluruhan += total_realisasi_prog
        total_realisasi_output_keseluruhan += total_realisasi_output_prog

        # Tambahkan angka untuk program
        prog_number = program_counter
        program_counter += 1

        prog_data.append({
            'prog_number': prog_number,  # Nomor program dengan angka
            'prog': prog,
            'kegs': prog_kegs,
            'total_pagu_prog': total_pagu_prog,
            'total_output_prog': total_output_prog,
            'total_realisasi_prog': total_realisasi_prog,
            'total_realisasi_output_prog': total_realisasi_output_prog
        })

    return {
        'prog_data': prog_data,
        'total_pagu_keseluruhan': total_pagu_keseluruhan,
        'total_output_keseluruhan': total_output_keseluruhan,
        'total_realisasi_keseluruhan': total_realisasi_keseluruhan,
        'total_realisasi_output_keseluruhan': total_realisasi_output_keseluruhan,
        'tahunrealisasi': realisasi_tahun,
        'danarealisasi_id': Subkegiatan.objects.get(pk=realisasi_dana),
        'tahaprealisasi_id': TahapDana.objects.get(pk=realisasi_tahap),
        'subopdrealisasi_id': Subopd.objects.get(pk=realisasi_subopd),
        'jadwal': jadwal
    }