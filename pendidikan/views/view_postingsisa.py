# File: your_app/views.py
from django.shortcuts import render,redirect
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session
from django.db.models import Q
from django.urls import reverse
from core.forms.budget_opd import is_special_opd

from pendidikan.models import Rencanapostingsisa, Rencanasisa
from pendidikan.forms.form_pendidikan import RencanaPostingForm
from jadwal.models import Jadwal

model_rencana = Rencanasisa
model_posting = Rencanapostingsisa
form_posting = RencanaPostingForm
model_jadwal = Jadwal
sesidana = 'sisa-dana-alokasi-umum-dukungan-bidang-pendidikan'

tag_url = 'posting_pendidikan_listsisa'
tag_posting = 'posting_pendidikansisa'

template_form = 'pendidikan/posting/form.html'
template_list = 'pendidikan/posting/list.html'
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
    if sesiidopd and not is_special_opd(sesiidopd):
        filters &= Q(posting_subopd_id=sesiidopd)
    if sesitahun:
        filters &= Q(posting_tahun=sesitahun)

    induk = model_posting.objects.filter(posting_jadwal=jadwalaktif).filter(filters).order_by('posting_subopd_id')
    perubahan = model_posting.objects.filter(posting_jadwal=perubahanaktif).filter(filters).order_by('posting_subopd_id')

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
        'judul': 'Posting Kegiatan Sisa DAU SG Pendidikan Tahun Lalu',
        'tombol': 'Posting',
        'combined_data': combined_data,
        'session':sesiidopd,
        'posting': reverse(tag_posting),
    }
    return render(request, template_list, context)


@set_submenu_session
@menu_access_required('simpan')
def posting(request):
    jadwal = None
    opd = None
    jadwalaktif = request.session.get('jadwal')
    tahun = request.session.get('tahun')
    
    if request.method == 'POST':
        form = form_posting(
            request.POST or None,
            tahun=tahun,
            jadwal=jadwalaktif,
            sesidana=sesidana,
            sesisubopd=request.session.get('idsubopd'),
        )
        if form.is_valid():
            jadwal = form.cleaned_data.get('posting_jadwal')  # Ambil nilai dari form
            opd = form.cleaned_data.get('posting_subopd')  # Ambil nilai dari form
            
            if jadwal is not None :
                rencana = model_rencana.objects.filter(
                    rencana_tahun=tahun,
                    rencana_dana__sub_slug=sesidana,
                )
                if opd is not None:
                    rencana = rencana.filter(rencana_subopd=opd)
                else:
                    opd_ids = form.fields['posting_subopd'].queryset.values_list('id', flat=True)
                    rencana = rencana.filter(rencana_subopd_id__in=opd_ids)

                posted_count = 0
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
                    posted_count += 1
                messages.success(request, f'{posted_count} data berhasil diposting')
                return redirect(tag_url)
            else:
                messages.error(request, 'Jadwal wajib dipilih.')
        else:
            messages.error(request, 'Form posting tidak valid.')
    else:
        form = form_posting(
            request.POST or None,
            tahun=tahun,
            jadwal=jadwalaktif,
            sesidana=sesidana,
            sesisubopd=request.session.get('idsubopd'),
        )
    
    context = {
        'judul': 'Posting Kegiatan Sisa DAU SG Pendidikan Tahun Lalu',
        'tombol': 'Posting',
        'form': form,
        'kembali' : reverse(tag_url),
        
    }
    return render(request, template_form, context)
