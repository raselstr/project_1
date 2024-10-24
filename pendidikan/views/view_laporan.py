from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q,Sum, Prefetch
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session
from datetime import datetime

import logging
from opd.models import Pejabat, Subopd
from pendidikan.models import Rencanaposting, Rencana, Realisasi
from dausg.models import Subkegiatan, DausgpendidikanProg
from pendidikan.forms import RealisasiFilterForm, RealisasiForm
from penerimaan.models import Penerimaan
from dana.models import TahapDana
from pagu.models import Pagudausg
from ..tables import RekapPaguTable


form_filter = RealisasiFilterForm
form_data = RealisasiForm

model_data = Rencanaposting
model_rencana = Rencana
model_dana = Subkegiatan
model_realisasi = Realisasi
model_penerimaan = Penerimaan
model_program = DausgpendidikanProg
model_pejabat = Pejabat
model_tahap = TahapDana
model_subopd = Subopd
model_pagu = Pagudausg

url_home = 'laporan_pendidikan_home'
url_filter = 'laporan_pendidikan_filter'
url_list = 'laporan_pendidikan_list'
url_pdf = 'laporan_pendidikan_pdf'
url_apip = 'laporan_pendidikan_apip'

template_pdf = 'pendidikan/laporan/pdf.html'
template_home = 'pendidikan/laporan/home.html'
template_list = 'pendidikan/laporan/list.html'
template_modal = 'pendidikan/laporan/modal.html'
template_apip = 'pendidikan/laporan/apip.html'

tabel= RekapPaguTable

sesidana = 'dau-dukungan-bidang-pendidikan'

logger = logging.getLogger(__name__)

def rekap(request):
    tahun = request.session.get('tahun')
    dana = model_dana.objects.get(sub_slug=sesidana)
    subopd = request.session.get('idsubopd')
    jadwal = request.session.get('jadwal')

    filters = Q(pagudausg_tahun=tahun, pagudausg_dana_id=dana.id)
    if subopd not in [None, 67, 70]:
        filters &= Q(pagudausg_opd=subopd)

    pagu_list = model_pagu.objects.filter(filters)

    rekap_data = []
    for pagu in pagu_list:
        common_filters = {
            'tahun': tahun,
            'dana_id': dana.id,
            'subopd_id': pagu.pagudausg_opd_id
        }

        total_nilai_rencana = model_rencana.objects.filter(
            rencana_tahun=common_filters['tahun'], rencana_dana_id=common_filters['dana_id'], rencana_subopd_id=common_filters['subopd_id']
        ).aggregate(total_rencana=Sum('rencana_pagu'))['total_rencana'] or 0

        total_nilai_posting = model_data.objects.filter(
            posting_tahun=common_filters['tahun'], posting_dana_id=common_filters['dana_id'], posting_subopd_id=common_filters['subopd_id'], posting_jadwal=jadwal
        ).aggregate(total_posting=Sum('posting_pagu'))['total_posting'] or 0

        total_nilai_tahap = [
            model_realisasi.objects.filter(
                realisasi_tahun=common_filters['tahun'], realisasi_dana_id=common_filters['dana_id'], realisasi_subopd_id=common_filters['subopd_id'], realisasi_tahap=i
            ).aggregate(total_realisasi=Sum('realisasi_nilai'))['total_realisasi'] or 0
            for i in range(1, 4)
        ]

        total_nilai_realisasi = sum(total_nilai_tahap)

        rekap_data.append({
            'subopd': pagu.pagudausg_opd.sub_nama,
            'pagu': pagu.pagudausg_nilai,
            'total_rencana': total_nilai_rencana,
            'total_posting': total_nilai_posting,
            'total_tahap1': total_nilai_tahap[0],
            'total_tahap2': total_nilai_tahap[1],
            'total_tahap3': total_nilai_tahap[2],
            'total_realisasi': total_nilai_realisasi,
        })

    table = tabel(rekap_data)
    return {'rekap_data': table}
    
@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    level = request.session.get('level')
    
    if level == 'APIP':
        link_tombol = {
            'tombol':'Cetak Hasil Reviu',
            'link' : reverse(url_apip)
        }
    else:
        link_tombol = {
            'tombol':'Cetak',
            'link' : reverse(url_pdf)
        }
    
    context.update({
        'judul': 'Rekapitulasi Realisasi DAU SG Bidang Pendidikan',
        'tombolsp2d': 'Cetak Daftar SP2D',
        'link_url_kembali' : reverse(url_home),
        'kembali' : 'Kembali',
        'level' : level,
        'link_tombol' : link_tombol
    })
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
    context = rekap(request)
    
    try:
        dana = model_dana.objects.get(sub_slug=sesidana)
    except model_dana.DoesNotExist:
        dana = None
    
    if dana:
        pagu = model_rencana().get_pagu(tahun=tahun, opd=sesisubopd, dana=dana)
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
    
    context.update({
        'judul': 'Laporan Kegiatan DAU Bidang Pendidikan',
        'tab1': 'Laporan Kegiatan Tahun Berjalan',
        'datapagu': pagu,
        'datarencana' : rencana,
        'penerimaan' : penerimaan,
        'realisasi' : realisasi,
        'persendana' : persendana,
        'persenpagu' : persenpagu,
        
        'link_url': reverse(url_filter),
    })
    return render(request, template_home, context)



def get_data_context(request):
    # Ambil data dari session
    realisasi_tahun = request.session.get('realisasi_tahun')
    realisasi_dana = request.session.get('realisasi_dana')
    realisasi_subopd = request.session.get('realisasi_subopd')
    realisasi_tahap = request.session.get('realisasi_tahap')
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
    if realisasi_subopd not in [None, 124, 67, 70]:
        filters &= Q(posting_subopd_id=realisasi_subopd)

    filterreals = Q()
    if level == 'APIP':
        filterreals &= Q(realisasi_verif=1)
    if realisasi_tahun:
        filterreals &= Q(realisasi_tahun=realisasi_tahun)
    if realisasi_dana:
        filterreals &= Q(realisasi_dana_id=realisasi_dana)
    if realisasi_tahap:
        if realisasi_tahap == 1:
            filterreals &= Q(realisasi_tahap_id=1)
        elif realisasi_tahap == 2:
            filterreals &= Q(realisasi_tahap_id__in=[1, 2])
        elif realisasi_tahap == 3:
            filterreals &= Q(realisasi_tahap_id__in=[1, 2, 3])
    if realisasi_subopd not in [None, 124, 67, 70]:
        filterreals &= Q(realisasi_subopd_id=realisasi_subopd)

    progs = model_program.objects.prefetch_related(
        Prefetch('dausgpendidikankegs__dausgpendidikansubs__rencanaposting_set')
    ).filter(dausgpendidikankegs__dausgpendidikansubs__rencanaposting__isnull=False).distinct().order_by('id')

    rencanas = model_data.objects.filter(filters)
    realisasis = model_realisasi.objects.filter(filterreals)

    # Siapkan data untuk template
    prog_data = []
    total_pagu_keseluruhan = 0
    total_output_keseluruhan = 0
    total_realisasi_keseluruhan = 0
    total_realisasi_output_keseluruhan = 0
    total_tahap1_keseluruhan = 0
    total_tahap2_keseluruhan = 0
    total_tahap3_keseluruhan = 0

    program_counter = 1  # Counter untuk program
    for prog in progs:
        total_pagu_prog = 0
        total_output_prog = 0
        total_realisasi_prog = 0
        total_realisasi_output_prog = 0
        total_tahap1_prog = 0
        total_tahap2_prog = 0
        total_tahap3_prog = 0
        prog_kegs = []
        kegiatan_counter = 1  # Counter untuk kegiatan

        for keg in prog.dausgpendidikankegs.all().order_by('id'):
            total_pagu_keg = 0
            total_output_keg = 0
            total_realisasi_keg = 0
            total_realisasi_output_keg = 0
            total_tahap1_keg = 0
            total_tahap2_keg = 0
            total_tahap3_keg = 0
            keg_subs = []
            sub_kegiatan_counter = 1  # Counter untuk sub-kegiatan

            for sub in keg.dausgpendidikansubs.all().order_by('id'):
                related_rencanas = rencanas.filter(posting_subkegiatan=sub)

                if related_rencanas.exists():
                    pagu_output = related_rencanas.aggregate(
                        total_pagu=Sum('posting_pagu'),
                        total_output=Sum('posting_output')
                    )
                    pagu = pagu_output['total_pagu'] or 0
                    output = pagu_output['total_output'] or 0

                    if pagu > 0:  # Hanya jika ada pagu
                        total_pagu_keg += pagu
                        total_output_keg += output

                        total_sp2d = 0
                        total_output_realisasi = 0
                        total_tahap1 = 0
                        total_tahap2 = 0
                        total_tahap3 = 0

                        for rencana in related_rencanas:
                            realisasi_rencana = realisasis.filter(realisasi_rencanaposting_id=rencana.id)
                            
                            total_sp2d += realisasi_rencana.aggregate(total_sp2d=Sum('realisasi_nilai'))['total_sp2d'] or 0
                            total_output_realisasi += realisasi_rencana.aggregate(total_output=Sum('realisasi_output'))['total_output'] or 0

                            # Hitung total per tahap
                            total_tahap1 += realisasi_rencana.filter(realisasi_tahap_id=1).aggregate(total=Sum('realisasi_nilai'))['total'] or 0
                            total_tahap2 += realisasi_rencana.filter(realisasi_tahap_id=2).aggregate(total=Sum('realisasi_nilai'))['total'] or 0
                            total_tahap3 += realisasi_rencana.filter(realisasi_tahap_id=3).aggregate(total=Sum('realisasi_nilai'))['total'] or 0

                        keg_subs.append({
                            'sub': sub,
                            'pagu': pagu,
                            'output': output,
                            'realisasi': {
                                'total_sp2d': total_sp2d,
                                'total_output': total_output_realisasi,
                                'tahap1': total_tahap1,
                                'tahap2': total_tahap2,
                                'tahap3': total_tahap3
                            },
                            'sub_number': f"{program_counter:02}.{kegiatan_counter:02}.{sub_kegiatan_counter:02}"  # Nomor sub-kegiatan
                        })

                        total_realisasi_output_keg += total_output_realisasi
                        total_realisasi_keg += total_sp2d
                        total_tahap1_keg += total_tahap1
                        total_tahap2_keg += total_tahap2
                        total_tahap3_keg += total_tahap3

                    sub_kegiatan_counter += 1  # Increment counter sub-kegiatan

            if total_pagu_keg > 0:  # Hanya jika ada total pagu
                prog_kegs.append({
                    'keg': keg,
                    'subs': keg_subs,
                    'total_pagu_keg': total_pagu_keg,
                    'total_output_keg': total_output_keg,
                    'total_realisasi_keg': total_realisasi_keg,
                    'total_realisasi_output_keg': total_realisasi_output_keg,
                    'total_tahap1_keg': total_tahap1_keg,
                    'total_tahap2_keg': total_tahap2_keg,
                    'total_tahap3_keg': total_tahap3_keg,
                    'kegiatan_number': f"{program_counter:02}.{kegiatan_counter:02}"  # Nomor kegiatan
                })
                total_pagu_prog += total_pagu_keg
                total_output_prog += total_output_keg
                total_realisasi_prog += total_realisasi_keg
                total_realisasi_output_prog += total_realisasi_output_keg
                total_tahap1_prog += total_tahap1_keg
                total_tahap2_prog += total_tahap2_keg
                total_tahap3_prog += total_tahap3_keg

            kegiatan_counter += 1  # Increment counter kegiatan

        if total_pagu_prog > 0:  # Hanya jika ada total pagu
            prog_data.append({
                'prog_number': f"{program_counter:02}",
                'prog': prog,
                'kegs': prog_kegs,
                'total_pagu_prog': total_pagu_prog,
                'total_output_prog': total_output_prog,
                'total_realisasi_prog': total_realisasi_prog,
                'total_realisasi_output_prog': total_realisasi_output_prog,
                'total_tahap1_prog': total_tahap1_prog,
                'total_tahap2_prog': total_tahap2_prog,
                'total_tahap3_prog': total_tahap3_prog,
            })
            total_pagu_keseluruhan += total_pagu_prog
            total_output_keseluruhan += total_output_prog
            total_realisasi_keseluruhan += total_realisasi_prog
            total_realisasi_output_keseluruhan += total_realisasi_output_prog
            total_tahap1_keseluruhan += total_tahap1_prog
            total_tahap2_keseluruhan += total_tahap2_prog
            total_tahap3_keseluruhan += total_tahap3_prog

        program_counter += 1  # Increment counter program
    
    tahap_laporan = model_tahap.objects.filter(id=realisasi_tahap).first().tahap_dana
    subopd_laporan = model_subopd.objects.filter(id=realisasi_subopd).first().sub_nama
    dana_laporan = model_dana.objects.filter(id=realisasi_dana).first().sub_nama
    
    return {
        'prog_data': prog_data,
        'total_pagu_keseluruhan': total_pagu_keseluruhan,
        'total_output_keseluruhan': total_output_keseluruhan,
        'total_realisasi_keseluruhan': total_realisasi_keseluruhan,
        'total_realisasi_output_keseluruhan': total_realisasi_output_keseluruhan,
        'total_tahap1_keseluruhan': total_tahap1_keseluruhan,
        'total_tahap2_keseluruhan': total_tahap2_keseluruhan,
        'total_tahap3_keseluruhan': total_tahap3_keseluruhan,
        'realisasi_tahun': realisasi_tahun,
        'realisasi_dana' : dana_laporan,
        'realisasi_subopd' : subopd_laporan,
        'realisasi_tahap' : tahap_laporan,
        'jadwal':jadwal
        
    }


@set_submenu_session
@menu_access_required('list')
def pdf(request):
    # today = datetime.now().date() tanggal sekarang
    formatted_today = datetime.now().strftime('%d %B %Y')
    
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    
    realisasi_subopd = request.session.get('realisasi_subopd')
    
    if realisasi_subopd:
        data = model_pejabat.objects.filter(pejabat_sub=realisasi_subopd)
        
    context.update({
        'judul': 'Rekapitulasi Realisasi DAU Bidang Pendidikan',
        'tombol': 'Cetak',
        'tanggal' : formatted_today,
        'data' : data,    
        })
    return render(request,template_pdf, context)

@set_submenu_session
@menu_access_required('list')
def apip(request):
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    formatted_today = datetime.now().strftime('%d %B %Y')
    
    sesiidopd = request.session.get('idsubopd')
    realisasi_tahap = request.session.get('realisasi_tahap')
    
    filterreals = Q(penerimaan_dana__sub_slug=sesidana)
    if realisasi_tahap:
        if realisasi_tahap == 1:
            filterreals &= Q(penerimaan_tahap_id=1)
        elif realisasi_tahap == 2:
            filterreals &= Q(penerimaan_tahap_id__in=[1, 2])
        elif realisasi_tahap == 3:
            filterreals &= Q(penerimaan_tahap_id__in=[1, 2, 3])
        
    if sesiidopd :
        data = model_pejabat.objects.filter(pejabat_sub=sesiidopd)
           
    penerimaan = model_penerimaan.objects.filter(filterreals)
        
    context.update({
        'judul': 'Hasil Reviu APIP Realisasi DAU Bidang Pendidikan',
        'subjudul': 'Pemerintah Kabupaten Asahan',
        'tombol': 'Cetak',
        'tanggal' : formatted_today,
        'data' : data,
        'penerimaan' : penerimaan,    
        })
    # print(f'penerimaan : {penerimaan}')
    return render(request, template_apip, context)

@set_submenu_session
@menu_access_required('list')
def sp2d(request):
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    
    tahunrealisasi = request.session.get('realisasidankel_tahun')
    danarealisasi_id = request.session.get('realisasidankel_dana')
    tahaprealisasi_id = request.session.get('realisasidankel_tahap')
    subopdrealisasi_id = request.session.get('realisasidankel_subopd')
    level = request.session.get('level')
    
    filterreals = Q()
    if level != 'Pengguna':
        filterreals &= Q(realisasidankel_verif=1)
    if tahunrealisasi:
        filterreals &= Q(realisasidankel_tahun=tahunrealisasi)
    if danarealisasi_id:
        filterreals &= Q(realisasidankel_dana_id=danarealisasi_id)
    if tahaprealisasi_id:
        filterreals &= Q(realisasidankel_tahap_id=tahaprealisasi_id)
    if subopdrealisasi_id != 124 and subopdrealisasi_id != 67:
        filterreals &= Q(realisasidankel_subopd_id=subopdrealisasi_id)
        
    sp2d = model_realisasi.objects.filter(filterreals)
    if subopdrealisasi_id:
        data = model_pejabat.objects.filter(pejabat_sub=subopdrealisasi_id)
        
    context.update({
        'judul': 'REKAPITULASI SP2D',
        'sp2d' : sp2d,
        'data' : data,
        # 'persen': total_persentase,
        })
    return render(request, 'dankel_laporan/laporan_sp2d.html', context)


