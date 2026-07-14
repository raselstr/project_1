from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import RencDankeljadwalsisa, RencDankelsisa
from ..forms.form_postingsisa import RencDankeljadwalsisaForm
from project.decorators import menu_access_required, set_submenu_session
from ..services.posting_service import (
    build_combined_posting_data,
    build_posting_filters,
    get_active_jadwal_ids,
    get_session_scope,
    post_rencana_to_jadwal,
)


Model_data = RencDankeljadwalsisa
Model_induk = RencDankelsisa
Form_filter = RencDankeljadwalsisaForm
tag_url = 'postingsisa_list'
template_form = 'dankel_postingsisa/postingsisa_form.html'
template_list = 'dankel_postingsisa/postingsisa_list.html'
sesidana = 'sisa-dana-kelurahan'
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
    scope = get_session_scope(request)
    filters = build_posting_filters('rencdankelsisa', scope['opd_id'], scope['tahun'])
    combined_data = build_combined_posting_data(
        RencDankeljadwalsisa,
        'rencdankelsisa',
        get_active_jadwal_ids(scope['tahun']),
        filters,
    )
    
    context = {
        'judul': 'Posting Sisa Rencana Kegiatan Dana Kelurahan',
        'tombol': 'Posting',
        'combined_data': combined_data,
        'session': scope['opd_id'],
    }
    return render(request, template_list, context)


@set_submenu_session
@menu_access_required('simpan')
def posting(request):
    scope = get_session_scope(request)
    
    if request.method == 'POST':
        form = RencDankeljadwalsisaForm(
            request.POST or None,
            tahun=scope['tahun'],
            jadwal=scope['jadwal_id'],
            sesidana=sesidana,
            sesiidopd=scope['opd_id'],
        )
        if form.is_valid():
            jadwal = form.cleaned_data.get('rencdankelsisa_jadwal')  # Ambil nilai dari form
            opd = form.cleaned_data.get('rencdankelsisa_subopd')  # Ambil nilai dari form
            
            if jadwal is not None:
                opd_ids = None
                if opd is None:
                    opd_ids = form.fields['rencdankelsisa_subopd'].queryset.values_list('id', flat=True)
                posted_count = post_rencana_to_jadwal(
                    Model_induk,
                    Model_data,
                    'rencdankelsisa',
                    jadwal,
                    opd,
                    scope['tahun'],
                    opd_ids=opd_ids,
                    dana_slug=sesidana,
                )
                messages.success(request, f'{posted_count} data berhasil diposting')
                return redirect(tag_url)
            messages.error(request, 'Jadwal wajib dipilih.')
        else:
            messages.error(request, 'Form posting tidak valid.')
    else:
        form = Form_filter(
            tahun=scope['tahun'],
            jadwal=scope['jadwal_id'],
            sesidana=sesidana,
            sesiidopd=scope['opd_id'],
        )
    
    context = {
        'judul': 'Posting Rencana Kegiatan Dana Kelurahan',
        'tombol': 'Posting',
        'form': form
    }
    return render(request, template_form, context)
