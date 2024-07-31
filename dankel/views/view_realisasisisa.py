# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RealisasiDankelsisa, RencDankelsisa, Subkegiatan
from ..forms.form_realisasisisa import RealisasiDankelsisaFilterForm, RealisasiDankelsisaForm
from project.decorators import menu_access_required, set_submenu_session


Model_data = RealisasiDankelsisa
Form_filter = RealisasiDankelsisaFilterForm
Form_data = RealisasiDankelsisaForm
tag_url = 'realisasisisadankel_list'
tag_home = 'realisasisisadankel_home'
template = 'dankel_realisasisisa/realisasisisa_list.html'
template_filter = 'dankel_realisasisisa/realisasisisa_filter.html'
template_form = 'dankel_realisasisisa/realisasisisa_form.html'
template_home = 'dankel_realisasisisa/realisasisisa_home.html'
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
    realisasi_dankel = get_object_or_404(RealisasiDankelsisa, pk=pk)

    if request.method == 'POST':
        form = Form_data(request.POST, instance=realisasi_dankel)
        if form.is_valid():
            # Ambil data dari form yang sudah divalidasi
            realisasi_dankel = form.save(commit=False)
            
            # Ambil nilai-nilai yang diperlukan untuk validasi
            tahun = realisasi_dankel.realisasidankelsisa_tahun
            opd = realisasi_dankel.realisasidankelsisa_subopd_id
            dana = realisasi_dankel.realisasidankelsisa_dana_id
            rencana_pk = realisasi_dankel.realisasidankelsisa_rencana_id
            
            # Panggil method get_rencana_pk untuk validasi tambahan
            total_rencana_pk = realisasi_dankel.get_rencana_pk(tahun, opd, dana, rencana_pk)
            total_realisasi_pk = realisasi_dankel.get_realisasi_pk(tahun, opd, dana, rencana_pk)

            # Lakukan validasi tambahan jika diperlukan
            if total_realisasi_pk > total_rencana_pk:
                form.add_error('realisasidankelsisa_lpjnilai', f'Nilai LPJ tidak boleh lebih besar dari total rencana sebesar Rp. {total_rencana_pk}')
                context = {
                    'judul': 'Form Update SP2D',
                    'form': form,
                    'btntombol': 'Update',
                }
                return render(request, template_form, context)
            
            # Jika validasi tambahan berhasil, simpan data
            realisasi_dankel.save()
            return redirect(tag_url)  # ganti dengan halaman sukses Anda
        else:
            context = {
                'judul': 'Form Update SP2D',
                'form': form,
                'btntombol': 'Update',
            }
            return render(request, template_form, context)
    else:
        form = Form_data(instance=realisasi_dankel)
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
    if request.method == 'POST':
        form = Form_data(request.POST)
        if form.is_valid():
            # Ambil data dari form yang sudah divalidasi
            realisasisisa_dankel = form.save(commit=False)
            
            # Ambil nilai-nilai yang diperlukan untuk validasi
            tahun = realisasisisa_dankel.realisasidankelsisa_tahun
            opd = realisasisisa_dankel.realisasidankelsisa_subopd_id
            dana = realisasisisa_dankel.realisasidankelsisa_dana_id
            rencana_pk = realisasisisa_dankel.realisasidankelsisa_rencana_id
            
            # Panggil method get_rencana_pk untuk validasi tambahan
            total_rencana_pk = realisasisisa_dankel.get_rencana_pk(tahun, opd, dana, rencana_pk)
            total_realisasi_pk = realisasisisa_dankel.get_realisasi_pk(tahun, opd, dana, rencana_pk)
            
            
            # Lakukan validasi tambahan jika diperlukan
            if total_realisasi_pk > total_rencana_pk:
                form.add_error('realisasidankelsisa_lpjnilai', f'Nilai LPJ tidak boleh lebih besar dari total rencana sebesar Rp. {total_rencana_pk}')
                context = {
                    'judul': 'Form Input SP2D penggunaan Sisa',
                    'form': form,
                    'btntombol': 'Simpan',
                }
                return render(request, template_form, context)
            
            # Jika validasi tambahan berhasil, simpan data
            realisasisisa_dankel.save()
            return redirect(tag_url)  # ganti dengan halaman sukses Anda
        else:
            context = {
                'judul': 'Form Input SP2D penggunaan Sisa',
                'form': form,
                'btntombol': 'Simpan',
            }
            return render(request, template_form, context)
    else:
        # Ambil data filter dari sesi
        initial_data = {
            'realisasidankelsisa_tahun': request.session.get('realisasidankelsisa_tahun'),
            'realisasidankelsisa_dana': request.session.get('realisasidankelsisa_dana'),
            'realisasidankelsisa_tahap': request.session.get('realisasidankelsisa_tahap'),
            'realisasidankelsisa_subopd': request.session.get('realisasidankelsisa_subopd')
        }
        form = Form_data(initial=initial_data)
    context = {
        'judul': 'Form Input SP2D penggunaan Sisa',
        'form': form,
        'btntombol': 'Simpan',
    }
    return render(request, template_form, context)

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
        filters &= Q(realisasidankelsisa_tahun=tahunrealisasi)
    if danarealisasi_id:
        filters &= Q(realisasidankelsisa_dana_id=danarealisasi_id)
    if tahaprealisasi_id:
        filters &= Q(realisasidankelsisa_tahap_id=tahaprealisasi_id)
    if subopdrealisasi_id:
        filters &= Q(realisasidankelsisa_subopd_id=subopdrealisasi_id)
    
    # Terapkan filter ke query data
    data = Model_data.objects.filter(filters)

    context = {
        'judul' : 'Daftar Realisasi Sisa Tahun Lalu Dana Kelurahan',
        'tombol' : 'Tambah Realisasi Sisa Tahun Lalu ',
        'data' : data,
    }
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
            request.session['realisasidankelsisa_dana'] = form.cleaned_data.get('realisasidankelsisa_dana').id if form.cleaned_data.get('realisasidankelsisa_dana') else None
            request.session['realisasidankelsisa_tahap'] = form.cleaned_data.get('realisasidankelsisa_tahap').id if form.cleaned_data.get('realisasidankelsisa_tahap') else None
            request.session['realisasidankelsisa_subopd'] = form.cleaned_data.get('realisasidankelsisa_subopd').id if form.cleaned_data.get('realisasidankelsisa_subopd') else None
            
            return redirect(tag_url)
    else:
        form = Form_filter()
    
    context = {
        'judul' : 'Realisasi Sisa Tahun Lalu',
        'tombol' : 'Tambah Realisasi Sisa Tahun Lalu',
        'form': form
        # 'datasisa' : total_pagu_sisa,
    }
    return render(request, template_filter, context)
