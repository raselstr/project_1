from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import RencDankeljadwal, RencDankel
from ..forms.form_posting import RencDankeljadwalForm
from project.decorators import menu_access_required, set_submenu_session
from ..services.posting_service import (
    build_combined_posting_data,
    build_posting_filters,
    get_active_jadwal_ids,
    get_session_scope,
    post_rencana_to_jadwal,
)


Model_data = RencDankeljadwal
Form_filter = RencDankeljadwalForm
tag_url = 'posting_list'
template_home = 'dankel_posting/posting_home.html'
template_form = 'dankel_posting/posting_form.html'
template_list = 'dankel_posting/posting_list.html'
sesidana = 'dana-kelurahan'
# sesitahun = 2024


@set_submenu_session
@menu_access_required('list')    
def list(request):
    request.session['next'] = request.get_full_path()
    scope = get_session_scope(request)
    filters = build_posting_filters('rencdankel', scope['opd_id'], scope['tahun'])
    combined_data = build_combined_posting_data(
        RencDankeljadwal,
        'rencdankel',
        get_active_jadwal_ids(scope['tahun']),
        filters,
    )
    
    context = {
        'judul': 'Posting Rencana Kegiatan Dana Kelurahan',
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
        form = RencDankeljadwalForm(
            request.POST or None,
            tahun=scope['tahun'],
            jadwal=scope['jadwal_id'],
            sesidana=sesidana,
            sesiidopd=scope['opd_id'],
        )
        if form.is_valid():
            jadwal = form.cleaned_data.get('rencdankel_jadwal')  # Ambil nilai dari form
            opd = form.cleaned_data.get('rencdankel_subopd')  # Ambil nilai dari form
            
            if jadwal is not None:
                opd_ids = None
                if opd is None:
                    opd_ids = form.fields['rencdankel_subopd'].queryset.values_list('id', flat=True)
                posted_count = post_rencana_to_jadwal(
                    RencDankel,
                    Model_data,
                    'rencdankel',
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
        form = RencDankeljadwalForm(
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
