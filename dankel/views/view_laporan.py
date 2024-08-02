# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankel, RealisasiDankelsisa, RencDankel, Subkegiatan
from dausg.models import DankelProg, DankelKeg, Dankelsub
from ..forms.form_realisasi import RealisasiDankelFilterForm, RealisasiDankelForm
from project.decorators import menu_access_required, set_submenu_session


Model_data = RealisasiDankel
Model_prog = DankelProg
Model_keg = DankelKeg
Model_sub = Dankelsub
Model_rencana = RencDankel
Model_realisasi = RealisasiDankel
Form_filter = RealisasiDankelFilterForm
Form_data = RealisasiDankelForm
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
    tahunrealisasi = request.session.get('realisasidankel_tahun')
    danarealisasi_id = request.session.get('realisasidankel_dana')
    tahaprealisasi_id = request.session.get('realisasidankel_tahap')
    subopdrealisasi_id = request.session.get('realisasidankel_subopd')

    # Buat filter query
    filters = Q()
    if tahunrealisasi:
        filters &= Q(rencdankel_tahun=tahunrealisasi)
    if danarealisasi_id:
        filters &= Q(rencdankel_dana_id=danarealisasi_id)
    if subopdrealisasi_id:
        filters &= Q(rencdankel_subopd_id=subopdrealisasi_id)
        
    filterreals = Q()
    if tahunrealisasi:
        filterreals &= Q(realisasidankel_tahun=tahunrealisasi)
    if danarealisasi_id:
        filterreals &= Q(realisasidankel_dana_id=danarealisasi_id)
    if tahaprealisasi_id:
        filterreals &= Q(realisasidankel_tahap_id=tahaprealisasi_id)
    if subopdrealisasi_id:
        filterreals &= Q(realisasidankel_subopd_id=subopdrealisasi_id)
    
    progs = Model_prog.objects.all()
    kegs = Model_keg.objects.all()
    subs = Model_sub.objects.all()
    rencanas = Model_rencana.objects.filter(filters)
    realisasis = Model_realisasi.objects.filter(filterreals)

    # Siapkan data untuk template
    prog_data = []
    for prog in progs:
        prog_kegs = []
        for keg in prog.dankelkegs.all():
            keg_subs = []
            for sub in keg.dankelsubs.all():
                # Ambil rencana terkait dengan sub
                related_rencanas = rencanas.filter(rencdankel_sub=sub)
                
                # Ambil data pagu
                pagu = 0
                if related_rencanas.exists():
                    pagu = related_rencanas.first().rencdankel_pagu
                
                # Ambil realisasi terkait dengan sub
                realisasis_sub = realisasis.filter(realisasidankel_rencana__in=related_rencanas)
                realisasi_data = []
                for rencana in related_rencanas:
                    realisasi = realisasis_sub.filter(realisasidankel_rencana=rencana).aggregate(
                        total_lpj=Sum('realisasidankel_lpjnilai') or 0,
                        total_output=Sum('realisasidankel_output') or 0
                    )
                    realisasi_data.append({
                        'rencana': rencana,
                        'realisasi': realisasi
                    })
                
                keg_subs.append({
                    'sub': sub,
                    'pagu': pagu,
                    'realisasi': realisasi_data
                })
            prog_kegs.append({
                'keg': keg,
                'subs': keg_subs
            })
        prog_data.append({
            'prog': prog,
            'kegs': prog_kegs
        })

    context = {
        'judul': 'Rekapitulasi Realisasi Dana Kelurahan',
        'tombol': 'Cetak',
        'prog_data': prog_data,
    }
    print(prog_data)

    return render(request, template, context)

@set_submenu_session
@menu_access_required('list')    
def filter(request):
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    tahunrencana = RencDankel.objects.values_list('rencdankel_tahun', flat=True).distinct()
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
    sesiidopd = session_data.get('idsubopd')
    sesitahun = session_data.get('sesitahun')
    request.session['next'] = request.get_full_path()
    try:
        dana = Subkegiatan.objects.get(sub_slug=sesidana)
        danasisa = Subkegiatan.objects.get(sub_slug='sisa-dana-kelurahan')
    except Subkegiatan.DoesNotExist:
        dana = None
        danasisa = None
        
    if dana:
        total_penerimaan = RealisasiDankel().get_penerimaan_total(tahun=sesitahun, opd=sesiidopd, dana=dana)
        total_realisasilpj = RealisasiDankel().get_realisasilpj_total(tahun=sesitahun, opd=sesiidopd, dana=dana)
        total_persentase = RealisasiDankel().get_persentase(tahun=sesitahun, opd=sesiidopd, dana=dana)
        total_penerimaansisa = RealisasiDankelsisa().get_penerimaan_total(tahun=sesitahun, opd=sesiidopd, dana=danasisa)
        total_realisasilpjsisa = RealisasiDankelsisa().get_realisasilpj_total(tahun=sesitahun, opd=sesiidopd, dana=danasisa)
        total_persentasesisa = RealisasiDankelsisa().get_persentase(tahun=sesitahun, opd=sesiidopd, dana=danasisa)
    else:
        total_penerimaan = None
        total_realisasilpj = None
        total_persentase = None
        total_penerimaansisa = None
        total_realisasilpjsisa = None
        total_persentasesisa = None
        
    context = {
        'judul' : 'Laporan Realisasi Belanja',
        'tab1'      : 'Laporan Realisasi Belanja Tahun Berjalan',
        'tab2'      : 'Laporan Realisasi Belanja Sisa Tahun Lalu',
        'datapenerimaan' : total_penerimaan,
        'realisasilpj' : total_realisasilpj,
        'persentase' : total_persentase,
        'datapenerimaansisa' : total_penerimaansisa,
        'realisasilpjsisa' : total_realisasilpjsisa,
        'persentasesisa' : total_persentasesisa,
    }
    return render(request, template_home, context)
    