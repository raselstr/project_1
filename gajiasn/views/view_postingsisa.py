from django.shortcuts import render, redirect
from django.contrib import messages
from project.decorators import menu_access_required, set_submenu_session
from django.db.models import Q
from django.urls import reverse
from core.forms.budget_opd import is_special_opd

from gajiasn.models import Rencanagajiasnpostingsisa, Rencanagajiasnsisa
from gajiasn.forms.sisa import RencanagajiasnPostingForm
from jadwal.models import Jadwal

model_rencana = Rencanagajiasnsisa
model_posting = Rencanagajiasnpostingsisa
form_posting = RencanagajiasnPostingForm
model_jadwal = Jadwal
sesidana = 'sisa-dukungan-pemenuhan-kebutuhan-penggajian-aparatur-sipil-negara-daerah'

tag_url = 'posting_gajiasn_listsisa'
tag_posting = 'posting_gajiasnsisa'

template_form = 'gajiasn/posting/form.html'
template_list = 'gajiasn/posting/list.html'


@set_submenu_session
@menu_access_required('list')
def list(request):
    request.session['next'] = request.get_full_path()
    sesiidopd = request.session.get('idsubopd')
    sesitahun = request.session.get('tahun')

    tbljadwal = model_jadwal.objects.filter(jadwal_tahun=sesitahun).order_by('id').distinct()
    if tbljadwal.count() == 1:
        jadwalaktif = tbljadwal.first().id
        perubahanaktif = None
    elif tbljadwal.count() > 1:
        jadwalaktif = tbljadwal.first().id
        perubahanaktif = tbljadwal.last().id
    else:
        jadwalaktif = None
        perubahanaktif = None

    filters = Q()
    if sesiidopd and not is_special_opd(sesiidopd):
        filters &= Q(posting_subopd_id=sesiidopd)
    if sesitahun:
        filters &= Q(posting_tahun=sesitahun)

    induk = model_posting.objects.filter(posting_jadwal=jadwalaktif).filter(filters).order_by('posting_subopd_id')
    perubahan = model_posting.objects.filter(posting_jadwal=perubahanaktif).filter(filters).order_by('posting_subopd_id')

    induk_dict = {
        (item.posting_subopd_id, item.posting_tahun, item.posting_dana_id, item.posting_subkegiatan_id): item
        for item in induk
    }
    perubahan_dict = {
        (item.posting_subopd_id, item.posting_tahun, item.posting_dana_id, item.posting_subkegiatan_id): item
        for item in perubahan
    }

    combined_data = []
    all_keys = set(induk_dict.keys()).union(perubahan_dict.keys())

    for key in all_keys:
        item_induk = induk_dict.get(key)
        item_perubahan = perubahan_dict.get(key)

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
        'judul': 'Posting Rencana Kegiatan Sisa DAU SG Gaji ASN',
        'tombol': 'Posting',
        'combined_data': combined_data,
        'session': sesiidopd,
        'posting': reverse(tag_posting)
    }
    return render(request, template_list, context)


@set_submenu_session
@menu_access_required('simpan')
def posting(request):
    jadwalaktif = request.session.get('jadwal')
    tahun = request.session.get('tahun')

    if tahun:
        active_jadwal_obj = model_jadwal.objects.filter(jadwal_tahun=tahun, jadwal_aktif=True).last()
        if active_jadwal_obj:
            jadwalaktif = active_jadwal_obj.id
            if request.session.get('jadwal') != active_jadwal_obj.id:
                request.session['jadwal'] = active_jadwal_obj.id
                request.session['jadwal_ket'] = active_jadwal_obj.jadwal_keterangan
                request.session.modified = True

    if request.method == 'POST':
        form = form_posting(
            request.POST or None,
            tahun=tahun,
            jadwal=jadwalaktif,
            sesidana=sesidana,
            sesisubopd=request.session.get('idsubopd'),
        )
        if form.is_valid():
            jadwal = form.cleaned_data.get('posting_jadwal')
            opd = form.cleaned_data.get('posting_subopd')

            if jadwal is not None:
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
                    model_posting.objects.update_or_create(
                        posting_rencanaid=item,
                        posting_tahun=item.rencana_tahun,
                        posting_dana=item.rencana_dana,
                        posting_subopd=item.rencana_subopd,
                        posting_jadwal=jadwal,
                        defaults={
                            'posting_subkegiatan': item.rencana_kegiatan,
                            'posting_pagu': item.rencana_pagu,
                            'posting_output': item.rencana_output,
                            'posting_uraianoutput': item.rencana_uraianoutput,
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
            tahun=tahun,
            jadwal=jadwalaktif,
            sesidana=sesidana,
            sesisubopd=request.session.get('idsubopd'),
        )

    context = {
        'judul': 'Posting Rencana Kegiatan Sisa DAU SG Gaji ASN',
        'tombol': 'Posting',
        'form': form,
        'kembali': reverse(tag_url),
    }
    return render(request, template_form, context)
