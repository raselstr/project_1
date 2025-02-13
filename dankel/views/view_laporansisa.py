# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankelsisa, RencDankeljadwalsisa, Subkegiatan, TahapDana, Subopd, RencDankelsisa
from dausg.models import DankelProg, DankelKeg, Dankelsub
from ..forms.form_realisasisisa import RealisasiDankelsisaFilterForm, RealisasiDankelsisaForm
from project.decorators import menu_access_required, set_submenu_session
from opd.models import Pejabat, OpdDana
from penerimaan.models import DistribusiPenerimaan
from datetime import datetime


Model_prog = DankelProg
Model_keg = DankelKeg
Model_sub = Dankelsub
Model_rencana = RencDankeljadwalsisa
Model_pagu = RencDankelsisa
Model_realisasi = RealisasiDankelsisa
Form_filter = RealisasiDankelsisaFilterForm
Form_data = RealisasiDankelsisaForm
Model_pejabat = Pejabat

tag_url = 'laporansisa_list'
tag_home = 'laporansisa_home'
template = 'dankel_laporansisa/laporansisa_list.html'
template_filter = 'dankel_laporansisa/laporansisa_filter.html'
template_form = 'dankel_laporansisa/laporansisa_form.html'
template_home = 'dankel_laporansisa/laporansisa_home.html'
sesidana = 'sisa-dana-kelurahan'
Model_penerimaan = DistribusiPenerimaan

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
        'judul': 'Rekapitulasi Realisasi Sisa Dana Kelurahan',
        'tombol': 'Cetak',
        'tombolsp2d': 'Cetak Daftar SP2D Sisa',
        'level' : level
    })
    return render(request, template, context)


@set_submenu_session
@menu_access_required('list')    
def filter(request):
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    tahunrencana = request.session.get('tahun')
    request.session['next'] = request.get_full_path()
    # sessions = Session.objects.all()
    # for session in sessions:
    #     print(session.session_key, session.get_decoded())
    
    if request.method == 'GET':
        form = Form_filter(request.GET or None, sesiidopd=sesiidopd, sesidana=sesidana, tahunrencana=tahunrencana)
        if form.is_valid():
            # Simpan data filter di sesi
            request.session['realisasidankelsisa_tahun'] = form.cleaned_data.get('realisasidankelsisa_tahun')
            request.session['realisasidankelsisa_dana'] = form.cleaned_data.get('realisasidankelsisa_dana').id if form.cleaned_data.get('realisasidankelsisa_dana') else None
            request.session['realisasidankelsisa_tahap'] = form.cleaned_data.get('realisasidankelsisa_tahap').id if form.cleaned_data.get('realisasidankelsisa_tahap') else None
            request.session['realisasidankelsisa_subopd'] = form.cleaned_data.get('realisasidankelsisa_subopd').id if form.cleaned_data.get('realisasidankelsisa_subopd') else None
            
            return redirect(tag_url)
    else:
        form = Form_filter(request.GET or None, sesiidopd=sesiidopd, sesidana=sesidana, tahunrencana=tahunrencana)
    
    context = {
        'judul' : 'Laporan Realisasi Sisa Tahun Lalu',
        'tombol' : 'Cari Laporan Realisasi Sisa Tahun Lalu',
        'form': form
        # 'datasisa' : total_pagu_sisa,
    }
    return render(request, template_filter, context)

@set_submenu_session
@menu_access_required('list')
def pdf(request):
    formatted_today = datetime.now().strftime('%d %B %Y')
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    
    
    sesiidopd = request.session.get('realisasidankelsisa_subopd')
    
    if sesiidopd:
        data = Model_pejabat.objects.filter(pejabat_sub=sesiidopd)
    
    context.update({
        'judul': 'Rekapitulasi Realisasi Sisa Tahun Lalu',
        'tombol': 'Cetak',
        'tanggal' : formatted_today,
        'data': data,
    })
    return render(request, 'dankel_laporansisa/laporansisa_pdf.html', context)

@set_submenu_session
@menu_access_required('list')
def apip(request):
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    
    sesiidopd = request.session.get('idsubopd')
    idopd = request.session.get('realisasidankelsisa_subopd')
    
    if sesiidopd:
        data = Model_pejabat.objects.filter(pejabat_sub=sesiidopd)
    
    penerimaan = Model_penerimaan.objects.filter(distri_subopd_id=idopd, distri_penerimaan__penerimaan_dana__sub_slug=sesidana)
    
    context.update({
        'judul': 'Hasil Reviu APIP Realisasi Sisa Dana Kelurahan',
        'tombol': 'Cetak',
        'data' : data,
        'penerimaan' : penerimaan,    
        })
    return render(request, 'dankel_laporansisa/laporansisa_apip.html', context)

@set_submenu_session
@menu_access_required('list')
def sp2d(request):
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    
    tahunrealisasi = request.session.get('realisasidankelsisa_tahun')
    danarealisasi_id = request.session.get('realisasidankelsisa_dana')
    tahaprealisasi_id = request.session.get('realisasidankelsisa_tahap')
    subopdrealisasi_id = request.session.get('realisasidankelsisa_subopd')
    level = request.session.get('level')
    
    filterreals = Q()
    if level != 'Pengguna':
        filterreals &= Q(realisasidankelsisa_verif=1)
    if tahunrealisasi:
        filterreals &= Q(realisasidankelsisa_tahun=tahunrealisasi)
    if danarealisasi_id:
        filterreals &= Q(realisasidankelsisa_dana_id=danarealisasi_id)
    if tahaprealisasi_id:
        filterreals &= Q(realisasidankelsisa_tahap_id=tahaprealisasi_id)
    if subopdrealisasi_id != 124 and subopdrealisasi_id != 67:
        filterreals &= Q(realisasidankelsisa_subopd_id=subopdrealisasi_id)
        
    sp2d = Model_realisasi.objects.filter(filterreals)
    if subopdrealisasi_id:
        data = Model_pejabat.objects.filter(pejabat_sub=subopdrealisasi_id)
        
    context.update({
        'judul': 'REKAPITULASI SP2D',
        'sp2d' : sp2d,
        'data' : data,
        # 'persen': total_persentase,
        })
    return render(request, 'dankel_laporansisa/laporansisa_sp2d.html', context)

def get_data_context(request):
    tahunrealisasi = request.session.get('realisasidankelsisa_tahun')
    danarealisasi_id = request.session.get('realisasidankelsisa_dana')
    tahaprealisasi_id = request.session.get('realisasidankelsisa_tahap')
    subopdrealisasi_id = request.session.get('realisasidankelsisa_subopd')
    jadwal = request.session.get('jadwal')
    level = request.session.get('level')

    # Buat filter query
    filters = Q()
    if jadwal:
        filters &= Q(rencdankelsisa_jadwal=jadwal)
    if tahunrealisasi:
        filters &= Q(rencdankelsisa_tahun=tahunrealisasi)
    if danarealisasi_id:
        filters &= Q(rencdankelsisa_dana_id=danarealisasi_id)
    if subopdrealisasi_id != 124 and subopdrealisasi_id != 67:
        filters &= Q(rencdankelsisa_subopd_id=subopdrealisasi_id)
    
    filterreals = Q()
    if level == 'APIP' :
        filterreals &= Q(realisasidankelsisa_verif=1)
    if tahunrealisasi:
        filterreals &= Q(realisasidankelsisa_tahun=tahunrealisasi)
    if danarealisasi_id:
        filterreals &= Q(realisasidankelsisa_dana_id=danarealisasi_id)
    if tahaprealisasi_id:
        if tahaprealisasi_id == 1:
            filterreals &= Q(realisasidankelsisa_tahap_id=1)
        elif tahaprealisasi_id == 2:
            filterreals &= Q(realisasidankelsisa_tahap_id__in=[1, 2])
        elif tahaprealisasi_id == 3:
            filterreals &= Q(realisasidankelsisa_tahap_id__in=[1, 2, 3])
    if subopdrealisasi_id != 124 and subopdrealisasi_id != 67:
        filterreals &= Q(realisasidankelsisa_subopd_id=subopdrealisasi_id)
    
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
                related_rencanas = rencanas.filter(rencdankelsisa_sub=sub)

                # Ambil data pagu dan output
                pagu = 0
                output = 0
                if related_rencanas.exists():
                    pagu_output = related_rencanas.aggregate(
                        total_pagu=Sum('rencdankelsisa_pagu'),
                        total_output=Sum('rencdankelsisa_output')
                    )
                    pagu = pagu_output['total_pagu'] or 0
                    output = pagu_output['total_output'] or 0

                total_pagu_keg += pagu
                total_output_keg += output

                # Ambil realisasi terkait dengan `realisasidankel_idrencana`
                total_lpj = 0
                total_output_realisasi = 0
                for rencana in related_rencanas:
                    realisasi_rencana = realisasis.filter(realisasidankelsisa_rencana=rencana.id)
                    total_lpj += realisasi_rencana.aggregate(total_lpj=Sum('realisasidankelsisa_lpjnilai'))['total_lpj'] or 0
                    total_output_realisasi += realisasi_rencana.aggregate(total_output=Sum('realisasidankelsisa_output'))['total_output'] or 0
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

