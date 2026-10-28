# File: your_app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from django.contrib import messages
import traceback
from ..models import RealisasiDankelsisa, RencDankeljadwalsisa, Subkegiatan, TahapDana, Subopd, RencDankelsisa
from dausg.models import DankelProg, DankelKeg, Dankelsub
from ..forms.form_realisasisisa import RealisasiDankelsisaFilterForm, RealisasiDankelsisaForm
from project.decorators import menu_access_required, set_submenu_session
from opd.models import Pejabat, OpdDana
from penerimaan.models import DistribusiPenerimaan
from datetime import datetime
from core.forms.budget_opd import scoped_opd_id
from core.services.laporan_sp2d_service import LaporanSp2dService
from core.services.laporan_realisasi_excel_service import LaporanRealisasiExcelService


Model_prog = DankelProg
Model_keg = DankelKeg
Model_sub = Dankelsub
Model_rencana = RencDankeljadwalsisa
Model_pagu = RencDankelsisa
Model_realisasi = RealisasiDankelsisa
Form_filter = RealisasiDankelsisaFilterForm
Form_data = RealisasiDankelsisaForm
Model_pejabat = Pejabat

tag_url = 'laporansisa_list'
tag_home = 'laporansisa_home'
template = 'dankel_laporansisa/laporansisa_list.html'
template_filter = 'dankel_laporansisa/laporansisa_filter.html'
template_form = 'dankel_laporansisa/laporansisa_form.html'
template_home = 'dankel_laporansisa/laporansisa_home.html'
sesidana = 'sisa-dana-kelurahan'
Model_penerimaan = DistribusiPenerimaan

def _clean_id(val):
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str in {'', 'None', 'none', 'null', 'NULL', '0'}:
        return None
    try:
        return int(val_str)
    except (ValueError, TypeError):
        return None

def get_from_sessions(request):
    session_data = {
        'idsubopd': request.session.get('idsubopd'),
        'sesitahun': request.session.get('tahun'),
    }
    return session_data

@set_submenu_session
@menu_access_required('list')
def list(request):
    try:
        request.session['next'] = request.get_full_path()
        context = get_data_context(request)
        level = request.session.get('level')
        
        context.update({
            'judul': 'Rekapitulasi Realisasi Sisa Dana Kelurahan',
            'tombol': 'Cetak',
            'tombolsp2d': 'Cetak Daftar SP2D Sisa',
            'tombolexcel': 'Export Excel',
            'level': level
        })
        return render(request, template, context)
    except Exception as e:
        err_msg = traceback.format_exc()
        try:
            with open('/tmp/dankel_laporansisa_error.log', 'w') as f:
                f.write(err_msg)
        except Exception:
            pass
        return HttpResponse(f"<div style='font-family:monospace;padding:20px;background:#ffebee;color:#c62828;border:2px solid #b71c1c;'><h3>Error 500 di Laporan Realisasi Sisa:</h3><pre>{err_msg}</pre></div>", status=500)

@set_submenu_session
@menu_access_required('list')
def excel(request):
    context = get_data_context(request)
    return LaporanRealisasiExcelService.export_dankel_sisa(context)


@set_submenu_session
@menu_access_required('list')    
def filter(request):
    session_data = get_from_sessions(request)
    sesiidopd = session_data.get('idsubopd')
    tahunrencana = request.session.get('tahun')
    request.session['next'] = request.get_full_path()
    # sessions = Session.objects.all()
    # for session in sessions:
    #     print(session.session_key, session.get_decoded())
    
    if request.method == 'GET':
        form = Form_filter(request.GET or None, sesiidopd=sesiidopd, sesidana=sesidana, tahunrencana=tahunrencana)
        if form.is_valid():
            # Simpan data filter di sesi
            request.session['realisasidankelsisa_tahun'] = form.cleaned_data.get('realisasidankelsisa_tahun')
            request.session['realisasidankelsisa_dana'] = form.cleaned_data.get('realisasidankelsisa_dana').id if form.cleaned_data.get('realisasidankelsisa_dana') else None
            request.session['realisasidankelsisa_tahap'] = form.cleaned_data.get('realisasidankelsisa_tahap').id if form.cleaned_data.get('realisasidankelsisa_tahap') else None
            request.session['realisasidankelsisa_subopd'] = form.cleaned_data.get('realisasidankelsisa_subopd').id if form.cleaned_data.get('realisasidankelsisa_subopd') else None
            
            return redirect(tag_url)
    else:
        form = Form_filter(request.GET or None, sesiidopd=sesiidopd, sesidana=sesidana, tahunrencana=tahunrencana)
    
    context = {
        'judul' : 'Laporan Realisasi Sisa Tahun Lalu',
        'tombol' : 'Cari Laporan Realisasi Sisa Tahun Lalu',
        'form': form
        # 'datasisa' : total_pagu_sisa,
    }
    return render(request, template_filter, context)

@set_submenu_session
@menu_access_required('list')
def pdf(request):
    formatted_today = datetime.now().strftime('%d %B %Y')
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    data = Model_pejabat.objects.none()
    
    sesiidopd = _clean_id(request.session.get('realisasidankelsisa_subopd'))
    scoped_sub = scoped_opd_id(sesiidopd) or scoped_opd_id(_clean_id(request.session.get('idsubopd')))
    
    if scoped_sub:
        data = Model_pejabat.objects.filter(pejabat_sub=scoped_sub)
    if not data:
        data = Model_pejabat.objects.filter(
            Q(pejabat_nama__icontains='Sri Lusi') | Q(pejabat_nama__icontains='Lusi Masdiany')
        )
        if not data:
            data = Model_pejabat.objects.all()[:1]
    
    context.update({
        'judul': 'Rekapitulasi Realisasi Sisa Tahun Lalu',
        'tombol': 'Cetak',
        'tanggal': formatted_today,
        'data': data,
    })
    return render(request, 'dankel_laporansisa/laporansisa_pdf.html', context)

@set_submenu_session
@menu_access_required('list')
def apip(request):
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    
    sesiidopd = _clean_id(request.session.get('idsubopd'))
    idopd = _clean_id(request.session.get('realisasidankelsisa_subopd'))
    scoped_sub = scoped_opd_id(idopd) or scoped_opd_id(sesiidopd)
    data = Model_pejabat.objects.none()
    
    if scoped_sub:
        data = Model_pejabat.objects.filter(pejabat_sub=scoped_sub)
    if not data:
        data = Model_pejabat.objects.filter(
            Q(pejabat_nama__icontains='Sri Lusi') | Q(pejabat_nama__icontains='Lusi Masdiany')
        )
        if not data:
            data = Model_pejabat.objects.all()[:1]
    
    penerimaan_filter = Q(distri_penerimaan__penerimaan_dana__sub_slug=sesidana)
    if scoped_sub:
        penerimaan_filter &= Q(distri_subopd_id=scoped_sub)
    penerimaan = Model_penerimaan.objects.filter(penerimaan_filter)
    
    context.update({
        'judul': 'Hasil Reviu APIP Realisasi Sisa Dana Kelurahan',
        'tombol': 'Cetak',
        'data': data,
        'penerimaan': penerimaan,    
    })
    return render(request, 'dankel_laporansisa/laporansisa_apip.html', context)

@set_submenu_session
@menu_access_required('list')
def sp2d(request):
    request.session['next'] = request.get_full_path()
    context = get_data_context(request)
    formatted_today = datetime.now().strftime('%d %B %Y')
    
    tahun_clean = _clean_id(request.session.get('realisasidankelsisa_tahun')) or _clean_id(request.session.get('tahun'))
    tahunrealisasi = tahun_clean if tahun_clean else datetime.now().year
    danarealisasi_id = _clean_id(request.session.get('realisasidankelsisa_dana'))
    tahaprealisasi_id = _clean_id(request.session.get('realisasidankelsisa_tahap'))
    raw_subopd = _clean_id(request.session.get('realisasidankelsisa_subopd'))
    raw_ses_opd = _clean_id(request.session.get('idsubopd'))
    scoped_subopd = scoped_opd_id(raw_subopd) or scoped_opd_id(raw_ses_opd)
    level = request.session.get('level')
    data = Model_pejabat.objects.none()
    
    dana_obj = Subkegiatan.objects.filter(pk=danarealisasi_id).first() if danarealisasi_id else Subkegiatan.objects.filter(sub_slug=sesidana).first()
    tahap_obj = TahapDana.objects.filter(pk=tahaprealisasi_id).first() if tahaprealisasi_id else None
    subopd_obj = Subopd.objects.filter(pk=scoped_subopd).first() if scoped_subopd else (Subopd.objects.filter(pk=raw_subopd).first() if raw_subopd else None)

    filterreals = Q()
    if level != 'Pengguna':
        filterreals &= Q(realisasidankelsisa_verif=1)
    if tahunrealisasi:
        filterreals &= Q(realisasidankelsisa_tahun=tahunrealisasi)
    if dana_obj:
        filterreals &= Q(realisasidankelsisa_dana_id=dana_obj.id)
    if tahaprealisasi_id:
        filterreals &= Q(realisasidankelsisa_tahap_id__in=[*range(1, tahaprealisasi_id + 1)])
    if scoped_subopd:
        filterreals &= Q(realisasidankelsisa_subopd_id=scoped_subopd)
        
    sp2d = Model_realisasi.objects.filter(filterreals)
    if scoped_subopd:
        data = Model_pejabat.objects.filter(pejabat_sub=scoped_subopd)
    if not data:
        data = Model_pejabat.objects.filter(
            Q(pejabat_nama__icontains='Sri Lusi') | Q(pejabat_nama__icontains='Lusi Masdiany')
        )
        if not data:
            data = Model_pejabat.objects.all()[:1]

    report_data = LaporanSp2dService.get_sp2d_report_data(
        tahun=tahunrealisasi,
        jenis_dana='dankel',
        subopd_id=scoped_subopd,
        tahap_id=tahaprealisasi_id,
        sumber='sisa',
        level=level
    )
        
    context.update({
        'judul': 'REKAPITULASI SP2D SISA',
        'subjudul': 'Pemerintah Kabupaten Asahan',
        'sp2d': sp2d,
        'data': data,
        'tanggal': formatted_today,
        'report_data': report_data,
        'kegiatan_list': report_data['kegiatan_list'],
        'grand_total_nominal': report_data['grand_total_nominal'],
        'grand_total_output': report_data['grand_total_output'],
        'grand_total_rencana_output': report_data['grand_total_rencana_output'],
        'total_items': report_data['total_items'],
        'tahunrealisasi': tahunrealisasi,
        'subopdrealisasi_id': subopd_obj.sub_nama if subopd_obj else 'Semua Kelurahan',
        'danarealisasi_id': dana_obj.sub_nama if dana_obj else 'Dana Kelurahan (Sisa)',
        'tahaprealisasi_id': report_data.get('tahap_label', 'Semua Tahap'),
    })
    return render(request, 'dankel_laporansisa/laporansisa_sp2d.html', context)

def get_data_context(request):
    tahun_clean = _clean_id(request.session.get('realisasidankelsisa_tahun')) or _clean_id(request.session.get('tahun'))
    tahunrealisasi = tahun_clean if tahun_clean else datetime.now().year
    danarealisasi_id = _clean_id(request.session.get('realisasidankelsisa_dana'))
    tahaprealisasi_id = _clean_id(request.session.get('realisasidankelsisa_tahap'))
    raw_subopd = _clean_id(request.session.get('realisasidankelsisa_subopd'))
    raw_ses_opd = _clean_id(request.session.get('idsubopd'))
    scoped_subopd = scoped_opd_id(raw_subopd) or scoped_opd_id(raw_ses_opd)
    jadwal = _clean_id(request.session.get('jadwal'))
    level = request.session.get('level')

    dana_obj = Subkegiatan.objects.filter(pk=danarealisasi_id).first() if danarealisasi_id else Subkegiatan.objects.filter(sub_slug=sesidana).first()
    tahap_obj = TahapDana.objects.filter(pk=tahaprealisasi_id).first() if tahaprealisasi_id else None
    subopd_obj = Subopd.objects.filter(pk=scoped_subopd).first() if scoped_subopd else (Subopd.objects.filter(pk=raw_subopd).first() if raw_subopd else None)

    # Buat filter query rencana
    filters = Q()
    if jadwal:
        filters &= Q(rencdankelsisa_jadwal_id=jadwal)
    if tahunrealisasi:
        filters &= Q(rencdankelsisa_tahun=tahunrealisasi)
    if dana_obj:
        filters &= Q(rencdankelsisa_dana_id=dana_obj.id)
    if scoped_subopd:
        filters &= Q(rencdankelsisa_subopd_id=scoped_subopd)
    
    # Buat filter query realisasi
    filterreals = Q()
    if level == 'APIP':
        filterreals &= Q(realisasidankelsisa_verif=1)
    if tahunrealisasi:
        filterreals &= Q(realisasidankelsisa_tahun=tahunrealisasi)
    if dana_obj:
        filterreals &= Q(realisasidankelsisa_dana_id=dana_obj.id)
    if tahaprealisasi_id:
        filterreals &= Q(realisasidankelsisa_tahap_id__in=[*range(1, tahaprealisasi_id + 1)])
    if scoped_subopd:
        filterreals &= Q(realisasidankelsisa_subopd_id=scoped_subopd)
    
    progs = Model_prog.objects.all()
    rencanas = Model_rencana.objects.filter(filters)
    realisasis = Model_realisasi.objects.filter(filterreals)
    

    # Siapkan data untuk template
    prog_data = []
    total_pagu_keseluruhan = 0
    total_output_keseluruhan = 0
    total_realisasi_keseluruhan = 0
    total_realisasi_output_keseluruhan = 0

    for prog in progs:
        total_pagu_prog = 0
        total_output_prog = 0
        total_realisasi_prog = 0
        total_realisasi_output_prog = 0
        prog_kegs = []
        for keg in prog.dankelkegs.all():
            total_pagu_keg = 0
            total_output_keg = 0
            total_realisasi_keg = 0
            total_realisasi_output_keg = 0
            keg_subs = []
            for sub in keg.dankelsubs.all():
                # Ambil rencana terkait dengan sub
                related_rencanas = rencanas.filter(rencdankelsisa_sub=sub)

                # Ambil data pagu dan output
                pagu = 0
                output = 0
                if related_rencanas.exists():
                    pagu_output = related_rencanas.aggregate(
                        total_pagu=Sum('rencdankelsisa_pagu'),
                        total_output=Sum('rencdankelsisa_output')
                    )
                    pagu = pagu_output['total_pagu'] or 0
                    output = pagu_output['total_output'] or 0

                total_pagu_keg += pagu
                total_output_keg += output

                # Ambil realisasi terkait dengan rencana
                total_lpj = 0
                total_output_realisasi = 0
                for rencana in related_rencanas:
                    realisasi_rencana = realisasis.filter(
                        Q(realisasidankelsisa_rencana_id=rencana.id) | Q(realisasidankelsisa_idrencana_id=rencana.rencdankelsisa_id_id)
                    )
                    total_lpj += realisasi_rencana.aggregate(total_lpj=Sum('realisasidankelsisa_lpjnilai'))['total_lpj'] or 0
                    total_output_realisasi += realisasi_rencana.aggregate(total_output=Sum('realisasidankelsisa_output'))['total_output'] or 0
                keg_subs.append({
                    'sub': sub,
                    'pagu': pagu,
                    'output': output,
                    'realisasi': {
                        'total_lpj': total_lpj,
                        'total_output': total_output_realisasi
                    }
                })

                total_realisasi_output_keg += total_output_realisasi
                total_realisasi_keg += total_lpj

            prog_kegs.append({
                'keg': keg,
                'subs': keg_subs,
                'total_pagu_keg': total_pagu_keg,
                'total_output_keg': total_output_keg,
                'total_realisasi_keg': total_realisasi_keg,
                'total_realisasi_output_keg': total_realisasi_output_keg
            })
            total_pagu_prog += total_pagu_keg
            total_output_prog += total_output_keg
            total_realisasi_prog += total_realisasi_keg
            total_realisasi_output_prog += total_realisasi_output_keg
            

        total_pagu_keseluruhan += total_pagu_prog
        total_output_keseluruhan += total_output_prog
        total_realisasi_keseluruhan += total_realisasi_prog
        total_realisasi_output_keseluruhan += total_realisasi_output_keseluruhan

        prog_data.append({
            'prog': prog,
            'kegs': prog_kegs,
            'total_pagu_prog': total_pagu_prog,
            'total_output_prog': total_output_prog,
            'total_realisasi_prog': total_realisasi_prog,
            'total_realisasi_output_prog': total_realisasi_output_prog
        })

    return {
        'prog_data': prog_data,
        'total_pagu_keseluruhan': total_pagu_keseluruhan,
        'total_output_keseluruhan': total_output_keseluruhan,
        'total_realisasi_keseluruhan': total_realisasi_keseluruhan,
        'total_realisasi_output_keseluruhan': total_realisasi_output_keseluruhan,
        'tahunrealisasi': tahunrealisasi,
        'danarealisasi_id': dana_obj,
        'tahaprealisasi_id': tahap_obj,
        'subopdrealisasi_id': subopd_obj,
        'tahunrealisasisisa': tahunrealisasi,
        'danarealisasisisa_id': dana_obj,
        'tahaprealisasisisa_id': tahap_obj,
        'subopdrealisasisisa_id': subopd_obj,
        'jadwal': jadwal
    }
