# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RencDankeljadwal, RencDankel
from ..forms.form_posting import RencDankeljadwalForm
from project.decorators import menu_access_required, set_submenu_session
# from itertools import zip_longest digunakan untuk menggabungkan 2 data


Model_data = RencDankeljadwal
Form_filter = RencDankeljadwalForm
tag_url = 'posting_list'
template_home = 'dankel_posting/posting_home.html'
template_form = 'dankel_posting/posting_form.html'
template_list = 'dankel_posting/posting_list.html'
# sesitahun = 2024


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
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    sesitahun = session_data.get('sesitahun')
    
    filters = Q()
    if sesiidopd:
        filters &= Q(rencdankel_subopd_id=sesiidopd)
    if sesitahun:
        filters &= Q(rencdankel_tahun=sesitahun)

    induk = RencDankeljadwal.objects.filter(rencdankel_jadwal=1).filter(filters).order_by('rencdankel_subopd_id')
    perubahan = RencDankeljadwal.objects.filter(rencdankel_jadwal=2).filter(filters).order_by('rencdankel_subopd_id')

    # Buat dictionary untuk menyimpan data dengan kunci sebagai kombinasi field
    induk_dict = {
        (item.rencdankel_subopd_id, item.rencdankel_tahun, item.rencdankel_dana_id,  item.rencdankel_sub_id): item
        for item in induk
    }
    perubahan_dict = {
        (item.rencdankel_subopd_id, item.rencdankel_tahun, item.rencdankel_dana_id, item.rencdankel_sub_id): item
        for item in perubahan
    }
    
    # Gabungkan data untuk ditampilkan di template
    combined_data = []
    all_keys = set(induk_dict.keys()).union(perubahan_dict.keys())
    
    for key in all_keys:
        item_induk = induk_dict.get(key)
        item_perubahan = perubahan_dict.get(key)
        
        # Tambahkan selisih ke dalam data
        if item_induk and item_perubahan:
            selisih_pagu = item_perubahan.rencdankel_pagu - item_induk.rencdankel_pagu
        elif item_perubahan:
            selisih_pagu = item_perubahan.rencdankel_pagu
        elif item_induk:
            selisih_pagu = -item_induk.rencdankel_pagu
        else:
            selisih_pagu = 0

        combined_data.append({
            'item_induk': item_induk,
            'item_perubahan': item_perubahan,
            'selisih_pagu': selisih_pagu,
        })
    
    context = {
        'judul': 'Posting Rencana Kegiatan Dana Kelurahan',
        'tombol': 'Posting',
        'combined_data': combined_data,
        'session':sesiidopd,
    }
    return render(request, template_list, context)


@set_submenu_session
@menu_access_required('simpan')
def posting(request):
    rencana = RencDankel.objects.all()
    jadwal = None
    
    if request.method == 'POST':
        form = RencDankeljadwalForm(request.POST or None)
        if form.is_valid():
            jadwal = form.cleaned_data.get('rencdankel_jadwal')  # Ambil nilai dari form
            
            if jadwal is not None:
                for item in rencana:
                    obj, created = Model_data.objects.update_or_create(
                        rencdankel_tahun=item.rencdankel_tahun,
                        rencdankel_dana=item.rencdankel_dana,
                        rencdankel_subopd=item.rencdankel_subopd,
                        rencdankel_sub=item.rencdankel_sub,
                        rencdankel_jadwal=jadwal,
                        defaults={
                            'rencdankel_pagu': item.rencdankel_pagu,
                            'rencdankel_output': item.rencdankel_output,
                            'rencdankel_ket': item.rencdankel_ket,
                        }
                    )
                return redirect(tag_url)
            else:
                print("Field jadwal tidak ada di form.")
        else:
            print("Form tidak valid")
            print(form.errors)  # Tampilkan error form untuk debugging
    else:
        form = RencDankeljadwalForm()
    
    context = {
        'judul': 'Posting Rencana Kegiatan Dana Kelurahan',
        'tombol': 'Posting',
        'form': form
    }
    return render(request, template_form, context)

@set_submenu_session
@menu_access_required('list')    
def home(request):
    request.session['next'] = request.get_full_path()
            
    context = {
        'judul' : 'Posting Kegiatan Dana Kelurahan',
        'tab1'      : 'Posting Kegiatan Tahun Berjalan',
        'tab2'      : 'Posting Kegiatan Sisa Tahun Lalu',
       
    }
    return render(request, template_home, context)
