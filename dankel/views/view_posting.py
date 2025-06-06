# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RencDankeljadwal, RencDankel
from ..forms.form_posting import RencDankeljadwalForm
from project.decorators import menu_access_required, set_submenu_session
from jadwal.models import Jadwal
# from itertools import zip_longest digunakan untuk menggabungkan 2 data


Model_data = RencDankeljadwal
Form_filter = RencDankeljadwalForm
model_jadwal = Jadwal
tag_url = 'posting_list'
template_home = 'dankel_posting/posting_home.html'
template_form = 'dankel_posting/posting_form.html'
template_list = 'dankel_posting/posting_list.html'
# sesitahun = 2024


@set_submenu_session
@menu_access_required('list')    
def list(request):
    request.session['next'] = request.get_full_path()
    sesiidopd = request.session.get('idsubopd')
    sesitahun = request.session.get('tahun')
    
    tbljadwal = model_jadwal.objects.filter(jadwal_tahun=sesitahun).distinct()
    if tbljadwal.count() == 1:
    # Jika hanya ada 1 data, gunakan untuk induk
        jadwalaktif = tbljadwal.first().id
        perubahanaktif = None
    elif tbljadwal.count() > 1:
        # Jika lebih dari 1 data, jadwal pertama untuk induk, terakhir untuk perubahan
        jadwalaktif = tbljadwal.first().id
        perubahanaktif = tbljadwal.last().id
    else:
        # Jika tidak ada data, jadwalaktif kosong
        jadwalaktif = None
        perubahanaktif = None
        
    filters = Q()
    if sesiidopd:
        filters &= Q(rencdankel_subopd_id=sesiidopd)
    if sesitahun:
        filters &= Q(rencdankel_tahun=sesitahun)

    induk = RencDankeljadwal.objects.filter(rencdankel_jadwal=jadwalaktif).filter(filters).order_by('rencdankel_subopd_id')
    perubahan = RencDankeljadwal.objects.filter(rencdankel_jadwal=perubahanaktif).filter(filters).order_by('rencdankel_subopd_id')

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
            selisih_pagu = item_induk.rencdankel_pagu
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
    opd = None
    jadwalaktif = request.session.get('jadwal')
    tahun = request.session.get('tahun')
    
    if request.method == 'POST':
        form = RencDankeljadwalForm(request.POST or None,tahun=tahun, jadwal=jadwalaktif)
        if form.is_valid():
            jadwal = form.cleaned_data.get('rencdankel_jadwal')  # Ambil nilai dari form
            opd = form.cleaned_data.get('rencdankel_subopd')  # Ambil nilai dari form
            
            if jadwal is not None :
                if opd is not None :
                    rencana = rencana.filter(rencdankel_subopd=opd, rencdankel_tahun=tahun)
                    for item in rencana:
                        obj, created = Model_data.objects.update_or_create(
                            rencdankel_id = item,
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
                    print("Field jadwal atau OPD tidak ada di form.")
            else:
                print("Field jadwal tidak ada di form.")
        else:
            print("Form tidak valid")
            print(form.errors)  # Tampilkan error form untuk debugging
    else:
        form = RencDankeljadwalForm(tahun=tahun, jadwal=jadwalaktif)
    
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
        'judul' : 'Posting Kegiatan',
        'tab1'      : 'Posting Kegiatan Dana Kelurahan Tahun Berjalan',
        'tab2'      : 'Posting Kegiatan Sisa Dana Kelurahan Tahun Lalu',
        'tab3'      : 'Posting Kegiatan DAU SG Pendidikan Tahun Berjalan',
        'tab4'      : 'Posting Kegiatan Sisa DAU SG Pendidikan Tahun Lalu',
        'tab5'      : 'Posting Kegiatan DAU SG Kesehatan Tahun Berjalan',
        'tab6'      : 'Posting Kegiatan Sisa DAU SG Kesehatan Tahun Lalu',
        'tab7'      : 'Posting Kegiatan DAU SG Pekerjaan Umum Tahun Berjalan',
        'tab8'      : 'Posting Kegiatan Sisa DAU SG Pekerjaan Umum Tahun Lalu',
       
    }
    return render(request, template_home, context)
