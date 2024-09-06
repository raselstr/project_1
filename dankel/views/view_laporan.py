# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankel, RealisasiDankelsisa, RencDankeljadwal, RencDankelsisa, Subkegiatan,TahapDana, Subopd, RencDankel
from dausg.models import DankelProg, DankelKeg, Dankelsub
from penerimaan.models import DistribusiPenerimaan
from ..forms.form_realisasi import RealisasiDankelFilterForm, RealisasiDankelForm
from project.decorators import menu_access_required, set_submenu_session
from opd.models import Pejabat, OpdDana
from datetime import datetime


Model_prog = DankelProg
Model_keg = DankelKeg
Model_sub = Dankelsub
Model_rencana = RencDankeljadwal
Model_pagu = RencDankel
Model_pagusisa = RencDankelsisa
Model_realisasi = RealisasiDankel
Model_realisasisisa = RealisasiDankelsisa
Form_filter = RealisasiDankelFilterForm
Form_data = RealisasiDankelForm
Model_pejabat = Pejabat
Model_penerimaan = DistribusiPenerimaan

tag_url = 'laporan_list'
tag_home = 'laporan_home'
template = 'dankel_laporan/laporan_list.html'
template_filter = 'dankel_laporan/laporan_filter.html'
template_form = 'dankel_laporan/laporan_form.html'
template_home = 'dankel_laporan/laporan_home.html'
sesidana = 'dana-kelurahan'

def get_from_sessions(request):
    session_data = {
        'idsubopd': request.session.get('idsubopd'),
        'sesitahun': request.session.get('tahun'),  # Ganti 'idsubopd_lain' dengan kunci session yang diinginkan
        # Tambahkan lebih banyak kunci session jika diperlukan
    }
    
    return session_data

@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    level = request.session.get('level')
    
    context.update({
        'judul': 'Rekapitulasi Realisasi Dana Kelurahan',
        'tombol': 'Cetak',
        'tombolsp2d': 'Cetak Daftar SP2D',
        'level' : level
    })
    return render(request, template, context)


@set_submenu_session
@menu_access_required('list')    
def filter(request):
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    tahunrencana = Model_rencana.objects.values_list('rencdankel_tahun', flat=True).distinct()
    request.session['next'] = request.get_full_path()
    
    if request.method == 'GET':
        form = Form_filter(request.GET, sesiidopd=sesiidopd, sesidana=sesidana, tahunrencana=tahunrencana)
        if form.is_valid():
            # Simpan data filter di sesi
            request.session['realisasidankel_tahun'] = form.cleaned_data.get('realisasidankel_tahun')
            request.session['realisasidankel_dana'] = form.cleaned_data.get('realisasidankel_dana').id if form.cleaned_data.get('realisasidankel_dana') else None
            request.session['realisasidankel_tahap'] = form.cleaned_data.get('realisasidankel_tahap').id if form.cleaned_data.get('realisasidankel_tahap') else None
            request.session['realisasidankel_subopd'] = form.cleaned_data.get('realisasidankel_subopd').id if form.cleaned_data.get('realisasidankel_subopd') else None
            
            return redirect(tag_url)
    else:
        form = Form_filter()
    
    context = {
        'judul' : 'Realisasi Tahun Berjalan',
        'tombol' : 'Cari Laporan Realisasi Tahun Berjalan',
        'form': form
        # 'datasisa' : total_pagu_sisa,
    }
    return render(request, template_filter, context)

@set_submenu_session
@menu_access_required('list')
def home(request):
    session_data = get_from_sessions(request)
    sesitahun = session_data.get('sesitahun')
    sesiidopd = session_data.get('idsubopd')
    request.session['next'] = request.get_full_path()

    try:
        dana = Subkegiatan.objects.get(sub_slug= sesidana)  # Sesuaikan dengan slug dana utama
        danasisa = Subkegiatan.objects.get(sub_slug='sisa-dana-kelurahan')
    except Subkegiatan.DoesNotExist:
        dana = None
        danasisa = None
    
    if sesiidopd is not None and sesiidopd !=70 and sesiidopd !=67:
        subopds = OpdDana.objects.filter(opddana_dana=dana, opddana_subopd=sesiidopd)
    else:
        subopds = OpdDana.objects.filter(opddana_dana=dana)

    # Inisialisasi variabel untuk menyimpan total per OPD dan total global
    total_per_opd = []

    total_pagu_global = 0
    total_pagusisa_global = 0
    total_penerimaan_global = 0
    total_realisasilpj_global = 0
    total_persentase_global = 0
    total_penerimaansisa_global = 0
    total_realisasilpjsisa_global = 0
    total_persentasesisa_global = 0

    # Iterasi melalui setiap sub-OPD
    for subopd in subopds:
        sesiidopd = subopd.opddana_subopd
        # print(sesiidopd)

        if dana:
            total_pagu = Model_pagu().get_pagudausg(tahun=sesitahun, opd=sesiidopd, dana=dana)
            total_penerimaan = Model_realisasi().get_penerimaan_total(tahun=sesitahun, opd=sesiidopd, dana=dana)
            total_realisasilpj = Model_realisasi().get_realisasilpj_total(tahun=sesitahun, opd=sesiidopd, dana=dana)
            total_persentase = Model_realisasi().get_persentase(tahun=sesitahun, opd=sesiidopd, dana=dana)

            # Menghitung total penerimaan, realisasi LPJ, dan persentase untuk sisa dana
            total_pagusisa = Model_pagusisa().get_sisapagudausg(tahun=sesitahun, opd=sesiidopd, dana=dana)
            total_penerimaansisa = Model_realisasisisa().get_penerimaan_total(tahun=sesitahun, opd=sesiidopd, dana=danasisa)
            total_realisasilpjsisa = Model_realisasisisa().get_realisasilpj_total(tahun=sesitahun, opd=sesiidopd, dana=danasisa)
            total_persentasesisa = Model_realisasisisa().get_persentase(tahun=sesitahun, opd=sesiidopd, dana=danasisa)
        else:
            total_penerimaan = total_realisasilpj = total_persentase = total_pagu = None
            total_penerimaansisa = total_realisasilpjsisa = total_persentasesisa = total_pagusisa = None

        # Menambahkan nilai OPD saat ini ke total global
        if total_pagu is not None:
            total_pagu_global += total_pagu
        if total_penerimaan is not None:
            total_penerimaan_global += total_penerimaan
        if total_realisasilpj is not None:
            total_realisasilpj_global += total_realisasilpj
        if total_persentase is not None:
            total_persentase_global += total_persentase
        
        if total_pagusisa is not None:
            total_pagusisa_global += total_pagusisa
        if total_penerimaansisa is not None:
            total_penerimaansisa_global += total_penerimaansisa
        if total_realisasilpjsisa is not None:
            total_realisasilpjsisa_global += total_realisasilpjsisa
        if total_persentasesisa is not None:
            total_persentasesisa_global += total_persentasesisa

        # Menyimpan hasil per OPD
        total_per_opd.append({
            'opd': subopd.opddana_subopd,  # Ganti sesuai dengan nama field sub-OPD
            'total_pagu': total_pagu,
            'total_penerimaan': total_penerimaan,
            'total_realisasilpj': total_realisasilpj,
            'total_persentase': total_persentase,
            'total_pagusisa': total_pagusisa,
            'total_penerimaansisa': total_penerimaansisa,
            'total_realisasilpjsisa': total_realisasilpjsisa,
            'total_persentasesisa': total_persentasesisa,
        })

    # Menghitung rata-rata persentase global (karena ini penjumlahan, kita perlu membaginya dengan jumlah OPD)
    opd_count = subopds.count()
    rata_persentase_global = total_persentase_global / opd_count if opd_count > 0 else 0
    rata_persentasesisa_global = total_persentasesisa_global / opd_count if opd_count > 0 else 0

    context = {
        'judul' : 'Laporan Realisasi Belanja Dana Kelurahan',
        'tab1'      : 'Laporan Realisasi Belanja Tahun Berjalan',
        'tab2'      : 'Laporan Realisasi Belanja Sisa Tahun Lalu',
        'data_per_opd': total_per_opd,
        'total_pagu_global': total_pagu_global,
        'total_penerimaan_global': total_penerimaan_global,
        'total_realisasilpj_global': total_realisasilpj_global,
        'rata_persentase_global': rata_persentase_global,
        
        'total_pagusisa_global': total_pagusisa_global,
        'total_penerimaansisa_global': total_penerimaansisa_global,
        'total_realisasilpjsisa_global': total_realisasilpjsisa_global,
        'rata_persentasesisa_global': rata_persentasesisa_global,
    }
    # print(f"Total Penerimaan: {total_penerimaan}")
    return render(request, template_home, context)
    
@set_submenu_session
@menu_access_required('list')
def pdf(request):
    # today = datetime.now().date() tanggal sekarang
    formatted_today = datetime.now().strftime('%d %B %Y')
    
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    
    sesiidopd = request.session.get('realisasidankel_subopd')
    
    if sesiidopd:
        data = Model_pejabat.objects.filter(pejabat_sub=sesiidopd)
        
    context.update({
        'judul': 'Rekapitulasi Realisasi Dana Kelurahan',
        'tombol': 'Cetak',
        'tanggal' : formatted_today,
        'data' : data,    
        })
    return render(request, 'dankel_laporan/laporan_pdf.html', context)

@set_submenu_session
@menu_access_required('list')
def apip(request):
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    
    sesiidopd = request.session.get('idsubopd')
    idopd = request.session.get('realisasidankel_subopd')
    
    if sesiidopd :
        data = Model_pejabat.objects.filter(pejabat_sub=sesiidopd)
    
    penerimaan = Model_penerimaan.objects.filter(distri_subopd_id=idopd, distri_penerimaan__penerimaan_dana__sub_slug=sesidana)
        
    context.update({
        'judul': 'Hasil Reviu APIP Realisasi Dana Kelurahan',
        'tombol': 'Cetak',
        'data' : data,
        'penerimaan' : penerimaan,    
        })
    # print(f'penerimaan : {penerimaan}')
    return render(request, 'dankel_laporan/laporan_apip.html', context)

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
        
    sp2d = Model_realisasi.objects.filter(filterreals)
    if subopdrealisasi_id:
        data = Model_pejabat.objects.filter(pejabat_sub=subopdrealisasi_id)
        
    context.update({
        'judul': 'REKAPITULASI SP2D',
        'sp2d' : sp2d,
        'data' : data,
        # 'persen': total_persentase,
        })
    return render(request, 'dankel_laporan/laporan_sp2d.html', context)

def get_data_context(request):
    tahunrealisasi = request.session.get('realisasidankel_tahun')
    danarealisasi_id = request.session.get('realisasidankel_dana')
    tahaprealisasi_id = request.session.get('realisasidankel_tahap')
    subopdrealisasi_id = request.session.get('realisasidankel_subopd')
    jadwal = request.session.get('jadwal')
    level = request.session.get('level')

    # Buat filter query
    filters = Q()
    if jadwal:
        filters &= Q(rencdankel_jadwal=jadwal)
    if tahunrealisasi:
        filters &= Q(rencdankel_tahun=tahunrealisasi)
    if danarealisasi_id:
        filters &= Q(rencdankel_dana_id=danarealisasi_id)
    if subopdrealisasi_id != 124 and subopdrealisasi_id != 67:
        filters &= Q(rencdankel_subopd_id=subopdrealisasi_id)
    
    filterreals = Q()
    if level == 'APIP' :
        filterreals &= Q(realisasidankel_verif=1)
    if tahunrealisasi:
        filterreals &= Q(realisasidankel_tahun=tahunrealisasi)
    if danarealisasi_id:
        filterreals &= Q(realisasidankel_dana_id=danarealisasi_id)
    if tahaprealisasi_id:
        filterreals &= Q(realisasidankel_tahap_id=tahaprealisasi_id)
    if subopdrealisasi_id != 124 and subopdrealisasi_id != 67:
        filterreals &= Q(realisasidankel_subopd_id=subopdrealisasi_id)
    
    progs = Model_prog.objects.all()
    rencanas = Model_rencana.objects.filter(filters)
    realisasis = Model_realisasi.objects.filter(filterreals)

    # Siapkan data untuk template
    prog_data = []
    total_pagu_keseluruhan = 0
    total_output_keseluruhan = 0
    total_realisasi_keseluruhan = 0
    total_realisasi_output_keseluruhan = 0

    for prog in progs:
        total_pagu_prog = 0
        total_output_prog = 0
        total_realisasi_prog = 0
        total_realisasi_output_prog = 0
        prog_kegs = []
        for keg in prog.dankelkegs.all():
            total_pagu_keg = 0
            total_output_keg = 0
            total_realisasi_keg = 0
            total_realisasi_output_keg = 0
            keg_subs = []
            for sub in keg.dankelsubs.all():
                # Ambil rencana terkait dengan sub
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
                total_lpj = 0
                total_output_realisasi = 0
                for rencana in related_rencanas:
                    realisasi_rencana = realisasis.filter(realisasidankel_idrencana=rencana.id)
                    total_lpj += realisasi_rencana.aggregate(total_lpj=Sum('realisasidankel_lpjnilai'))['total_lpj'] or 0
                    total_output_realisasi += realisasi_rencana.aggregate(total_output=Sum('realisasidankel_output'))['total_output'] or 0

                keg_subs.append({
                    'sub': sub,
                    'pagu': pagu,
                    'output': output,
                    'realisasi': {
                        'total_lpj': total_lpj,
                        'total_output': total_output_realisasi
                    }
                })

                total_realisasi_output_keg += total_output_realisasi
                total_realisasi_keg += total_lpj

            prog_kegs.append({
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

        prog_data.append({
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
        'tahunrealisasi': tahunrealisasi,
        'danarealisasi_id': Subkegiatan.objects.get(pk=danarealisasi_id),
        'tahaprealisasi_id': TahapDana.objects.get(pk=tahaprealisasi_id),
        'subopdrealisasi_id': Subopd.objects.get(pk=subopdrealisasi_id),
        'jadwal': jadwal
    }

