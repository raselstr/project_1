# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankel, RencDankelsisa
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

@set_submenu_session
@menu_access_required('simpan')
def simpan(request):
    request.session['next'] = request.get_full_path()
    if request.method == 'POST':
        form = Form_data(request.POST)
        if form.is_valid():
            form.save()
            return redirect(tag_url)  # ganti dengan halaman sukses Anda
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
        'judul' : 'Form Input SP2D',
        'form': form,
        'btntombol' : 'Simpan',
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
    request.session['next'] = request.get_full_path()
    if request.method == 'GET':
        form = Form_filter(request.GET)
        if form.is_valid():
            # Simpan data filter di sesi
            request.session['realisasidankel_tahun'] = form.cleaned_data.get('realisasidankel_tahun')
            request.session['realisasidankel_dana'] = form.cleaned_data.get('realisasidankel_dana').id if form.cleaned_data.get('realisasidankel_dana') else None
            request.session['realisasidankel_tahap'] = form.cleaned_data.get('realisasidankel_tahap').id if form.cleaned_data.get('realisasidankel_tahap') else None
            request.session['realisasidankel_subopd'] = form.cleaned_data.get('realisasidankel_subopd').id if form.cleaned_data.get('realisasidankel_subopd') else None
            
            return redirect(tag_home)
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
    request.session['next'] = request.get_full_path()
    context = {
        'judul' : 'Realisasi Kegiatan Dana Kelurahan',
        'tab1'      : 'Realisasi Kegiatan Tahun Berjalan',
        'tab2'      : 'Realisasi Kegiatan Sisa Tahun Lalu',
    }
    return render(request, template_home, context)
    