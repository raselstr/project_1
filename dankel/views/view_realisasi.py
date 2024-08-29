# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankel, RealisasiDankelsisa, RencDankeljadwal, Subkegiatan
from ..forms.form_realisasi import RealisasiDankelFilterForm, RealisasiDankelForm
from project.decorators import menu_access_required, set_submenu_session
from django.http import JsonResponse


Model_data = RealisasiDankel
Model_sisa = RealisasiDankelsisa
Model_rencana = RencDankeljadwal
Form_filter = RealisasiDankelFilterForm
Form_data = RealisasiDankelForm

tag_url = 'realisasidankel_list'
tag_home = 'realisasidankel_home'
template = 'dankel_realisasi/realisasi_list.html'
template_filter = 'dankel_realisasi/realisasi_filter.html'
template_form = 'dankel_realisasi/realisasi_form.html'
template_home = 'dankel_realisasi/realisasi_home.html'
sesidana = 'dana-kelurahan'


def modal_content(request, pk):
    data = get_object_or_404(Model_data, pk=pk)
    return render(request, 'dankel_realisasi/verifikasi_modal.html', {'data': data})

def get_idrencana(request):
    data = {
        'idrencana': '12345'  # Data dummy untuk uji
    }
    return JsonResponse(data)

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
                'judul': 'Form Update SP2D Realisasi Tahun Berjalan',
                'form': form,
                'btntombol': 'Update',
            }
            return render(request, template_form, context)
    else:
        form = Form_data(instance=realisasi_dankel, keg=keg)
    context = {
        'judul': 'Form Update SP2D Realisasi Tahun Berjalan',
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
            realisasi_dankel = form.save(commit=False)
            realisasi_dankel.save()
            return redirect(tag_url)  # ganti dengan halaman sukses Anda
        else:
            form = Form_data(request.POST, keg=keg)
            context = {
                'judul': 'Form Input SP2D',
                'form': form,
                'btntombol': 'Simpan',
            }
            return render(request, template_form, context)
    else:
        initial_data = {
            'realisasidankel_tahun': request.session.get('realisasidankel_tahun'),
            'realisasidankel_dana': request.session.get('realisasidankel_dana'),
            'realisasidankel_tahap': request.session.get('realisasidankel_tahap'),
            'realisasidankel_subopd': request.session.get('realisasidankel_subopd')
        }
        form = Form_data(initial=initial_data, keg=keg)
    
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
    if subopdrealisasi_id != 125 and subopdrealisasi_id != 70:
        filters &= Q(realisasidankel_subopd_id=subopdrealisasi_id)
    
    # Terapkan filter ke query data
    data = Model_data.objects.filter(filters)
    
    
    total_realisasilpj = Model_data().get_realisasilpj_total(tahun=tahunrealisasi, opd=subopdrealisasi_id, dana=danarealisasi_id)
     

    context = {
        'judul' : 'Daftar Realisasi Dana Kelurahan',
        'tombol' : 'Tambah Realisasi',
        'data' : data,
        'total_realisasilpj':total_realisasilpj,
        'level': request.session.get('level')
    }
    return render(request, template, context)

@set_submenu_session
@menu_access_required('list')    
def filter(request):
    sesiidopd = request.session.get('idsubopd')
    tahunrencana = Model_rencana.objects.values_list('rencdankel_tahun', flat=True).distinct()
    request.session['next'] = request.get_full_path()
    
    
    if request.method == 'GET':
        form = Form_filter(request.GET, sesiidopd=sesiidopd, sesidana=sesidana, tahunrencana=tahunrencana)
        if form.is_valid():
            request.session['realisasidankel_tahun'] = form.cleaned_data.get('realisasidankel_tahun')
            request.session['realisasidankel_dana'] = form.cleaned_data.get('realisasidankel_dana').id if form.cleaned_data.get('realisasidankel_dana') else None
            request.session['realisasidankel_tahap'] = form.cleaned_data.get('realisasidankel_tahap').id if form.cleaned_data.get('realisasidankel_tahap') else None
            request.session['realisasidankel_subopd'] = form.cleaned_data.get('realisasidankel_subopd').id if form.cleaned_data.get('realisasidankel_subopd') else None
            
            # print(f"Redirecting to: {tag_url}")
            return redirect(tag_url)
        else:
            print(f"Form gak cocok : {form.errors}")
            # print(form.errors)
    else:
        form = Form_filter()
    # print(form)
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
    