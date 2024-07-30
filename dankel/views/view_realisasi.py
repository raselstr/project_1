# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankel, RencDankelsisa, RencDankel, Subkegiatan
from ..forms.form_realisasi import RealisasiDankelFilterForm, RealisasiDankelForm
from project.decorators import menu_access_required, set_submenu_session


Model_data = RealisasiDankel
Form_filter = RealisasiDankelFilterForm
Form_data = RealisasiDankelForm
tag_url = 'realisasidankel_list'
tag_home = 'realisasidankel_home'
template = 'dankel_realisasi/realisasi_list.html'
template_filter = 'dankel_realisasi/realisasi_filter.html'
template_form = 'dankel_realisasi/realisasi_form.html'
template_home = 'dankel_realisasi/realisasi_home.html'
sesidana = 'dana-kelurahan'

def get_from_sessions(request):
    session_data = {
        'idsubopd': request.session.get('idsubopd'),
        'sesitahun': request.session.get('tahun'),  # Ganti 'idsubopd_lain' dengan kunci session yang diinginkan
        # Tambahkan lebih banyak kunci session jika diperlukan
    }
    
    return session_data

@set_submenu_session
@menu_access_required('simpan')
def simpan(request):
    request.session['next'] = request.get_full_path()
    if request.method == 'POST':
        form = Form_data(request.POST)
        if form.is_valid():
            # Ambil data dari form yang sudah divalidasi
            realisasi_dankel = form.save(commit=False)
            
            # Ambil nilai-nilai yang diperlukan untuk validasi
            tahun = realisasi_dankel.realisasidankel_tahun
            opd = realisasi_dankel.realisasidankel_subopd_id
            dana = realisasi_dankel.realisasidankel_dana_id
            rencana_pk = realisasi_dankel.realisasidankel_rencana_id
            
            # Panggil method get_rencana_pk untuk validasi tambahan
            total_rencana_pk = realisasi_dankel.get_rencana_pk(tahun, opd, dana, rencana_pk)
            
            # Lakukan validasi tambahan jika diperlukan
            if realisasi_dankel.realisasidankel_lpjnilai > total_rencana_pk:
                form.add_error('realisasidankel_lpjnilai', 'Nilai LPJ tidak boleh lebih besar dari total rencana.')
                context = {
                    'judul': 'Form Input SP2D',
                    'form': form,
                    'btntombol': 'Simpan',
                }
                return render(request, template_form, context)
            
            # Jika validasi tambahan berhasil, simpan data
            realisasi_dankel.save()
            return redirect(tag_url)  # ganti dengan halaman sukses Anda
        else:
            context = {
                'judul': 'Form Input SP2D',
                'form': form,
                'btntombol': 'Simpan',
            }
            return render(request, template_form, context)
    else:
        # Ambil data filter dari sesi
        initial_data = {
            'realisasidankel_tahun': request.session.get('realisasidankel_tahun'),
            'realisasidankel_dana': request.session.get('realisasidankel_dana'),
            'realisasidankel_tahap': request.session.get('realisasidankel_tahap'),
            'realisasidankel_subopd': request.session.get('realisasidankel_subopd')
        }
        form = Form_data(initial=initial_data)
    context = {
        'judul': 'Form Input SP2D',
        'form': form,
        'btntombol': 'Simpan',
    }
    return render(request, template_form, context)

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
        filters &= Q(realisasidankel_tahun=tahunrealisasi)
    if danarealisasi_id:
        filters &= Q(realisasidankel_dana_id=danarealisasi_id)
    if tahaprealisasi_id:
        filters &= Q(realisasidankel_tahap_id=tahaprealisasi_id)
    if subopdrealisasi_id:
        filters &= Q(realisasidankel_subopd_id=subopdrealisasi_id)
    
    # Terapkan filter ke query data
    data = Model_data.objects.filter(filters)

    context = {
        'judul' : 'Daftar Realisasi Dana Kelurahan',
        'tombol' : 'Tambah Realisasi',
        'data' : data,
    }
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
        'tombol' : 'Tambah Realisasi Tahun Berjalan',
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
    except Subkegiatan.DoesNotExist:
        dana = None
        
    if dana:
        total_penerimaan = RealisasiDankel().get_penerimaan_total(tahun=sesitahun, opd=sesiidopd, dana=dana)
        total_realisasilpj = RealisasiDankel().get_realisasilpj_total(tahun=sesitahun, opd=sesiidopd, dana=dana)
        total_persentase = RealisasiDankel().get_persentase(tahun=sesitahun, opd=sesiidopd, dana=dana)
        # sisa_rencana = RencDankel().sisa(tahun=sesitahun, opd=sesiidopd, dana=dana)
        # total_pagu_sisa = RencDankelsisa().get_sisapagudausg(tahun=sesitahun, opd=sesiidopd, dana=dana)
        # total_rencana_sisa = RencDankelsisa().get_total_sisa(tahun=sesitahun, opd=sesiidopd, dana=dana)
        # sisa_rencana_sisa = RencDankelsisa().sisa_sisa(tahun=sesitahun, opd=sesiidopd, dana=dana)
    else:
        total_penerimaan = None
        total_realisasilpj = None
        total_persentase = None
        # sisa_rencana = None
        # total_pagu_sisa = None
        # total_rencana_sisa = None
        # sisa_rencana_sisa = None
        
    context = {
        'judul' : 'Realisasi Belanja',
        'tab1'      : 'Realisasi Belanja Tahun Berjalan',
        'tab2'      : 'Realisasi Belanja Sisa Tahun Lalu',
        # 'data' : data,
        'datapenerimaan' : total_penerimaan,
        'realisasilpj' : total_realisasilpj,
        'persentase' : total_persentase,
        # 'sisarencana' : sisa_rencana,
        # 'datasisa' : total_pagu_sisa,
        # 'total_rencana_sisa' : total_rencana_sisa,
        # 'sisa_rencana_sisa' : sisa_rencana_sisa,
    }
    return render(request, template_home, context)
    