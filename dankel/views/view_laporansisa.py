# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankelsisa, RencDankeljadwalsisa, Subkegiatan, TahapDana, Subopd
from dausg.models import DankelProg, DankelKeg, Dankelsub
from ..forms.form_realisasisisa import RealisasiDankelsisaFilterForm, RealisasiDankelsisaForm
from project.decorators import menu_access_required, set_submenu_session
from django.contrib.sessions.models import Session
from opd.models import Pejabat
from penerimaan.models import DistribusiPenerimaan


Model_prog = DankelProg
Model_keg = DankelKeg
Model_sub = Dankelsub
Model_rencana = RencDankeljadwalsisa
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
    context.update({
        'judul': 'Rekapitulasi Realisasi Sisa Dana Kelurahan',
        'tombol': 'Cetak'
    })
    return render(request, template, context)


@set_submenu_session
@menu_access_required('list')    
def filter(request):
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    tahunrencana = Model_rencana.objects.values_list('rencdankelsisa_tahun', flat=True).distinct()
    request.session['next'] = request.get_full_path()
    # sessions = Session.objects.all()
    # for session in sessions:
    #     print(session.session_key, session.get_decoded())
    
    if request.method == 'GET':
        form = Form_filter(request.GET, sesiidopd=sesiidopd, sesidana=sesidana, tahunrencana=tahunrencana)
        if form.is_valid():
            # Simpan data filter di sesi
            request.session['realisasidankelsisa_tahun'] = form.cleaned_data.get('realisasidankelsisa_tahun')
            request.session['realisasidankelsisa_dana'] = form.cleaned_data.get('realisasidankelsisa_dana').id if form.cleaned_data.get('realisasidankelsisa_dana') else None
            request.session['realisasidankelsisa_tahap'] = form.cleaned_data.get('realisasidankelsisa_tahap').id if form.cleaned_data.get('realisasidankelsisa_tahap') else None
            request.session['realisasidankelsisa_subopd'] = form.cleaned_data.get('realisasidankelsisa_subopd').id if form.cleaned_data.get('realisasidankelsisa_subopd') else None
            
            return redirect(tag_url)
    else:
        form = Form_filter()
    
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
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    
    idsubopd = request.session.get('idsubopd')
    if idsubopd:
        data = Model_pejabat.objects.filter(pejabat_sub=idsubopd)
    
    context.update({
        'judul': 'Rekapitulasi Realisasi Sisa Tahun Lalu',
        'tombol': 'Cetak',
        'data': data,
    })
    return render(request, 'dankel_laporansisa/laporansisa_pdf.html', context)

@set_submenu_session
@menu_access_required('list')
def apip(request):
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    idopd = request.session.get('realisasidankelsisa_subopd')
    idsubopd = request.session.get('idsubopd')
    if idsubopd:
        data = Model_pejabat.objects.filter(pejabat_sub=idsubopd)
    
    penerimaan = Model_penerimaan.objects.filter(distri_subopd_id=idopd, distri_penerimaan__penerimaan_dana__sub_slug=sesidana)
    
    context.update({
        'judul': 'Hasil Reviu APIP Realisasi Sisa Dana Kelurahan',
        'tombol': 'Cetak',
        'data' : data,
        'penerimaan' : penerimaan,    
        })
    return render(request, 'dankel_laporansisa/laporansisa_apip.html', context)

def get_data_context(request):
    tahunrealisasisisa = request.session.get('realisasidankelsisa_tahun')
    danarealisasisisa_id = request.session.get('realisasidankelsisa_dana')
    tahaprealisasisisa_id = request.session.get('realisasidankelsisa_tahap')
    subopdrealisasisisa_id = request.session.get('realisasidankelsisa_subopd')
    jadwal = request.session.get('jadwal')
    level = request.session.get('level')

    # Buat filter query
    filters = Q()
    if jadwal:
        filters &=Q(rencdankelsisa_jadwal=jadwal)
    if tahunrealisasisisa:
        filters &= Q(rencdankelsisa_tahun=tahunrealisasisisa)
    if danarealisasisisa_id:
        filters &= Q(rencdankelsisa_dana_id=danarealisasisisa_id)
    if subopdrealisasisisa_id != 124 and subopdrealisasisisa_id != 70:
        filters &= Q(rencdankelsisa_subopd_id=subopdrealisasisisa_id)

    filterreals = Q()
    if level != 'Pengguna':
        filterreals &= Q(realisasidankelsisa_verif=1)
    if tahunrealisasisisa:
        filterreals &= Q(realisasidankelsisa_tahun=tahunrealisasisisa)
    if danarealisasisisa_id:
        filterreals &= Q(realisasidankelsisa_dana_id=danarealisasisisa_id)
    if tahaprealisasisisa_id:
        filterreals &= Q(realisasidankelsisa_tahap_id=tahaprealisasisisa_id)
    if subopdrealisasisisa_id != 124 and subopdrealisasisisa_id != 70:
        filterreals &= Q(realisasidankelsisa_subopd_id=subopdrealisasisisa_id)
    
    progs = Model_prog.objects.all()
    kegs = Model_keg.objects.all()
    subs = Model_sub.objects.all()
    rencanas = Model_rencana.objects.filter(filters)
    realisasis = Model_realisasi.objects.filter(filterreals)
    

    # Siapkan data untuk template
    prog_data = []
    total_pagu_keseluruhan = 0
    total_realisasi_keseluruhan = 0
    
    for prog in progs:
        total_pagu_prog = 0
        total_realisasi_prog = 0
        prog_kegs = []
        for keg in prog.dankelkegs.all():
            total_pagu_keg = 0
            total_realisasi_keg = 0
            keg_subs = []
            for sub in keg.dankelsubs.all():
                # Ambil rencana terkait dengan sub
                related_rencanas = rencanas.filter(rencdankelsisa_sub=sub)
                
                # Ambil data pagu
                pagu = 0
                if related_rencanas.exists():
                    pagu = related_rencanas.aggregate(total_pagu=Sum('rencdankelsisa_pagu'))['total_pagu'] or 0
                
                # Hitung total pagu untuk keg dan prog
                total_pagu_keg += pagu
                
                # Ambil realisasi terkait dengan sub
                realisasis_sub = realisasis.filter(realisasidankelsisa_rencana__in=related_rencanas)
                realisasi_data = []
                for rencana in related_rencanas:
                    realisasi = realisasis_sub.filter(realisasidankelsisa_rencana=rencana).aggregate(
                        total_lpj=Sum('realisasidankelsisa_lpjnilai'),
                        total_output=Sum('realisasidankelsisa_output')
                    )
                    total_lpj = realisasi['total_lpj'] if realisasi['total_lpj'] is not None else 0
                    total_output = realisasi['total_output'] if realisasi['total_output'] is not None else 0
                    realisasi_data.append({
                        'rencana': rencana,
                        'realisasi': {
                            'total_lpj': total_lpj,
                            'total_output': total_output
                        }
                    })
                    total_realisasi_keg += total_lpj
                
                keg_subs.append({
                    'sub': sub,
                    'pagu': pagu,
                    'realisasi': realisasi_data
                })
            prog_kegs.append({
                'keg': keg,
                'subs': keg_subs,
                'total_pagu_keg': total_pagu_keg,
                'total_realisasi_keg': total_realisasi_keg
            })
            total_pagu_prog += total_pagu_keg
            total_realisasi_prog += total_realisasi_keg
        
        total_pagu_keseluruhan += total_pagu_prog
        total_realisasi_keseluruhan += total_realisasi_prog
        
        prog_data.append({
            'prog': prog,
            'kegs': prog_kegs,
            'total_pagu_prog': total_pagu_prog,
            'total_realisasi_prog': total_realisasi_prog
        })
    return {
        'prog_data': prog_data,
        'total_pagu_keseluruhan': total_pagu_keseluruhan,
        'total_realisasi_keseluruhan': total_realisasi_keseluruhan,
        'tahunrealisasisisa' : tahunrealisasisisa,
        'danarealisasisisa_id' : Subkegiatan.objects.get(pk=danarealisasisisa_id),
        'tahaprealisasisisa_id' : TahapDana.objects.get(pk=tahaprealisasisisa_id),
        'subopdrealisasisisa_id' : Subopd.objects.get(pk=subopdrealisasisisa_id),
        'jadwal' : jadwal
    }


