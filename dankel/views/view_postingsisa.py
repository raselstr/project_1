# File: your_app/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib import messages
from ..models import RencDankeljadwalsisa, RencDankelsisa
from ..forms.form_postingsisa import RencDankeljadwalsisaForm
from project.decorators import menu_access_required, set_submenu_session


Model_data = RencDankeljadwalsisa
Model_induk = RencDankelsisa
Form_filter = RencDankeljadwalsisaForm
tag_url = 'postingsisa_list'
template_form = 'dankel_postingsisa/postingsisa_form.html'
template_list = 'dankel_postingsisa/postingsisa_list.html'
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
    sesiidopd = request.session.get('idsubopd')
    sesitahun = request.session.get('tahun')
    
    filters = Q()
    if sesiidopd:
        filters &= Q(rencdankelsisa_subopd_id=sesiidopd)
    if sesitahun:
        filters &= Q(rencdankelsisa_tahun=sesitahun)

    induk = RencDankeljadwalsisa.objects.filter(rencdankelsisa_jadwal=1).filter(filters).order_by('rencdankelsisa_subopd_id')
    perubahan = RencDankeljadwalsisa.objects.filter(rencdankelsisa_jadwal=2).filter(filters).order_by('rencdankelsisa_subopd_id')

    # Buat dictionary untuk menyimpan data dengan kunci sebagai kombinasi field
    induk_dict = {
        (item.rencdankelsisa_subopd_id, item.rencdankelsisa_tahun, item.rencdankelsisa_dana_id,  item.rencdankelsisa_sub_id): item
        for item in induk
    }
    perubahan_dict = {
        (item.rencdankelsisa_subopd_id, item.rencdankelsisa_tahun, item.rencdankelsisa_dana_id, item.rencdankelsisa_sub_id): item
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
            selisih_pagu = item_perubahan.rencdankelsisa_pagu - item_induk.rencdankelsisa_pagu
        elif item_perubahan:
            selisih_pagu = item_perubahan.rencdankelsisa_pagu
        elif item_induk:
            selisih_pagu = item_induk.rencdankelsisa_pagu
        else:
            selisih_pagu = 0

        combined_data.append({
            'item_induk': item_induk,
            'item_perubahan': item_perubahan,
            'selisih_pagu': selisih_pagu,
        })
    
    context = {
        'judul': 'Posting Sisa Rencana Kegiatan Dana Kelurahan',
        'tombol': 'Posting',
        'combined_data': combined_data,
        'session':sesiidopd,
    }
    return render(request, template_list, context)


@set_submenu_session
@menu_access_required('simpan')
def posting(request):
    rencana = Model_induk.objects.all()
    jadwal = None
    
    if request.method == 'POST':
        form = RencDankeljadwalsisaForm(request.POST or None)
        if form.is_valid():
            jadwal = form.cleaned_data.get('rencdankelsisa_jadwal')  # Ambil nilai dari form
            
            if jadwal is not None:
                for item in rencana:
                    obj, created = Model_data.objects.update_or_create(
                        rencdankelsisa_id = item,
                        rencdankelsisa_tahun=item.rencdankelsisa_tahun,
                        rencdankelsisa_dana=item.rencdankelsisa_dana,
                        rencdankelsisa_subopd=item.rencdankelsisa_subopd,
                        rencdankelsisa_sub=item.rencdankelsisa_sub,
                        rencdankelsisa_jadwal=jadwal,
                        defaults={
                            'rencdankelsisa_pagu': item.rencdankelsisa_pagu,
                            'rencdankelsisa_output': item.rencdankelsisa_output,
                            'rencdankelsisa_ket': item.rencdankelsisa_ket,
                        }
                    )
                return redirect(tag_url)
            else:
                print("Field jadwal tidak ada di form.")
        else:
            print("Form tidak valid")
            print(form.errors)  # Tampilkan error form untuk debugging
    else:
        form = Form_filter()
    
    context = {
        'judul': 'Posting Rencana Kegiatan Dana Kelurahan',
        'tombol': 'Posting',
        'form': form
    }
    return render(request, template_form, context)


