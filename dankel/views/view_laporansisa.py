# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankelsisa, RencDankelsisa, Subkegiatan
from dausg.models import DankelProg, DankelKeg, Dankelsub
from ..forms.form_realisasisisa import RealisasiDankelsisaFilterForm, RealisasiDankelsisaForm
from project.decorators import menu_access_required, set_submenu_session


Model_prog = DankelProg
Model_keg = DankelKeg
Model_sub = Dankelsub
Model_rencana = RencDankelsisa
Model_realisasi = RealisasiDankelsisa
Form_filter = RealisasiDankelsisaFilterForm
Form_data = RealisasiDankelsisaForm
tag_url = 'laporansisa_list'
tag_home = 'laporansisa_home'
template = 'dankel_laporansisa/laporansisa_list.html'
template_filter = 'dankel_laporansisa/laporansisa_filter.html'
template_form = 'dankel_laporansisa/laporansisa_form.html'
template_home = 'dankel_laporansisa/laporansisa_home.html'
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
    tahunrealisasi = request.session.get('realisasidankelsisa_tahun')
    danarealisasi_id = request.session.get('realisasidankelsisa_dana')
    tahaprealisasi_id = request.session.get('realisasidankelsisa_tahap')
    subopdrealisasi_id = request.session.get('realisasidankelsisa_subopd')

    # Buat filter query
    filters = Q()
    if tahunrealisasi:
        filters &= Q(rencdankelsisa_tahun=tahunrealisasi)
    if danarealisasi_id:
        filters &= Q(rencdankelsisa_dana_id=danarealisasi_id)
    if subopdrealisasi_id:
        filters &= Q(rencdankelsisa_subopd_id=subopdrealisasi_id)

    filterreals = Q()
    if tahunrealisasi:
        filterreals &= Q(realisasidankelsisa_tahun=tahunrealisasi)
    if danarealisasi_id:
        filterreals &= Q(realisasidankelsisa_dana_id=danarealisasi_id)
    if tahaprealisasi_id:
        filterreals &= Q(realisasidankelsisa_tahap_id=tahaprealisasi_id)
    if subopdrealisasi_id:
        filterreals &= Q(realisasidankelsisa_subopd_id=subopdrealisasi_id)

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

    context = {
        'judul': 'Rekapitulasi Realisasi Sisa Dana Kelurahan',
        'tombol': 'Cetak',
        'prog_data': prog_data,
        'total_pagu_keseluruhan': total_pagu_keseluruhan,
        'total_realisasi_keseluruhan': total_realisasi_keseluruhan
    }
    print(context)

    return render(request, template, context)


@set_submenu_session
@menu_access_required('list')    
def filter(request):
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    tahunrencana = RencDankelsisa.objects.values_list('rencdankelsisa_tahun', flat=True).distinct()
    request.session['next'] = request.get_full_path()
    
    if request.method == 'GET':
        form = Form_filter(request.GET, sesiidopd=sesiidopd, sesidana=sesidana, tahunrencana=tahunrencana)
        if form.is_valid():
            # Simpan data filter di sesi
            request.session['realisasidankelsisa_tahun'] = form.cleaned_data.get('realisasidankelsisa_tahun')
            request.session['realisasidankelsisa_dana'] = form.cleaned_data.get('realisasidankelsisa_dana').id if form.cleaned_data.get('realisasidankel_dana') else None
            request.session['realisasidankelsisa_tahap'] = form.cleaned_data.get('realisasidankelsisa_tahap').id if form.cleaned_data.get('realisasidankel_tahap') else None
            request.session['realisasidankelsisa_subopd'] = form.cleaned_data.get('realisasidankelsisa_subopd').id if form.cleaned_data.get('realisasidankel_subopd') else None
            
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

