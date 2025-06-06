from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q,Sum, Prefetch
from django.urls import reverse
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session
from datetime import datetime

import logging
from opd.models import Pejabat, Subopd
from kesehatan.models import Rencanakesehatanposting, Rencanakesehatanpostingsisa, Rencanakesehatan, Rencanakesehatansisa, Realisasikesehatan, Realisasikesehatansisa
from dausg.models import Subkegiatan, DausgkesehatanProg
from kesehatan.forms.forms import RealisasikesehatanFilterForm, RealisasikesehatanForm
from penerimaan.models import Penerimaan
from dana.models import TahapDana
from pagu.models import Pagudausg
from ..tables import RekapPaguTable, Sp2dTable

form_filter = RealisasikesehatanFilterForm
form_data = RealisasikesehatanForm

model_data = Rencanakesehatanposting
model_datasisa = Rencanakesehatanpostingsisa
model_rencana = Rencanakesehatan
model_rencanasisa = Rencanakesehatansisa
model_dana = Subkegiatan
model_realisasi = Realisasikesehatan
model_realisasisisa = Realisasikesehatansisa
model_penerimaan = Penerimaan
model_program = DausgkesehatanProg
model_pejabat = Pejabat
model_tahap = TahapDana
model_subopd = Subopd
model_pagu = Pagudausg

url_home = 'laporan_kesehatan_home'
url_filter = 'laporan_kesehatan_filter'
url_filtersisa = 'laporan_kesehatan_filtersisa'
url_list = 'laporan_kesehatan_list'
url_listsisa = 'laporan_kesehatan_listsisa'
url_pdf = 'laporan_kesehatan_pdf'
url_apip = 'laporan_kesehatan_apip'
url_sp2d = 'laporan_kesehatan_sp2d'

template_apip = 'kesehatan/laporan/apip.html'
template_pdf = 'kesehatan/laporan/pdf.html'
template_home = 'kesehatan/laporan/home.html'
template_list = 'kesehatan/laporan/list.html'
template_modal = 'kesehatan/laporan/modal.html'
template_sp2d = 'kesehatan/laporan/sp2d.html'

tabel= RekapPaguTable
tabelsp2d= Sp2dTable

sesidana = 'dau-dukungan-bidang-kesehatan'
sesidanasisa = 'sisa-dana-alokasi-umum-dukungan-bidang-kesehatan'

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
        total_nilai_sisa = total_nilai_rencana - total_nilai_realisasi

        rekap_data.append({
            'subopd': pagu.pagudausg_opd.sub_nama,
            'pagu': pagu.pagudausg_nilai,
            'total_rencana': total_nilai_rencana,
            'total_posting': total_nilai_posting,
            'total_tahap1': total_nilai_tahap[0],
            'total_tahap2': total_nilai_tahap[1],
            'total_tahap3': total_nilai_tahap[2],
            'total_realisasi': total_nilai_realisasi,
            'total_sisa': total_nilai_sisa,
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
            'link' : reverse(url_apip),
            'tombolsp2d' : 'SP2D',
            'linksp2d' : reverse(url_sp2d),
        }
    else:
        link_tombol = {
            'tombol':'Cetak',
            'link' : reverse(url_pdf),
            'tombolsp2d' : 'SP2D',
            'linksp2d' : reverse(url_sp2d),
        }
    
    context.update({
        'judul': 'Rekapitulasi Realisasi DAU SG Bidang Kesehatan',
        'tombolsp2d': 'Cetak Daftar SP2D',
        'link_url_kembali' : reverse(url_home),
        'kembali' : 'Kembali',
        'level' : level,
        'link_tombol':link_tombol,
        
    })
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
    jadwal = request.session.get('jadwal')
    context = rekap(request)
    
    try:
        dana = model_dana.objects.get(sub_slug=sesidana)
        danasisa = model_dana.objects.get(sub_slug=sesidanasisa)
    except model_dana.DoesNotExist:
        dana = None
        danasisa = None
    
    if dana:
        pagu = model_rencana().get_pagu(tahun=tahun, opd=sesisubopd, dana=dana)
        rencana = model_data().get_total_rencana(tahun=tahun, opd=sesisubopd, dana=dana, posting=jadwal)
        penerimaan = model_penerimaan().totalpenerimaan(tahun=tahun, dana=dana)
        realisasi = model_realisasi().get_realisasi_total(tahun=tahun, opd=sesisubopd, dana=dana)
        persendana = model_realisasi().get_persendana(tahun=tahun, opd=sesisubopd, dana=dana)
        persenpagu = model_realisasi().get_persenpagu(tahun=tahun, opd=sesisubopd, dana=dana, posting=jadwal)
        sisadana = penerimaan-realisasi
        
        pagusisa = model_rencanasisa().get_pagu(tahun=tahun, opd=sesisubopd, dana=danasisa)
        rencanasisa = model_datasisa().get_total_rencana(tahun=tahun, opd=sesisubopd, dana=danasisa, posting=jadwal)
        penerimaansisa = model_penerimaan().totalpenerimaan(tahun=tahun, dana=danasisa)
        realisasisisa = model_realisasisisa().get_realisasi_total(tahun=tahun, opd=sesisubopd, dana=danasisa)
        persendanasisa = model_realisasisisa().get_persendana(tahun=tahun, opd=sesisubopd, dana=danasisa)
        persenpagusisa = model_realisasisisa().get_persenpagu(tahun=tahun, opd=sesisubopd, dana=danasisa, posting=jadwal)
        sisasisadana=penerimaansisa-realisasisisa
    else:
        pagu = 0
        rencana = 0
        penerimaan = 0
        realisasi = 0
        persendana = 0
        persenpagu = 0
        sisadana = 0
        
        pagusisa = 0
        rencanasisa = 0
        penerimaansisa = 0
        realisasisisa = 0
        persendanasisa = 0
        persenpagusisa = 0
        sisasisadana = 0
    
    context.update({
        'judul': 'Laporan Kegiatan DAU Bidang kesehatan',
        'tab1': 'Laporan Kegiatan Tahun Berjalan',
        'tab2': 'Laporan Sisa Kegiatan Tahun Lalu',
        'datapagu': pagu,
        'datarencana' : rencana,
        'penerimaan' : penerimaan,
        'realisasi' : realisasi,
        'persendana' : persendana,
        'persenpagu' : persenpagu,
        'sisadana' : sisadana,
        
        'pagusisa' : pagusisa,
        'rencanasisa' : rencanasisa,
        'penerimaansisa' : penerimaansisa,
        'realisasisisa' : realisasisisa,
        'persendanasisa' : persendanasisa,
        'persenpagusisa' : persenpagusisa,
        'sisasisadana' : sisasisadana,
        
        'link_url': reverse(url_filter),
        'link_urlsisa': reverse(url_filtersisa),
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
        Prefetch('dausgkesehatankegs__dausgkesehatansubs__rencanakesehatanposting_set')
    ).filter(dausgkesehatankegs__dausgkesehatansubs__rencanakesehatanposting__isnull=False, dausgkesehatan_tahun=realisasi_tahun).distinct().order_by('id')

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

    for program_counter, prog in enumerate(progs, start=1):
        total_pagu_prog = 0
        total_output_prog = 0
        total_realisasi_prog = 0
        total_realisasi_output_prog = 0
        total_tahap1_prog = 0
        total_tahap2_prog = 0
        total_tahap3_prog = 0
        prog_kegs = []
        kegiatan_counter = 1  # Counter untuk kegiatan

        for keg in prog.dausgkesehatankegs.all().order_by('id'):
            total_pagu_keg = 0
            total_output_keg = 0
            total_realisasi_keg = 0
            total_realisasi_output_keg = 0
            total_tahap1_keg = 0
            total_tahap2_keg = 0
            total_tahap3_keg = 0
            keg_subs = []
            sub_kegiatan_counter = 1  # Counter untuk sub-kegiatan

            for sub in keg.dausgkesehatansubs.all().order_by('id'):
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
                            realisasi_rencana = realisasis.filter(realisasi_rencana_id=rencana.posting_rencanaid)
                            
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

        # program_counter += 1  # Increment counter program
        
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
        'judul': 'Rekapitulasi Realisasi DAU Bidang kesehatan',
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
        'judul': 'Hasil Reviu APIP Realisasi DAU Bidang kesehatan',
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
    formatted_today = datetime.now().strftime('%d %B %Y')
    
    sesiidopd = request.session.get('realisasi_subopd')
    realisasi_tahap = request.session.get('realisasi_tahap')
    tahun = request.session.get('tahun')
    filterreals = Q()
    if tahun:
        filterreals &= Q(realisasi_tahun=tahun)
    if sesiidopd not in [124]:
        filterreals = Q(realisasi_subopd=sesiidopd)
    if realisasi_tahap:
        if realisasi_tahap == 1:
            filterreals &= Q(realisasi_tahap_id=1)
        elif realisasi_tahap == 2:
            filterreals &= Q(realisasi_tahap_id__in=[1, 2])
        elif realisasi_tahap == 3:
            filterreals &= Q(realisasi_tahap_id__in=[1, 2, 3])
    
    data = model_realisasi.objects.filter(filterreals).order_by('realisasi_tahap','realisasi_subopd' )
    table = tabelsp2d(data)
        
    context.update({
        'judul': 'Rekapitulasi SP2D',
        'subjudul': 'Pemerintah Kabupaten Asahan',
        'tombol': 'Cetak',
        'tanggal' : formatted_today,
        'tabel' : table,
        })
    return render(request, template_sp2d, context)