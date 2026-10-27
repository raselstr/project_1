from datetime import datetime
from django.shortcuts import render
from django.db.models import Q
from project.decorators import menu_access_required, set_submenu_session
from core.services.laporan_sp2d_service import LaporanSp2dService
from core.forms.budget_opd import scoped_opd_id
from opd.models import Subopd, Pejabat
from dana.models import TahapDana


@set_submenu_session
@menu_access_required('list')
def laporan_sp2d_rekap(request):
    """
    Halaman Rekapitulasi Laporan SP2D untuk:
    - Dana Kelurahan
    - Bidang Pendidikan
    - Bidang Kesehatan
    - Bidang Pekerjaan Umum
    Format:
    No - SKPD - Kegiatan - Sub Rincian Kegiatan - Keterangan SP2D - Nomor SP2D - Nominal SP2D - Tanggal SP2D - Output - Satuan Output - Keterangan
    Dilengkapi Sub Total per Kegiatan & Sub Rincian Kegiatan, serta Total Keseluruhan.
    """
    request.session['next'] = request.get_full_path()

    # 1. Tahun: Utamakan dari GET, fallback ke session tahun login
    tahun_session = request.session.get('tahun')
    tahun_param = request.GET.get('tahun')
    if tahun_param:
        try:
            tahun = int(str(tahun_param).replace('.', '').replace(',', '').strip())
        except (ValueError, TypeError):
            tahun = tahun_session or datetime.now().year
    else:
        tahun = tahun_session or datetime.now().year

    # 2. Filter Jenis Dana
    jenis_dana = request.GET.get('dana', 'all')
    if jenis_dana not in ('all', 'dankel', 'pendidikan', 'kesehatan', 'pu'):
        jenis_dana = 'all'

    # 3. Filter Sub OPD (SKPD) dengan scoping akses
    session_subopd = request.session.get('idsubopd')
    scoped_subopd = scoped_opd_id(session_subopd)

    if scoped_subopd:
        subopd_id = scoped_subopd
        is_subopd_locked = True
    else:
        is_subopd_locked = False
        subopd_param = request.GET.get('subopd')
        subopd_id = int(subopd_param) if subopd_param and subopd_param.isdigit() else None

    # 4. Filter Tahap
    tahap_param = request.GET.get('tahap')
    tahap_id = int(tahap_param) if tahap_param and tahap_param.isdigit() else None

    # 5. Filter Sumber (Utama / Sisa / Semua)
    sumber = request.GET.get('sumber', 'all')
    if sumber not in ('all', 'utama', 'sisa'):
        sumber = 'all'

    # 6. Pencarian Keyword q
    q = request.GET.get('q', '').strip()

    level = request.session.get('level')

    # Ambil data dari Service
    report_data = LaporanSp2dService.get_sp2d_report_data(
        tahun=tahun,
        jenis_dana=jenis_dana,
        subopd_id=subopd_id,
        tahap_id=tahap_id,
        sumber=sumber,
        level=level,
        q=q
    )

    # Pilihan Tahun untuk Dropdown
    curr_year = datetime.now().year
    tahun_list = sorted(list(set([curr_year - 2, curr_year - 1, curr_year, curr_year + 1, tahun])), reverse=True)

    # Pilihan Sub OPD untuk Dropdown
    if is_subopd_locked:
        subopd_list = Subopd.objects.filter(id=scoped_subopd)
    else:
        subopd_list = Subopd.objects.all().order_by('sub_nama')

    tahap_list = TahapDana.objects.all().order_by('id')

    context = {
        'judul': 'Laporan SP2D DAU SG & Dana Kelurahan',
        'subjudul': f'Pemerintah Kabupaten Asahan - Tahun Anggaran {tahun}',
        'tahun': tahun,
        'tahun_login': tahun_session,
        'tahun_list': tahun_list,
        'jenis_dana': jenis_dana,
        'dana_choices': LaporanSp2dService.DANA_CHOICES,
        'subopd_id': subopd_id,
        'is_subopd_locked': is_subopd_locked,
        'subopd_list': subopd_list,
        'tahap_id': tahap_id,
        'tahap_list': tahap_list,
        'sumber': sumber,
        'q': q,
        'report_data': report_data,
        'kegiatan_list': report_data['kegiatan_list'],
        'dana_sections': report_data['dana_sections'],
        'grand_total_nominal': report_data['grand_total_nominal'],
        'grand_total_output': report_data['grand_total_output'],
        'grand_total_rencana_output': report_data['grand_total_rencana_output'],
        'total_items': report_data['total_items'],
        'total_kegiatan': report_data['total_kegiatan'],
    }

    return render(request, 'core/laporan_sp2d/laporan_sp2d_list.html', context)


@set_submenu_session
@menu_access_required('list')
def laporan_sp2d_rekap_cetak(request):
    """
    Halaman khusus Cetak / Print Laporan SP2D dengan kop dan tanda tangan pejabat.
    """
    tahun_session = request.session.get('tahun')
    tahun_param = request.GET.get('tahun')
    if tahun_param:
        try:
            tahun = int(str(tahun_param).replace('.', '').replace(',', '').strip())
        except (ValueError, TypeError):
            tahun = tahun_session or datetime.now().year
    else:
        tahun = tahun_session or datetime.now().year

    jenis_dana = request.GET.get('dana', 'all')
    if jenis_dana not in ('all', 'dankel', 'pendidikan', 'kesehatan', 'pu'):
        jenis_dana = 'all'

    session_subopd = request.session.get('idsubopd')
    scoped_subopd = scoped_opd_id(session_subopd)
    if scoped_subopd:
        subopd_id = scoped_subopd
    else:
        subopd_param = request.GET.get('subopd')
        subopd_id = int(subopd_param) if subopd_param and subopd_param.isdigit() else None

    tahap_param = request.GET.get('tahap')
    tahap_id = int(tahap_param) if tahap_param and tahap_param.isdigit() else None
    sumber = request.GET.get('sumber', 'all')
    q = request.GET.get('q', '').strip()
    level = request.session.get('level')

    report_data = LaporanSp2dService.get_sp2d_report_data(
        tahun=tahun,
        jenis_dana=jenis_dana,
        subopd_id=subopd_id,
        tahap_id=tahap_id,
        sumber=sumber,
        level=level,
        q=q
    )

    # Ambil Pejabat untuk Tanda Tangan
    pejabat = None
    if subopd_id:
        pejabat = Pejabat.objects.filter(pejabat_sub_id=subopd_id).first()
    if not pejabat and session_subopd:
        pejabat = Pejabat.objects.filter(pejabat_sub_id=session_subopd).first()
    if not pejabat:
        # Saat tidak ada OPD terpilih (semua OPD): gunakan Sri Lusi dari Data Umum
        pejabat = Pejabat.objects.filter(
            Q(pejabat_nama__icontains='Sri Lusi') | Q(pejabat_nama__icontains='Lusi Masdiany')
        ).first()
        if not pejabat:
            pejabat = Pejabat.objects.first()

    opd_nama = None
    if subopd_id:
        sub_obj = Subopd.objects.filter(id=subopd_id).first()
        if sub_obj:
            opd_nama = sub_obj.sub_nama

    formatted_today = datetime.now().strftime('%d %B %Y')

    context = {
        'judul': 'LAPORAN REALISASI SP2D',
        'subjudul': 'PEMERINTAH KABUPATEN ASAHAN',
        'tahun': tahun,
        'jenis_dana_label': report_data['jenis_dana_label'],
        'opd_nama': opd_nama or 'Seluruh OPD / SKPD Terkait',
        'report_data': report_data,
        'kegiatan_list': report_data['kegiatan_list'],
        'dana_sections': report_data['dana_sections'],
        'grand_total_nominal': report_data['grand_total_nominal'],
        'grand_total_output': report_data['grand_total_output'],
        'grand_total_rencana_output': report_data['grand_total_rencana_output'],
        'total_items': report_data['total_items'],
        'pejabat': pejabat,
        'tanggal_cetak': formatted_today,
    }

    return render(request, 'core/laporan_sp2d/laporan_sp2d_cetak.html', context)


@set_submenu_session
@menu_access_required('list')
def laporan_sp2d_rekap_excel(request):
    """
    Export laporan SP2D ke file Excel (.xlsx).
    """
    tahun_session = request.session.get('tahun')
    tahun_param = request.GET.get('tahun')
    if tahun_param:
        try:
            tahun = int(str(tahun_param).replace('.', '').replace(',', '').strip())
        except (ValueError, TypeError):
            tahun = tahun_session or datetime.now().year
    else:
        tahun = tahun_session or datetime.now().year

    jenis_dana = request.GET.get('dana', 'all')
    if jenis_dana not in ('all', 'dankel', 'pendidikan', 'kesehatan', 'pu'):
        jenis_dana = 'all'

    session_subopd = request.session.get('idsubopd')
    scoped_subopd = scoped_opd_id(session_subopd)
    if scoped_subopd:
        subopd_id = scoped_subopd
    else:
        subopd_param = request.GET.get('subopd')
        subopd_id = int(subopd_param) if subopd_param and subopd_param.isdigit() else None

    tahap_param = request.GET.get('tahap')
    tahap_id = int(tahap_param) if tahap_param and tahap_param.isdigit() else None
    sumber = request.GET.get('sumber', 'all')
    q = request.GET.get('q', '').strip()
    level = request.session.get('level')

    report_data = LaporanSp2dService.get_sp2d_report_data(
        tahun=tahun,
        jenis_dana=jenis_dana,
        subopd_id=subopd_id,
        tahap_id=tahap_id,
        sumber=sumber,
        level=level,
        q=q
    )

    return LaporanSp2dService.export_excel(
        report_data=report_data,
        tahun=tahun,
        jenis_dana_label=report_data['jenis_dana_label']
    )

