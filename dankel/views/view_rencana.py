# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RencDankel, RencDankelsisa, Subrinc
from ..forms.form_rencana import RencDankelForm

Model_data = RencDankel
Form_data = RencDankelForm
tag_url = 'dankel_list'
template = 'dankel_rencana/dankel_form.html'
template_list = 'dankel_rencana/dankel_list.html'
template_home = 'dankel_rencana/dankel_home.html'
sesidana = 'dana-kelurahan'
sesitahun = 2024
sesiidopd = None

def delete(request, pk):
    try:
        data = Model_data.objects.get(id=pk)
        data.delete()
        messages.warning(request, "Data Berhasil dihapus")
    except Model_data.DoesNotExist:
        messages.error(request,"Dana tidak ditemukan")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect(tag_url)

def update(request, pk):
    data = get_object_or_404(Model_data, id=pk)

    if request.method == 'POST':
        form = Form_data(request.POST or None, instance=data, sesiidopd=sesiidopd, sesidana=sesidana)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Update')
            return redirect(tag_url)
    else:
        form = Form_data(instance=data, sesiidopd=sesiidopd, sesidana=sesidana)
    context = {
        'form': form,
        'judul': 'Update Rencana Kegiatan',
        'btntombol' : 'Update',
    }
    return render(request, template, context)


def simpan(request):
    if request.method == 'POST':
        form = Form_data(request.POST or None, sesiidopd=sesiidopd, sesidana=sesidana)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Simpan')
            return redirect(tag_url)  # Ganti dengan URL redirect setelah berhasil
    else:
        form = Form_data(sesiidopd=sesiidopd, sesidana=sesidana)
    context = {
        'form': form,
        'judul': 'Form Rencana Kegiatan',
        'btntombol' : 'Simpan',
    }
    return render(request, template, context)

def list(request):
    try:
        dana = Subrinc.objects.get(subrinc_slug=sesidana)
    except Subrinc.DoesNotExist:
        dana = None
        
    total_rencana = RencDankel().get_total_rencana(tahun=sesitahun, opd=sesiidopd, dana=dana)
    try:
        dana = Subrinc.objects.get(subrinc_slug=sesidana)
    except Subrinc.DoesNotExist:
        dana = None

    # Membuat query secara dinamis
    query = Q(rencdankel_tahun=sesitahun) & Q(rencdankel_dana=dana)
    if sesiidopd is not None:
        query &= Q(rencdankel_subopd=sesiidopd)

    data = RencDankel.objects.filter(query)
    context = {
        'judul' : 'Rencana Kegiatan',
        'tombol' : 'Tambah Perencanaan',
        'data' : data,
        'rencana' : total_rencana,
        # 'datasisa' : total_pagu_sisa,
    }
    return render(request, template_list, context)
    

def home(request):
    try:
        dana = Subrinc.objects.get(subrinc_slug=sesidana)
    except Subrinc.DoesNotExist:
        dana = None
        
    if dana:
        total_pagu_nilai = RencDankel().get_pagudausg(tahun=sesitahun, opd=sesiidopd, dana=dana)
        total_rencana = RencDankel().get_total_rencana(tahun=sesitahun, opd=sesiidopd, dana=dana)
        sisa_rencana = RencDankel().sisa(tahun=sesitahun, opd=sesiidopd, dana=dana)
        total_pagu_sisa = RencDankelsisa().get_sisapagudausg(tahun=sesitahun, opd=sesiidopd, dana=dana)
        total_rencana_sisa = RencDankelsisa().get_total_sisa(tahun=sesitahun, opd=sesiidopd, dana=dana)
        sisa_rencana_sisa = RencDankelsisa().sisa_sisa(tahun=sesitahun, opd=sesiidopd, dana=dana)
    else:
        total_pagu_nilai = None
        total_rencana = None
        sisa_rencana = None
        total_pagu_sisa = None
        total_rencana_sisa = None
        sisa_rencana_sisa = None
        
    context = {
        'judul' : 'Rencana Kegiatan',
        'tombol' : 'Tambah Perencanaan',
        'tab1'      : 'Rencana Kegiatan Tahun Berjalan',
        'tab2'      : 'Rencana Kegiatan Sisa Tahun Lalu',
        # 'data' : data,
        'datapagu' : total_pagu_nilai,
        'datarencana' : total_rencana,
        'sisarencana' : sisa_rencana,
        'datasisa' : total_pagu_sisa,
        'total_rencana_sisa' : total_rencana_sisa,
        'sisa_rencana_sisa' : sisa_rencana_sisa,
    }
    return render(request, template_home, context)