# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankel, RencDankelsisa, Subrinc
from ..forms.form_realisasi import RealisasiDankelFilterForm, RealisasiDankelForm

Model_data = RealisasiDankel
Form_filter = RealisasiDankelFilterForm
Form_data = RealisasiDankelForm
tag_url = 'realisasidankel_list'
tag_home = 'realisasidankel_home'
template = 'dankel_realisasi/realisasi_list.html'
template_filter = 'dankel_realisasi/realisasi_filter.html'
template_form = 'dankel_realisasi/realisasi_form.html'
template_home = 'dankel_realisasi/realisasi_home.html'
# sesidana = 'dana-kelurahan'
# sesitahun = 2024
# sesiidopd = None

# def delete(request, pk):
#     try:
#         data = Model_data.objects.get(id=pk)
#         data.delete()
#         messages.warning(request, "Data Berhasil dihapus")
#     except Model_data.DoesNotExist:
#         messages.error(request,"Dana tidak ditemukan")
#     except ValidationError as e:
#         messages.error(request, str(e))
#     return redirect(tag_url)

# def update(request, pk):
#     data = get_object_or_404(Model_data, id=pk)

#     if request.method == 'POST':
#         form = Form_data(request.POST or None, instance=data, sesiidopd=sesiidopd, sesidana=sesidana)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Data Berhasil Update')
#             return redirect(tag_url)
#     else:
#         form = Form_data(instance=data, sesiidopd=sesiidopd,sesidana=sesidana)
#     context = {
#         'form': form,
#         'judul': 'Update Rencana Kegiatan Sisa Tahun Lalu',
#         'btntombol' : 'Update',
#     }
#     return render(request, template, context)


def simpan(request):
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
    return render(request, template_form, {'form': form, 'btntombol' : 'Simpan',})

def list(request):
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
    

def filter(request):
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

def home(request):
    # try:
    #     dana = Subrinc.objects.get(subrinc_slug=sesidana)
    # except Subrinc.DoesNotExist:
    #     dana = None
        
    # if dana:
    #     total_pagu_nilai = RencDankel().get_pagudausg(tahun=sesitahun, opd=sesiidopd, dana=dana)
    #     total_rencana = RencDankel().get_total_rencana(tahun=sesitahun, opd=sesiidopd, dana=dana)
    #     sisa_rencana = RencDankel().sisa(tahun=sesitahun, opd=sesiidopd, dana=dana)
    #     total_pagu_sisa = RencDankelsisa().get_sisapagudausg(tahun=sesitahun, opd=sesiidopd, dana=dana)
    #     total_rencana_sisa = RencDankelsisa().get_total_sisa(tahun=sesitahun, opd=sesiidopd, dana=dana)
    #     sisa_rencana_sisa = RencDankelsisa().sisa_sisa(tahun=sesitahun, opd=sesiidopd, dana=dana)
    # else:
    #     total_pagu_nilai = None
    #     total_rencana = None
    #     sisa_rencana = None
    #     total_pagu_sisa = None
    #     total_rencana_sisa = None
    #     sisa_rencana_sisa = None
        
    context = {
        'judul' : 'Realisasi Kegiatan Dana Kelurahan',
        'tab1'      : 'Realisasi Kegiatan Tahun Berjalan',
        'tab2'      : 'Realisasi Kegiatan Sisa Tahun Lalu',
        # 'data' : data,
        # 'datapagu' : total_pagu_nilai,
        # 'datarencana' : total_rencana,
        # 'sisarencana' : sisa_rencana,
        # 'datasisa' : total_pagu_sisa,
        # 'total_rencana_sisa' : total_rencana_sisa,
        # 'sisa_rencana_sisa' : sisa_rencana_sisa,
    }
    return render(request, template_home, context)
    