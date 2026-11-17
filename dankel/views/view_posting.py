from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Sum

from ..models import (
    RencDankeljadwal,
    RencDankel,
    RencDankelsisa,
    RencDankeljadwalsisa,
)
from ..forms.form_posting import RencDankeljadwalForm
from project.decorators import menu_access_required, set_submenu_session
from ..services.posting_service import (
    build_combined_posting_data,
    build_posting_filters,
    get_active_jadwal_ids,
    get_session_scope,
    post_rencana_to_jadwal,
)
from jadwal.models import Jadwal
from pendidikan.models import (
    Rencana as RencPend,
    Rencanaposting as PostPend,
    Rencanasisa as RencPendsisa,
    Rencanapostingsisa as PostPendsisa,
)
from kesehatan.models import (
    Rencanakesehatan as RencKes,
    Rencanakesehatanposting as PostKes,
    Rencanakesehatansisa as RencKessisa,
    Rencanakesehatanpostingsisa as PostKessisa,
)
from pu.models import (
    Rencanapu as RencPU,
    Rencanapuposting as PostPU,
    Rencanapusisa as RencPUsisa,
    Rencanapupostingsisa as PostPUsisa,
)
from gajiasn.models import (
    Rencanagajiasn as RencGaji,
    Rencanagajiasnposting as PostGaji,
    Rencanagajiasnsisa as RencGajiSisa,
    Rencanagajiasnpostingsisa as PostGajiSisa,
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

def get_posting_dashboard_data(tahun):
    jadwal_aktif = Jadwal.objects.filter(jadwal_tahun=tahun, jadwal_aktif=True).first()

    bidang_defs = [
        {
            'id': 'pendidikan',
            'nama': 'DAU SG Pendidikan',
            'singkat': 'Pendidikan',
            'icon': 'fas fa-graduation-cap',
            'badge_color': '#0052cc',
            'border_color': '#2563eb',
            'header_bg': 'linear-gradient(135deg, #07192f 0%, #0052cc 100%)',
            'mr_u': RencPend,
            'mp_u': PostPend,
            'mr_s': RencPendsisa,
            'mp_s': PostPendsisa,
            'r_thn': 'rencana_tahun',
            'p_thn': 'posting_tahun',
            'p_jad': 'posting_jadwal',
            'p_pagu': 'posting_pagu',
            'url_list_u': 'posting_pendidikan_list',
            'url_exec_u': 'posting_pendidikan',
            'url_list_s': 'posting_pendidikan_listsisa',
            'url_exec_s': 'posting_pendidikansisa',
        },
        {
            'id': 'kesehatan',
            'nama': 'DAU SG Kesehatan',
            'singkat': 'Kesehatan',
            'icon': 'fas fa-heartbeat',
            'badge_color': '#0284c7',
            'border_color': '#0284c7',
            'header_bg': 'linear-gradient(135deg, #07192f 0%, #0284c7 100%)',
            'mr_u': RencKes,
            'mp_u': PostKes,
            'mr_s': RencKessisa,
            'mp_s': PostKessisa,
            'r_thn': 'rencana_tahun',
            'p_thn': 'posting_tahun',
            'p_jad': 'posting_jadwal',
            'p_pagu': 'posting_pagu',
            'url_list_u': 'posting_kesehatan_list',
            'url_exec_u': 'posting_kesehatan',
            'url_list_s': 'posting_kesehatan_listsisa',
            'url_exec_s': 'posting_kesehatansisa',
        },
        {
            'id': 'pu',
            'nama': 'DAU SG Pekerjaan Umum',
            'singkat': 'Pekerjaan Umum',
            'icon': 'fas fa-hard-hat',
            'badge_color': '#d97706',
            'border_color': '#d97706',
            'header_bg': 'linear-gradient(135deg, #07192f 0%, #d97706 100%)',
            'mr_u': RencPU,
            'mp_u': PostPU,
            'mr_s': RencPUsisa,
            'mp_s': PostPUsisa,
            'r_thn': 'rencana_tahun',
            'p_thn': 'posting_tahun',
            'p_jad': 'posting_jadwal',
            'p_pagu': 'posting_pagu',
            'url_list_u': 'posting_pu_list',
            'url_exec_u': 'posting_pu',
            'url_list_s': 'posting_pu_listsisa',
            'url_exec_s': 'posting_pusisa',
        },
        {
            'id': 'gajiasn',
            'nama': 'DAU SG Gaji ASN',
            'singkat': 'Gaji ASN',
            'icon': 'fas fa-users',
            'badge_color': '#7c3aed',
            'border_color': '#7c3aed',
            'header_bg': 'linear-gradient(135deg, #07192f 0%, #7c3aed 100%)',
            'mr_u': RencGaji,
            'mp_u': PostGaji,
            'mr_s': RencGajiSisa,
            'mp_s': PostGajiSisa,
            'r_thn': 'rencana_tahun',
            'p_thn': 'posting_tahun',
            'p_jad': 'posting_jadwal',
            'p_pagu': 'posting_pagu',
            'url_list_u': 'posting_gajiasn_list',
            'url_exec_u': 'posting_gajiasn',
            'url_list_s': 'posting_gajiasn_listsisa',
            'url_exec_s': 'posting_gajiasnsisa',
        },
        {
            'id': 'dankel',
            'nama': 'Dana Kelurahan',
            'singkat': 'Dana Kelurahan',
            'icon': 'fas fa-city',
            'badge_color': '#059669',
            'border_color': '#059669',
            'header_bg': 'linear-gradient(135deg, #07192f 0%, #059669 100%)',
            'mr_u': RencDankel,
            'mp_u': RencDankeljadwal,
            'mr_s': RencDankelsisa,
            'mp_s': RencDankeljadwalsisa,
            'r_thn': 'rencdankel_tahun',
            'p_thn': 'rencdankel_tahun',
            'p_jad': 'rencdankel_jadwal',
            'p_pagu': 'rencdankel_pagu',
            'url_list_u': 'posting_list',
            'url_exec_u': 'posting_simpan',
            'url_list_s': 'postingsisa_list',
            'url_exec_s': 'postingsisa_simpan',
        },
    ]

    bidang_list = []
    total_renc_u = 0
    total_post_u = 0
    total_nilai_u = 0
    total_renc_s = 0
    total_post_s = 0
    total_nilai_s = 0

    for b in bidang_defs:
        # Utama
        ru_cnt = b['mr_u'].objects.filter(**{b['r_thn']: tahun}).count()
        fu = {b['p_thn']: tahun}
        if jadwal_aktif:
            fu[b['p_jad']] = jadwal_aktif
        pu_agg = b['mp_u'].objects.filter(**fu).aggregate(c=Count('id'), s=Sum(b['p_pagu']))
        pu_cnt = pu_agg['c'] or 0
        pu_val = pu_agg['s'] or 0

        # Sisa
        r_thn_s = b['r_thn'] if 'rencdankel' not in b['r_thn'] else 'rencdankelsisa_tahun'
        p_thn_s = b['p_thn'] if 'rencdankel' not in b['p_thn'] else 'rencdankelsisa_tahun'
        p_jad_s = b['p_jad'] if 'rencdankel' not in b['p_jad'] else 'rencdankelsisa_jadwal'
        p_pagu_s = b['p_pagu'] if 'rencdankel' not in b['p_pagu'] else 'rencdankelsisa_pagu'

        rs_cnt = b['mr_s'].objects.filter(**{r_thn_s: tahun}).count()
        fs = {p_thn_s: tahun}
        if jadwal_aktif:
            fs[p_jad_s] = jadwal_aktif
        ps_agg = b['mp_s'].objects.filter(**fs).aggregate(c=Count('id'), s=Sum(p_pagu_s))
        ps_cnt = ps_agg['c'] or 0
        ps_val = ps_agg['s'] or 0

        total_renc_u += ru_cnt
        total_post_u += pu_cnt
        total_nilai_u += pu_val
        total_renc_s += rs_cnt
        total_post_s += ps_cnt
        total_nilai_s += ps_val

        # Status logic
        if ru_cnt > 0 and pu_cnt >= ru_cnt:
            status_u = 'synced'
            status_u_label = 'Terposting Lengkap'
            status_u_badge = 'badge-success'
        elif ru_cnt > 0 and pu_cnt > 0:
            status_u = 'partial'
            status_u_label = f'Sebagian ({pu_cnt}/{ru_cnt})'
            status_u_badge = 'badge-info'
        elif ru_cnt > 0 and pu_cnt == 0:
            status_u = 'unposted'
            status_u_label = 'Belum Diposting'
            status_u_badge = 'badge-warning'
        else:
            status_u = 'empty'
            status_u_label = 'Belum Ada Rencana'
            status_u_badge = 'badge-secondary'

        if rs_cnt > 0 and ps_cnt >= rs_cnt:
            status_s = 'synced'
            status_s_label = 'Terposting Lengkap'
            status_s_badge = 'badge-success'
        elif rs_cnt > 0 and ps_cnt > 0:
            status_s = 'partial'
            status_s_label = f'Sebagian ({ps_cnt}/{rs_cnt})'
            status_s_badge = 'badge-info'
        elif rs_cnt > 0 and ps_cnt == 0:
            status_s = 'unposted'
            status_s_label = 'Belum Diposting'
            status_s_badge = 'badge-warning'
        else:
            status_s = 'empty'
            status_s_label = 'Tidak Ada Sisa'
            status_s_badge = 'badge-secondary'

        bidang_list.append({
            'id': b['id'],
            'nama': b['nama'],
            'singkat': b['singkat'],
            'icon': b['icon'],
            'badge_color': b['badge_color'],
            'border_color': b['border_color'],
            'header_bg': b['header_bg'],
            'utama': {
                'label': 'Tahun Berjalan',
                'jml_rencana': ru_cnt,
                'jml_posted': pu_cnt,
                'nilai_posted': pu_val,
                'status': status_u,
                'status_label': status_u_label,
                'status_badge': status_u_badge,
                'url_list': reverse(b['url_list_u']),
                'url_eksekusi': reverse(b['url_exec_u']),
            },
            'sisa': {
                'label': 'Sisa Tahun Lalu',
                'jml_rencana': rs_cnt,
                'jml_posted': ps_cnt,
                'nilai_posted': ps_val,
                'status': status_s,
                'status_label': status_s_label,
                'status_badge': status_s_badge,
                'url_list': reverse(b['url_list_s']),
                'url_eksekusi': reverse(b['url_exec_s']),
            }
        })

    return {
        'bidang_list': bidang_list,
        'jadwal_aktif': jadwal_aktif,
        'total_renc_u': total_renc_u,
        'total_post_u': total_post_u,
        'total_nilai_u': total_nilai_u,
        'total_renc_s': total_renc_s,
        'total_post_s': total_post_s,
        'total_nilai_s': total_nilai_s,
    }


@set_submenu_session
@menu_access_required('list')    
def home(request):
    request.session['next'] = request.get_full_path()

    # Handle Filter Tahun
    tahun_param = request.GET.get('tahun')
    if tahun_param:
        try:
            tahun = int(tahun_param)
            request.session['tahun'] = tahun
            request.session.modified = True
        except (ValueError, TypeError):
            tahun = request.session.get('tahun') or datetime.now().year
    else:
        tahun = request.session.get('tahun') or datetime.now().year

    available_tahun = [
        y for y in Jadwal.objects.values_list('jadwal_tahun', flat=True).distinct().order_by('-jadwal_tahun')
    ]
    if not available_tahun:
        available_tahun = [tahun]
    elif tahun not in available_tahun:
        available_tahun.append(tahun)
        available_tahun.sort(reverse=True)

    dashboard_data = get_posting_dashboard_data(tahun)

    context = {
        'judul': 'Master Posting Rencana Kegiatan',
        'tahun': tahun,
        'available_tahun': available_tahun,
        **dashboard_data,

        # Kompatibilitas mundur
        'tab1': 'Posting Kegiatan Dana Kelurahan Tahun Berjalan',
        'tab2': 'Posting Kegiatan Sisa Dana Kelurahan Tahun Lalu',
        'tab3': 'Posting Kegiatan DAU SG Pendidikan Tahun Berjalan',
        'tab4': 'Posting Kegiatan Sisa DAU SG Pendidikan Tahun Lalu',
        'tab5': 'Posting Kegiatan DAU SG Kesehatan Tahun Berjalan',
        'tab6': 'Posting Kegiatan Sisa DAU SG Kesehatan Tahun Lalu',
        'tab7': 'Posting Kegiatan DAU SG Pekerjaan Umum Tahun Berjalan',
        'tab8': 'Posting Kegiatan Sisa DAU SG Pekerjaan Umum Tahun Lalu',
        'tab9': 'Posting Kegiatan DAU SG Gaji ASN Tahun Berjalan',
        'tab10': 'Posting Kegiatan Sisa DAU SG Gaji ASN Tahun Lalu',
    }
    return render(request, template_home, context)
