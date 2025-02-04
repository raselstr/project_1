# File: your_app/views.py
from django.shortcuts import render,redirect
from project.decorators import menu_access_required, set_submenu_session
from django.db.models import Q
from django.urls import reverse

from pendidikan.models import Rencanaposting, Rencana
from pendidikan.forms.form_pendidikan import RencanaPostingForm

model_rencana = Rencana
model_posting = Rencanaposting
form_posting = RencanaPostingForm

tag_url = 'posting_pendidikan_list'
tag_posting = 'posting_pendidikan'

template_form = 'pendidikan/posting/form.html'
template_list = 'pendidikan/posting/list.html'
# sesitahun = 2024


@set_submenu_session
@menu_access_required('list')    
def list(request):
    request.session['next'] = request.get_full_path()
    sesiidopd = request.session.get('idsubopd')
    sesitahun = request.session.get('tahun')
    jadwalaktif = request.session.get('jadwal')
    
    filters = Q()
    if sesiidopd:
        filters &= Q(posting_subopd_id=sesiidopd)
    if sesitahun:
        filters &= Q(posting_tahun=sesitahun)

    induk = model_posting.objects.filter(posting_jadwal=jadwalaktif).filter(filters).order_by('posting_subopd_id')
    perubahan = model_posting.objects.filter(posting_jadwal=2).filter(filters).order_by('posting_subopd_id')

    # Buat dictionary untuk menyimpan data dengan kunci sebagai kombinasi field
    induk_dict = {
        (item.posting_subopd_id, item.posting_tahun, item.posting_dana_id,  item.posting_subkegiatan_id): item
        for item in induk
    }
    perubahan_dict = {
        (item.posting_subopd_id, item.posting_tahun, item.posting_dana_id, item.posting_subkegiatan_id): item
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
            selisih_pagu = item_perubahan.posting_pagu - item_induk.posting_pagu
        elif item_perubahan:
            selisih_pagu = item_perubahan.posting_pagu
        elif item_induk:
            selisih_pagu = item_induk.posting_pagu
        else:
            selisih_pagu = 0

        combined_data.append({
            'item_induk': item_induk,
            'item_perubahan': item_perubahan,
            'selisih_pagu': selisih_pagu,
        })
    
    context = {
        'judul': 'Posting Rencana Kegiatan DAU SG Bidang Pendidikan',
        'tombol': 'Posting',
        'combined_data': combined_data,
        'session':sesiidopd,
        'posting': reverse(tag_posting),
    }
    return render(request, template_list, context)


@set_submenu_session
@menu_access_required('simpan')
def posting(request):
    rencana = model_rencana.objects.all()
    jadwal = None
    opd = None
    
    if request.method == 'POST':
        form = form_posting(request.POST or None)
        if form.is_valid():
            jadwal = form.cleaned_data.get('posting_jadwal')  # Ambil nilai dari form
            opd = form.cleaned_data.get('posting_subopd')  # Ambil nilai dari form
            
            if jadwal is not None :
                if opd is not None :
                    rencana = rencana.filter(rencana_subopd=opd)
                    for item in rencana:
                        obj, created = model_posting.objects.update_or_create(
                            posting_rencanaid = item,
                            posting_tahun=item.rencana_tahun,
                            posting_dana=item.rencana_dana,
                            posting_subopd=item.rencana_subopd,
                            posting_jadwal=jadwal,
                            defaults={
                                'posting_subkegiatan':item.rencana_kegiatan,
                                'posting_pagu': item.rencana_pagu,
                                'posting_output': item.rencana_output,
                                'posting_ket': item.rencana_ket,
                                'posting_pagudpa': item.rencana_pagudpa,
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
        form = form_posting()
    
    context = {
        'judul': 'Posting Rencana Kegiatan DAU SG Pendidikan',
        'tombol': 'Posting',
        'form': form,
        'kembali' : reverse(tag_url),
        
    }
    return render(request, template_form, context)


