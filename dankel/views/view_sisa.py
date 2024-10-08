# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RencDankelsisa, Subkegiatan
from ..forms.form_sisa import RencDankelsisaForm
from project.decorators import menu_access_required, set_submenu_session


Model_data = RencDankelsisa
Form_data = RencDankelsisaForm
tag_url = 'dankelsisa_list'
template = 'dankel_sisa/dankelsisa_form.html'
template_list = 'dankel_sisa/dankelsisa_list.html'
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
        form = Form_data(request.POST or None, instance=data, sesiidopd=sesiidopd, sesidana=sesidana)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Update')
            return redirect(tag_url)
    else:
        form = Form_data(instance=data, sesiidopd=sesiidopd,sesidana=sesidana)
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
        form = Form_data(request.POST or None, sesiidopd=sesiidopd, sesidana=sesidana)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data Berhasil Simpan')
            return redirect(tag_url)  # Ganti dengan URL redirect setelah berhasil
    else:
        form = Form_data(sesiidopd=sesiidopd, sesidana=sesidana)
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
    try:
        dana = Subkegiatan.objects.get(sub_slug=sesidana)
    except Subkegiatan.DoesNotExist:
        dana = None

    # Membuat query secara dinamis
    query = Q(rencdankelsisa_tahun=sesitahun) & Q(rencdankelsisa_dana=dana)
    if sesiidopd is not None and sesiidopd != 124 and sesiidopd !=70 and sesiidopd !=67:
        query &= Q(rencdankelsisa_subopd=sesiidopd)

    data = RencDankelsisa.objects.filter(query)
    context = {
        'judul' : 'Rencana Kegiatan Sisa Tahun Lalu',
        'tombol' : 'Tambah Perencanaan Sisa Tahun Lalu',
        'data' : data,
        'totalsisa' : total_sisa,
        # 'datasisa' : total_pagu_sisa,
    }
    return render(request, template_list, context)
