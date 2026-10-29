# File: your_app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RencDankelsisa, RencDankeljadwalsisa, Subkegiatan
from ..forms.form_sisa import RencDankelsisaForm
from ..tables import RencanasisaTable
from project.decorators import menu_access_required, set_submenu_session
from core.forms.budget_opd import scoped_opd_id
from core.services.rencana_service import enrich_rencana_with_perubahan


Model_data = RencDankelsisa
Form_data = RencDankelsisaForm
tabel_rencana = RencanasisaTable
tag_url = 'dankelsisa_list'
template = 'dankel_sisa/dankelsisa_form.html'
template_list = 'dankel_sisa/dankelsisa_list.html'
template_pdf = 'dankel_rencana/pdf.html'
sesidana = 'sisa-dana-kelurahan'
def get_from_sessions(request):
    session_data = {
        'idsubopd': request.session.get('idsubopd'),
        'sesitahun': request.session.get('tahun'),  # Ganti 'idsubopd_lain' dengan kunci session yang diinginkan
        # Tambahkan lebih banyak kunci session jika diperlukan
    }
    
    return session_data


@set_submenu_session
@menu_access_required('delete')
def delete(request, pk):
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    sesitahun = session_data.get('sesitahun')
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
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    sesitahun = session_data.get('sesitahun')
    data = get_object_or_404(Model_data, id=pk)

    if request.method == 'POST':
        form = Form_data(request.POST or None, instance=data, sesiidopd=sesiidopd, sesidana=sesidana, tahun=sesitahun)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Update')
            return redirect(tag_url)
    else:
        form = Form_data(instance=data, sesiidopd=sesiidopd, sesidana=sesidana, tahun=sesitahun)
    context = {
        'form': form,
        'judul': 'Update Rencana Kegiatan Sisa Tahun Lalu',
        'btntombol' : 'Update',
    }
    return render(request, template, context)

@set_submenu_session
@menu_access_required('simpan')
def simpan(request):
    request.session['next'] = request.get_full_path()
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    sesitahun = session_data.get('sesitahun')
    if request.method == 'POST':
        form = Form_data(request.POST or None, sesiidopd=sesiidopd, sesidana=sesidana, tahun=sesitahun)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Simpan')
            return redirect(tag_url)  # Ganti dengan URL redirect setelah berhasil
    else:
        form = Form_data(sesiidopd=sesiidopd, sesidana=sesidana, tahun=sesitahun)
    context = {
        'form': form,
        'judul': 'Form Rencana Kegiatan Sisa Tahun Lalu',
        'btntombol' : 'Simpan',
    }
    return render(request, template, context)

@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    sesitahun = session_data.get('sesitahun')
    try:
        dana = Subkegiatan.objects.get(sub_slug=sesidana)
    except Subkegiatan.DoesNotExist:
        dana = None
        
    total_sisa = RencDankelsisa().get_total_sisa(tahun=sesitahun, opd=sesiidopd, dana=dana)

    # Membuat query secara dinamis
    query = Q(rencdankelsisa_tahun=sesitahun) & Q(rencdankelsisa_dana=dana)
    scoped_subopd = scoped_opd_id(sesiidopd)
    if scoped_subopd:
        query &= Q(rencdankelsisa_subopd=scoped_subopd)

    data = RencDankelsisa.objects.filter(query)

    is_perubahan, context_extra, data = enrich_rencana_with_perubahan(
        data,
        sesitahun,
        RencDankeljadwalsisa,
        'rencdankelsisa_id',
        'rencdankelsisa_pagu',
        'rencdankelsisa_output',
        jadwal_field='rencdankelsisa_jadwal',
    )

    context = {
        'judul' : 'Rencana Kegiatan Sisa Tahun Lalu',
        'tombol' : 'Tambah Perencanaan Sisa Tahun Lalu',
        'cetak' : 'Cetak',
        'data' : data,
        'totalsisa' : total_sisa,
        'dankelsisa_cetak': reverse('dankelsisa_cetak'),
        'is_perubahan': is_perubahan,
    }
    context.update(context_extra)
    return render(request, template_list, context)


@set_submenu_session
@menu_access_required('list')
def cetak(request):
    request.session['next'] = request.get_full_path()
    tahun = request.session.get('tahun')
    sesisubopd = request.session.get('idsubopd')

    filters = Q()
    if tahun:
        filters &= Q(rencdankelsisa_tahun=tahun)
    sesisubopd = scoped_opd_id(sesisubopd)
    if sesisubopd:
        filters &= Q(rencdankelsisa_subopd=sesisubopd)

    try:
        data = Model_data.objects.filter(filters)
    except Model_data.DoesNotExist:
        data = None

    is_perubahan, context_extra, data = enrich_rencana_with_perubahan(
        data if data is not None else [],
        tahun,
        RencDankeljadwalsisa,
        'rencdankelsisa_id',
        'rencdankelsisa_pagu',
        'rencdankelsisa_output',
        jadwal_field='rencdankelsisa_jadwal',
    )

    tabel = tabel_rencana(data)

    context = {
        'judul': 'Daftar Kegiatan Rencana Kelurahan (Sisa)',
        'tombol': 'Tambah Perencanaan',
        'kembali' : 'Kembali',
        'data' : data,
        'tabel' : tabel,
        'is_perubahan': is_perubahan,
        'rencana_tahun' : tahun,
    }
    context.update(context_extra)
    return render(request, template_pdf, context)
