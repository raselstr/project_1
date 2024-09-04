# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankel, RencDankel, Subkegiatan, RealisasiDankelsisa
from ..forms.form_realisasi import RealisasiDankelFilterForm, RealisasiDankelForm
from project.decorators import menu_access_required, set_submenu_session
import logging

logger = logging.getLogger(__name__)


Model_data = RealisasiDankel
Model_sisa = RealisasiDankelsisa
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

def modal_content(request, pk):
    data = get_object_or_404(Model_data, pk=pk)
    return render(request, 'dankel_realisasi/verifikasi_modal.html', {'data': data})

@set_submenu_session
@menu_access_required('update')
def verif(request, pk):
    realisasi = get_object_or_404(Model_data, pk=pk)
    verif = request.GET.get('verif')
    
    if verif == '1':
        realisasi.realisasidankel_verif = 1
    elif verif == '0':
        realisasi.realisasidankel_verif = 0
    
    realisasi.save()
    return redirect(tag_url)

@set_submenu_session
@menu_access_required('delete')
def delete(request, pk):
    request.session['next'] = request.get_full_path()
    try:
        data = Model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url)

@set_submenu_session
@menu_access_required('update')
def update(request, pk):
    request.session['next'] = request.get_full_path()
    realisasi_dankel = get_object_or_404(RealisasiDankel, pk=pk)
    
    keg = {
        'tahun' : request.session.get('realisasidankel_tahun'),
        'dana' : request.session.get('realisasidankel_dana'),
        'subopd' : request.session.get('realisasidankel_subopd'),
        'jadwal' : request.session.get('jadwal')
    }

    if request.method == 'POST':
        form = Form_data(request.POST, instance=realisasi_dankel)
        if form.is_valid():
            realisasi_dankel = form.save(commit=False)
            realisasi_dankel.save()
            return redirect(tag_url)  # ganti dengan halaman sukses Anda
        else:
            form = Form_data(request.POST, instance=realisasi_dankel, keg=keg)
            context = {
                'judul': 'Form Update SP2D',
                'form': form,
                'btntombol': 'Update',
            }
            return render(request, template_form, context)
    else:
        form = Form_data(instance=realisasi_dankel, keg=keg)
    context = {
        'judul': 'Form Update SP2D',
        'form': form,
        'btntombol': 'Update',
    }
    return render(request, template_form, context)

@set_submenu_session
@menu_access_required('simpan')
def simpan(request):
    request.session['next'] = request.get_full_path()
    keg = {
        'tahun' : request.session.get('realisasidankel_tahun'),
        'dana' : request.session.get('realisasidankel_dana'),
        'subopd' : request.session.get('realisasidankel_subopd'),
        'jadwal' : request.session.get('jadwal')
    }
    if request.method == 'POST':
        form = Form_data(request.POST)
        if form.is_valid():
            logger.info("Form is valid")
            try:
                realisasi_dankel = form.save(commit=False)
                realisasi_dankel.save()
                logger.info("Form saved successfully")
                return redirect(tag_url)  # ganti dengan halaman sukses Anda
            except Exception as e:
                logger.error(f"Error saving form: {e}")
        else:
            logger.warning("Form is not valid")
            logger.error("Form errors: %s", form.errors)
            context = {
                'judul': 'Form Input SP2D penggunaan ',
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
        form = Form_data(initial=initial_data, keg=keg)
        
    context = {
        'judul': 'Form Input SP2D penggunaan ',
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
    if subopdrealisasi_id != 124 and subopdrealisasi_id != 70:
        filters &= Q(realisasidankel_subopd_id=subopdrealisasi_id)
    
    # Terapkan filter ke query data
    data = Model_data.objects.filter(filters)
    
    total_realisasilpj = Model_data().get_realisasilpj_total(tahun=tahunrealisasi, opd=subopdrealisasi_id, dana=danarealisasi_id)

    context = {
        'judul' : 'Daftar Realisasi Dana Kelurahan',
        'tombol' : 'Tambah Realisasi ',
        'data' : data,
        'total_realisasilpj':total_realisasilpj
    }
    return render(request, template, context)

@set_submenu_session
@menu_access_required('list')    
def filter(request):
    request.session['next'] = request.get_full_path()
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    tahunrencana = RencDankel.objects.values_list('rencdankel_tahun', flat=True).distinct()
    
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
        'judul' : 'Realisasi',
        'tombol' : 'Tambah Realisasi',
        'form': form
        # 'data' : total_pagu_,
    }
    return render(request, template_filter, context)

@set_submenu_session
@menu_access_required('list')
def home(request):
    request.session['next'] = request.get_full_path()
    sesiidopd = request.session.get('idsubopd')
    sesitahun = request.session.get('tahun')
    
    try:
        dana = Subkegiatan.objects.get(sub_slug=sesidana)
        danasisa = Subkegiatan.objects.get(sub_slug='sisa-dana-kelurahan')
    except Subkegiatan.DoesNotExist:
        dana = None
        danasisa = None
        
    if dana:
        total_penerimaan = Model_data().get_penerimaan_total(tahun=sesitahun, opd=sesiidopd, dana=dana)
        total_realisasilpj = Model_data().get_realisasilpj_total(tahun=sesitahun, opd=sesiidopd, dana=dana)
        total_persentase = Model_data().get_persentase(tahun=sesitahun, opd=sesiidopd, dana=dana)
        
        total_penerimaansisa = Model_sisa().get_penerimaan_total(tahun=sesitahun, opd=sesiidopd, dana=danasisa)
        total_realisasilpjsisa = Model_sisa().get_realisasilpj_total(tahun=sesitahun, opd=sesiidopd, dana=danasisa)
        total_persentasesisa = Model_sisa().get_persentase(tahun=sesitahun, opd=sesiidopd, dana=danasisa)
    else:
        total_penerimaan = None
        total_realisasilpj = None
        total_persentase = None
        total_penerimaansisa = None
        total_realisasilpjsisa = None
        total_persentasesisa = None
        
    context = {
        'judul' : 'Realisasi Belanja',
        'tab1'      : 'Realisasi Belanja Tahun Berjalan',
        'tab2'      : 'Realisasi Belanja Sisa Tahun Lalu',
        'datapenerimaan' : total_penerimaan,
        'realisasilpj' : total_realisasilpj,
        'persentase' : total_persentase,
        'datapenerimaansisa' : total_penerimaansisa,
        'realisasilpjsisa' : total_realisasilpjsisa,
        'persentasesisa' : total_persentasesisa,
    }
    return render(request, template_home, context)
