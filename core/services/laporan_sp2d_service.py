import io
from collections import defaultdict
from decimal import Decimal
from datetime import datetime, date

from django.db.models import Q
from django.http import HttpResponse

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from sipd.models import Sipd, TBP
from dankel.models import RealisasiDankel, RealisasiDankelsisa
from pendidikan.models import Realisasi as RealisasiPend, Realisasisisa as RealisasisisaPend
from kesehatan.models import Realisasikesehatan, Realisasikesehatansisa
from pu.models import Realisasipu, Realisasipusisa


class LaporanSp2dService:

    DANA_CHOICES = [
        ('all', 'Semua Dana (Kelurahan, Pendidikan, Kesehatan, PU)'),
        ('dankel', 'Dana Kelurahan'),
        ('pendidikan', 'Bidang Pendidikan'),
        ('kesehatan', 'Bidang Kesehatan'),
        ('pu', 'Bidang Pekerjaan Umum'),
    ]

    DANA_LABELS = {
        'all': 'Semua Dana (Kelurahan, Pendidikan, Kesehatan, PU)',
        'dankel': 'Dana Kelurahan',
        'pendidikan': 'Bidang Pendidikan',
        'kesehatan': 'Bidang Kesehatan',
        'pu': 'Bidang Pekerjaan Umum',
    }

    @classmethod
    def get_sp2d_keterangan_map(cls, nomor_sp2d_list, tahun=None):
        """
        Mengambil keterangan dokumen SP2D dari tabel SIPD dan TBP.
        """
        if not nomor_sp2d_list:
            return {}

        clean_list = [str(x).strip() for x in nomor_sp2d_list if x and str(x).strip()]
        if not clean_list:
            return {}

        keterangan_map = {}

        # 1. Dari SIPD
        sipd_qs = Sipd.objects.filter(
            nomor_sp2d__in=clean_list
        ).exclude(keterangan_dokumen__isnull=True).exclude(keterangan_dokumen='')

        for s in sipd_qs.values('nomor_sp2d', 'keterangan_dokumen', 'tahun'):
            sp2d = (s.get('nomor_sp2d') or '').strip()
            ket = (s.get('keterangan_dokumen') or '').strip()
            if not ket:
                continue
            if sp2d not in keterangan_map or (tahun and s.get('tahun') == tahun):
                keterangan_map[sp2d] = ket

        # 2. Dari TBP
        tbp_qs = TBP.objects.filter(
            nomor_tbp__in=clean_list
        ).exclude(keterangan_tbp__isnull=True).exclude(keterangan_tbp='')

        for t in tbp_qs.values('nomor_tbp', 'keterangan_tbp', 'tahun'):
            tbp_no = (t.get('nomor_tbp') or '').strip()
            ket = (t.get('keterangan_tbp') or '').strip()
            if not ket:
                continue
            if tbp_no not in keterangan_map or (tahun and t.get('tahun') == tahun):
                keterangan_map[tbp_no] = ket

        return keterangan_map

    @classmethod
    def _extract_dankel_item(cls, r, sumber='Utama'):
        subopd_obj = getattr(r, 'realisasidankelsisa_subopd', None) or getattr(r, 'realisasidankel_subopd', None)
        subopd_nama = subopd_obj.sub_nama if subopd_obj else '-'
        rencana = (
            getattr(r, 'realisasidankelsisa_rencana', None)
            or getattr(r, 'realisasidankelsisa_idrencana', None)
            or getattr(r, 'realisasidankel_rencana', None)
            or getattr(r, 'realisasidankel_idrencana', None)
        )

        if rencana and hasattr(rencana, 'rencdankelsisa_sub'):
            sub_keg = rencana.rencdankelsisa_sub
            keterangan_rencana = getattr(rencana, 'rencdankelsisa_ket', '') or ''
        elif rencana and hasattr(rencana, 'rencdankel_sub'):
            sub_keg = rencana.rencdankel_sub
            keterangan_rencana = getattr(rencana, 'rencdankel_ket', '') or ''
        else:
            sub_keg = None
            keterangan_rencana = ''

        kegiatan_nama = sub_keg.dankelsub_keg.dankelkeg_nama if sub_keg and sub_keg.dankelsub_keg else 'Lainnya'
        sub_rincian_nama = sub_keg.dankelsub_nama if sub_keg else 'Lainnya'
        satuan_output = sub_keg.dankelsub_satuan if sub_keg else ''

        # Tahap
        tahap_obj = getattr(r, 'realisasidankelsisa_tahap', None) or getattr(r, 'realisasidankel_tahap', None)
        tahap_id = getattr(r, 'realisasidankelsisa_tahap_id', None) or getattr(r, 'realisasidankel_tahap_id', None) or (tahap_obj.id if tahap_obj else None)
        tahap_nama = f"Tahap {tahap_id}" if tahap_id else "-"

        # Nilai & Nomor SP2D TU
        sp2d_tu = (getattr(r, 'realisasidankelsisa_sp2dtu', '') or getattr(r, 'realisasidankel_sp2dtu', '') or '').strip()
        raw_sp2d_nilai = getattr(r, 'realisasidankelsisa_nilai', None)
        if raw_sp2d_nilai is None:
            raw_sp2d_nilai = getattr(r, 'realisasidankel_nilai', 0)
        sp2d_tu_nilai = Decimal(str(raw_sp2d_nilai or 0))
        sp2d_tu_tgl = getattr(r, 'realisasidankelsisa_tgl', None) or getattr(r, 'realisasidankel_tgl', None)

        # Nilai & Nomor LPJ (Data utama untuk laporan Dana Kelurahan)
        lpj_no = (getattr(r, 'realisasidankelsisa_lpj', '') or getattr(r, 'realisasidankel_lpj', '') or '').strip()
        raw_lpj_nilai = getattr(r, 'realisasidankelsisa_lpjnilai', None)
        if raw_lpj_nilai is None:
            raw_lpj_nilai = getattr(r, 'realisasidankel_lpjnilai', 0)
        lpj_nilai = Decimal(str(raw_lpj_nilai or 0))
        lpj_tgl = getattr(r, 'realisasidankelsisa_lpjtgl', None) or getattr(r, 'realisasidankel_lpjtgl', None) or sp2d_tu_tgl

        # Sesuai permintaan: Nominal SP2D pada Dana Kelurahan mengambil nilai LPJ,
        # Nomor SP2D diganti menjadi Nomor LPJ, sedangkan No/Nilai/Tgl SP2D TU tetap ditampilkan sebagai info
        nomor_display = lpj_no if lpj_no else sp2d_tu
        nominal_display = lpj_nilai
        tanggal_display = lpj_tgl

        # Ambil rencana_output dan primary key rencana (RencDankel / RencDankelsisa)
        id_rencana = (
            getattr(r, 'realisasidankelsisa_idrencana', None)
            or getattr(r, 'realisasidankelsisa_rencana', None)
            or getattr(r, 'realisasidankel_idrencana', None)
            or getattr(r, 'realisasidankel_rencana', None)
        )
        rencana_output = Decimal(0)
        rencana_pk = getattr(id_rencana, 'pk', None) or getattr(id_rencana, 'id', None)
        rencana_key = f"dankel_{sumber}_{rencana_pk}" if rencana_pk else f"dankel_item_{r.id}"

        if id_rencana:
            if hasattr(id_rencana, 'rencdankelsisa_output'):
                rencana_output = Decimal(str(id_rencana.rencdankelsisa_output or 0))
            elif hasattr(id_rencana, 'rencdankel_output'):
                rencana_output = Decimal(str(id_rencana.rencdankel_output or 0))

        raw_out = getattr(r, 'realisasidankelsisa_output', None)
        if raw_out is None:
            raw_out = getattr(r, 'realisasidankel_output', 0)

        return {
            'id': r.id,
            'skpd': subopd_nama,
            'kegiatan': kegiatan_nama,
            'sub_rincian': sub_rincian_nama,
            'satuan_output': satuan_output,
            'tahap': tahap_nama,
            'tahap_id': tahap_id,
            'nomor_sp2d': nomor_display,
            'nominal_sp2d': nominal_display,
            'tanggal_sp2d': tanggal_display,
            'output': Decimal(str(raw_out or 0)),
            'rencana_output': rencana_output,
            'rencana_key': rencana_key,
            'keterangan': keterangan_rencana or '-',
            'jenis_dana': 'Dana Kelurahan',
            'sumber': sumber,
            'is_dankel': True,
            'sp2d_tu_nomor': sp2d_tu,
            'sp2d_tu_nominal': sp2d_tu_nilai,
            'sp2d_tu_tanggal': sp2d_tu_tgl,
            'lpj_nomor': lpj_no,
            'lpj_nominal': lpj_nilai,
            'lpj_tanggal': lpj_tgl,
        }

    @classmethod
    def _extract_standard_item(cls, r, jenis_dana_name, subkeg_attr, keg_attr, prog_attr, sumber='Utama'):
        subopd_nama = r.realisasi_subopd.sub_nama if getattr(r, 'realisasi_subopd', None) else '-'
        sub_keg = getattr(r, 'realisasi_subkegiatan', None)

        if not sub_keg and getattr(r, 'realisasi_rencanaposting', None):
            sub_keg = getattr(r.realisasi_rencanaposting, 'posting_subkegiatan', None)

        keg_obj = getattr(sub_keg, keg_attr, None) if sub_keg else None
        kegiatan_nama = getattr(keg_obj, keg_attr + '_nama', None) if keg_obj else None
        if not kegiatan_nama and keg_obj:
            kegiatan_nama = str(keg_obj)
        if not kegiatan_nama:
            kegiatan_nama = 'Lainnya'

        sub_rincian_nama = getattr(sub_keg, subkeg_attr + '_nama', 'Lainnya') if sub_keg else 'Lainnya'
        satuan_output = getattr(sub_keg, subkeg_attr + '_satuan', '') if sub_keg else ''

        tahap_obj = getattr(r, 'realisasi_tahap', None)
        tahap_id = getattr(r, 'realisasi_tahap_id', None) or (tahap_obj.id if tahap_obj else None)
        tahap_nama = f"Tahap {tahap_id}" if tahap_id else "-"

        ket_rencana = ''
        if getattr(r, 'realisasi_rencanaposting', None):
            ket_rencana = getattr(r.realisasi_rencanaposting, 'posting_ket', '') or ''
        if not ket_rencana and getattr(r, 'realisasi_rencana', None):
            ket_rencana = getattr(r.realisasi_rencana, 'rencana_ket', '') or ''

        # Ambil rencana_output dan primary key rencana (posting / rencana)
        # Jika primary key berbeda (misal OPD berbeda pada sub rincian), akan dijumlahkan
        rencana_output = Decimal(0)
        rencana_posting = getattr(r, 'realisasi_rencanaposting', None)
        rencana = getattr(r, 'realisasi_rencana', None)
        if rencana_posting:
            rencana_pk = getattr(rencana_posting, 'pk', None) or getattr(rencana_posting, 'id', None)
            rencana_key = f"{jenis_dana_name}_{sumber}_posting_{rencana_pk}"
            rencana_output = Decimal(str(getattr(rencana_posting, 'posting_output', 0) or 0))
        elif rencana:
            rencana_pk = getattr(rencana, 'pk', None) or getattr(rencana, 'id', None)
            rencana_key = f"{jenis_dana_name}_{sumber}_rencana_{rencana_pk}"
            rencana_output = Decimal(str(getattr(rencana, 'rencana_output', 0) or 0))
        else:
            rencana_key = f"{jenis_dana_name}_{sumber}_item_{r.id}"
            rencana_output = Decimal(0)

        return {
            'id': r.id,
            'skpd': subopd_nama,
            'kegiatan': kegiatan_nama,
            'sub_rincian': sub_rincian_nama,
            'satuan_output': satuan_output,
            'tahap': tahap_nama,
            'tahap_id': tahap_id,
            'nomor_sp2d': (r.realisasi_sp2d or '').strip(),
            'nominal_sp2d': Decimal(str(r.realisasi_nilai or 0)),
            'tanggal_sp2d': r.realisasi_tgl,
            'output': Decimal(str(r.realisasi_output or 0)),
            'rencana_output': rencana_output,
            'rencana_key': rencana_key,
            'keterangan': ket_rencana or '-',
            'jenis_dana': jenis_dana_name,
            'sumber': sumber,
            'is_dankel': False,
        }

    @classmethod
    def get_raw_items(cls, tahun, jenis_dana='all', subopd_id=None, tahap_id=None, sumber='all', level=None):
        """
        Mengambil semua record realisasi dan menormalkannya menjadi list of dict.
        Filter tahap_id bersifat kumulatif: jika tahap 2 dipilih, muncul dari tahap 1 s.d. 2.
        """
        items = []

        # Filter tahap kumulatif: Tahap 1 s.d. tahap_id
        tahap_filter_list = None
        if tahap_id:
            try:
                t_int = int(str(tahap_id).strip())
                tahap_filter_list = list(range(1, t_int + 1))
            except (ValueError, TypeError):
                tahap_filter_list = None

        # 1. DANA KELURAHAN
        if jenis_dana in ('all', 'dankel'):
            if sumber in ('all', 'utama'):
                q_dankel = Q(realisasidankel_tahun=tahun)
                if subopd_id:
                    q_dankel &= Q(realisasidankel_subopd_id=subopd_id)
                if tahap_filter_list:
                    q_dankel &= Q(realisasidankel_tahap_id__in=tahap_filter_list)
                if level == 'APIP':
                    q_dankel &= Q(realisasidankel_verif=1)

                qs_dk = RealisasiDankel.objects.filter(q_dankel).select_related(
                    'realisasidankel_subopd',
                    'realisasidankel_tahap',
                    'realisasidankel_rencana__rencdankel_sub__dankelsub_keg',
                    'realisasidankel_idrencana__rencdankel_sub__dankelsub_keg',
                )
                for r in qs_dk:
                    items.append(cls._extract_dankel_item(r, sumber='Utama'))

            if sumber in ('all', 'sisa'):
                q_dankelsisa = Q(realisasidankelsisa_tahun=tahun)
                if subopd_id:
                    q_dankelsisa &= Q(realisasidankelsisa_subopd_id=subopd_id)
                if tahap_filter_list:
                    q_dankelsisa &= Q(realisasidankelsisa_tahap_id__in=tahap_filter_list)
                if level == 'APIP':
                    q_dankelsisa &= Q(realisasidankelsisa_verif=1)

                qs_dksisa = RealisasiDankelsisa.objects.filter(q_dankelsisa).select_related(
                    'realisasidankelsisa_subopd',
                    'realisasidankelsisa_tahap',
                    'realisasidankelsisa_rencana__rencdankelsisa_sub__dankelsub_keg',
                    'realisasidankelsisa_idrencana__rencdankelsisa_sub__dankelsub_keg',
                )
                for r in qs_dksisa:
                    # Map field names for sisa model
                    r_mapped = type('DankelSisaProxy', (), {
                        'id': r.id,
                        'realisasidankel_subopd': r.realisasidankelsisa_subopd,
                        'realisasidankel_tahap': getattr(r, 'realisasidankelsisa_tahap', None),
                        'realisasidankel_tahap_id': getattr(r, 'realisasidankelsisa_tahap_id', None),
                        'realisasidankel_rencana': r.realisasidankelsisa_rencana,
                        'realisasidankel_idrencana': getattr(r, 'realisasidankelsisa_idrencana', None),
                        'realisasidankel_sp2dtu': r.realisasidankelsisa_sp2dtu,
                        'realisasidankel_nilai': r.realisasidankelsisa_nilai,
                        'realisasidankel_tgl': r.realisasidankelsisa_tgl,
                        'realisasidankel_lpj': getattr(r, 'realisasidankelsisa_lpj', ''),
                        'realisasidankel_lpjnilai': getattr(r, 'realisasidankelsisa_lpjnilai', 0),
                        'realisasidankel_lpjtgl': getattr(r, 'realisasidankelsisa_lpjtgl', None),
                        'realisasidankel_output': r.realisasidankelsisa_output,
                    })()
                    items.append(cls._extract_dankel_item(r_mapped, sumber='Sisa'))

        # Helper for Pendidikan, Kesehatan, PU
        def fetch_standard(model_main, model_sisa, dana_name, subkeg_attr, keg_attr, prog_attr):
            std_items = []
            if sumber in ('all', 'utama'):
                q = Q(realisasi_tahun=tahun)
                if subopd_id:
                    q &= Q(realisasi_subopd_id=subopd_id)
                if tahap_filter_list:
                    q &= Q(realisasi_tahap_id__in=tahap_filter_list)
                if level == 'APIP':
                    q &= Q(realisasi_verif=1)

                qs = model_main.objects.filter(q).select_related(
                    'realisasi_subopd',
                    'realisasi_tahap',
                    'realisasi_subkegiatan__' + keg_attr,
                    'realisasi_rencanaposting',
                    'realisasi_rencana',
                )
                for r in qs:
                    std_items.append(cls._extract_standard_item(r, dana_name, subkeg_attr, keg_attr, prog_attr, sumber='Utama'))

            if sumber in ('all', 'sisa'):
                q_s = Q(realisasi_tahun=tahun)
                if subopd_id:
                    q_s &= Q(realisasi_subopd_id=subopd_id)
                if tahap_filter_list:
                    q_s &= Q(realisasi_tahap_id__in=tahap_filter_list)
                if level == 'APIP':
                    q_s &= Q(realisasi_verif=1)

                qs_s = model_sisa.objects.filter(q_s).select_related(
                    'realisasi_subopd',
                    'realisasi_tahap',
                    'realisasi_subkegiatan__' + keg_attr,
                    'realisasi_rencanaposting',
                    'realisasi_rencana',
                )
                for r in qs_s:
                    std_items.append(cls._extract_standard_item(r, dana_name, subkeg_attr, keg_attr, prog_attr, sumber='Sisa'))

            return std_items

        # 2. PENDIDIKAN
        if jenis_dana in ('all', 'pendidikan'):
            items.extend(fetch_standard(
                RealisasiPend, RealisasisisaPend,
                'Bidang Pendidikan',
                'dausgpendidikansub', 'dausgpendidikansub_keg', 'dausgpendidikankeg_prog'
            ))

        # 3. KESEHATAN
        if jenis_dana in ('all', 'kesehatan'):
            items.extend(fetch_standard(
                Realisasikesehatan, Realisasikesehatansisa,
                'Bidang Kesehatan',
                'dausgkesehatansub', 'dausgkesehatansub_keg', 'dausgkesehatankeg_prog'
            ))

        # 4. PEKERJAAN UMUM
        if jenis_dana in ('all', 'pu'):
            items.extend(fetch_standard(
                Realisasipu, Realisasipusisa,
                'Bidang Pekerjaan Umum',
                'dausgpusub', 'dausgpusub_keg', 'dausgpukeg_prog'
            ))

        # Enrich dengan Keterangan SP2D dari SIPD / TBP
        sp2d_numbers = [item['nomor_sp2d'] for item in items if item.get('nomor_sp2d')]
        keterangan_map = cls.get_sp2d_keterangan_map(sp2d_numbers, tahun=tahun)

        for item in items:
            sp2d_no = item.get('nomor_sp2d', '')
            item['keterangan_sp2d'] = keterangan_map.get(sp2d_no, '-')

        return items

    @classmethod
    def group_report_data(cls, items):
        """
        Mengelompokkan data berdasarkan:
        Kegiatan -> Sub Rincian Kegiatan -> Items
        Menghitung:
        - Sub Total per Sub Rincian Kegiatan (Nominal SP2D & Output)
        - Sub Total per Kegiatan (Nominal SP2D & Output)
        - Total Keseluruhan (Grand Total Nominal SP2D & Output)
        """
        # Dictionary hierarki:
        # groups[kegiatan_nama][sub_rincian_nama] = {
        #     'satuan': '...',
        #     'items': [...]
        # }
        groups = defaultdict(lambda: defaultdict(lambda: {'satuan': '', 'items': []}))

        for it in items:
            keg_nama = it.get('kegiatan') or 'Lainnya'
            sub_nama = it.get('sub_rincian') or 'Lainnya'
            satuan = it.get('satuan_output') or ''

            groups[keg_nama][sub_nama]['items'].append(it)
            if satuan and not groups[keg_nama][sub_nama]['satuan']:
                groups[keg_nama][sub_nama]['satuan'] = satuan

        running_no = 1
        grand_total_nominal = Decimal(0)
        grand_total_output = Decimal(0)
        grand_total_rencana_output = Decimal(0)
        total_items_count = 0

        kegiatan_list = []

        # Sort kegiatan by name
        for keg_nama in sorted(groups.keys()):
            sub_map = groups[keg_nama]
            sub_list = []
            keg_total_nominal = Decimal(0)
            keg_total_output = Decimal(0)
            keg_total_rencana_output = Decimal(0)

            # Sort sub rincian by name
            for sub_nama in sorted(sub_map.keys()):
                sub_info = sub_map[sub_nama]
                raw_sub_items = sub_info['items']

                # Sort items by tanggal_sp2d (ascending), then nomor_sp2d
                sorted_items = sorted(
                    raw_sub_items,
                    key=lambda x: (
                        x['tanggal_sp2d'] if isinstance(x.get('tanggal_sp2d'), (date, datetime)) else date.min,
                        x.get('nomor_sp2d', '')
                    )
                )

                sub_nominal = Decimal(0)
                sub_output = Decimal(0)
                # Rencana output: jika primary key berbeda (misal beda OPD), jumlahkan nilainya.
                # Jika primary key sama (beberapa SP2D dari posting/rencana yang sama), dihitung satu kali.
                sub_rencana_map = {}

                for item in sorted_items:
                    item['no'] = running_no
                    running_no += 1
                    total_items_count += 1

                    nom = item.get('nominal_sp2d') or Decimal(0)
                    out = item.get('output') or Decimal(0)
                    ro = item.get('rencana_output') or Decimal(0)
                    r_key = item.get('rencana_key')

                    sub_nominal += nom
                    sub_output += out

                    if r_key and r_key not in sub_rencana_map:
                        sub_rencana_map[r_key] = ro

                sub_rencana_output = sum(sub_rencana_map.values()) if sub_rencana_map else Decimal(0)

                sub_list.append({
                    'sub_rincian_nama': sub_nama,
                    'satuan': sub_info['satuan'],
                    'items': sorted_items,
                    'subtotal_nominal': sub_nominal,
                    'subtotal_output': sub_output,
                    'subtotal_rencana_output': sub_rencana_output,
                })

                keg_total_nominal += sub_nominal
                keg_total_output += sub_output
                keg_total_rencana_output += sub_rencana_output

            kegiatan_list.append({
                'kegiatan_nama': keg_nama,
                'sub_rincian_list': sub_list,
                'subtotal_nominal': keg_total_nominal,
                'subtotal_output': keg_total_output,
                'subtotal_rencana_output': keg_total_rencana_output,
            })

            grand_total_nominal += keg_total_nominal
            grand_total_output += keg_total_output
            grand_total_rencana_output += keg_total_rencana_output

        return {
            'kegiatan_list': kegiatan_list,
            'grand_total_nominal': grand_total_nominal,
            'grand_total_output': grand_total_output,
            'grand_total_rencana_output': grand_total_rencana_output,
            'total_items': total_items_count,
            'total_kegiatan': len(kegiatan_list),
        }

    @classmethod
    def get_sp2d_report_data(cls, tahun, jenis_dana='all', subopd_id=None, tahap_id=None, sumber='all', level=None, q=None):
        """
        Fungsi utama untuk mengambil seluruh data laporan SP2D dengan subtotal dan total.
        Mendukung grouping per Kegiatan & Sub Rincian Kegiatan,
        serta grouping per Dana jika jenis_dana='all'.
        """
        raw_items = cls.get_raw_items(
            tahun=tahun,
            jenis_dana=jenis_dana,
            subopd_id=subopd_id,
            tahap_id=tahap_id,
            sumber=sumber,
            level=level
        )

        # Filter pencarian keyword q jika ada
        if q and str(q).strip():
            q_clean = str(q).strip().lower()
            raw_items = [
                it for it in raw_items
                if q_clean in (it.get('nomor_sp2d') or '').lower()
                or q_clean in (it.get('keterangan_sp2d') or '').lower()
                or q_clean in (it.get('kegiatan') or '').lower()
                or q_clean in (it.get('sub_rincian') or '').lower()
                or q_clean in (it.get('skpd') or '').lower()
            ]

        # Group data secara keseluruhan
        grouped = cls.group_report_data(raw_items)

        # Jika jenis_dana='all', buat juga dana_sections (per Dana)
        dana_sections = []
        if jenis_dana == 'all':
            dana_names = [
                ('dankel', 'Dana Kelurahan'),
                ('pendidikan', 'Bidang Pendidikan'),
                ('kesehatan', 'Bidang Kesehatan'),
                ('pu', 'Bidang Pekerjaan Umum'),
            ]
            for d_key, d_name in dana_names:
                d_items = [it for it in raw_items if it.get('jenis_dana') == d_name]
                if d_items:
                    d_grouped = cls.group_report_data(d_items)
                    dana_sections.append({
                        'dana_key': d_key,
                        'dana_nama': d_name,
                        'kegiatan_list': d_grouped['kegiatan_list'],
                        'total_nominal': d_grouped['grand_total_nominal'],
                        'total_output': d_grouped['grand_total_output'],
                        'total_rencana_output': d_grouped['grand_total_rencana_output'],
                        'total_items': d_grouped['total_items'],
                    })

        tahap_label = "Semua Tahap (Tahap 1 s.d. 5)"
        if tahap_id:
            try:
                t_int = int(str(tahap_id).strip())
                tahap_label = f"Tahap 1 s.d. Tahap {t_int}"
            except (ValueError, TypeError):
                tahap_label = f"Tahap {tahap_id}"

        return {
            'tahun': tahun,
            'jenis_dana': jenis_dana,
            'jenis_dana_label': cls.DANA_LABELS.get(jenis_dana, 'Semua Dana'),
            'subopd_id': subopd_id,
            'tahap_id': tahap_id,
            'tahap_label': tahap_label,
            'sumber': sumber,
            'kegiatan_list': grouped['kegiatan_list'],
            'grand_total_nominal': grouped['grand_total_nominal'],
            'grand_total_output': grouped['grand_total_output'],
            'grand_total_rencana_output': grouped['grand_total_rencana_output'],
            'total_items': grouped['total_items'],
            'total_kegiatan': grouped['total_kegiatan'],
            'dana_sections': dana_sections,
            'raw_items_count': len(raw_items),
        }

    @classmethod
    def export_excel(cls, report_data, tahun, jenis_dana_label='Semua Dana'):
        """
        Menghasilkan file Excel (.xlsx) dengan format laporan SP2D lengkap:
        No - SKPD - Kegiatan - Sub Rincian Kegiatan - Keterangan SP2D - Nomor SP2D - Nominal SP2D - Tanggal SP2D - Output - Satuan Output - Keterangan
        Termasuk baris Sub Total per Sub Rincian Kegiatan, Sub Total per Kegiatan, dan Total Keseluruhan.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Laporan SP2D"
        ws.views.sheetView[0].showGridLines = True

        # Styles
        font_title = Font(name="Calibri", size=14, bold=True, color="1F4E78")
        font_subtitle = Font(name="Calibri", size=11, bold=True, color="333333")
        font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        font_data = Font(name="Calibri", size=10)
        font_subtotal_sub = Font(name="Calibri", size=10, bold=True, color="7F6000")
        font_subtotal_keg = Font(name="Calibri", size=10, bold=True, color="1F4E78")
        font_grand_total = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

        fill_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        fill_subtotal_sub = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
        fill_subtotal_keg = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
        fill_grand_total = PatternFill(start_color="203764", end_color="203764", fill_type="solid")

        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
        align_right = Alignment(horizontal="right", vertical="center")

        thin_side = Side(border_style="thin", color="D9D9D9")
        dark_side = Side(border_style="thin", color="000000")
        double_side = Side(border_style="double", color="000000")

        border_cell = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
        border_subtotal = Border(left=dark_side, right=dark_side, top=dark_side, bottom=dark_side)
        border_grand_total = Border(left=dark_side, right=dark_side, top=dark_side, bottom=double_side)

        # Header Titles
        ws.merge_cells("A1:M1")
        ws["A1"] = "PEMERINTAH KABUPATEN ASAHAN"
        ws["A1"].font = font_title
        ws["A1"].alignment = align_center

        ws.merge_cells("A2:M2")
        ws["A2"] = f"LAPORAN REALISASI SP2D - TAHUN ANGGARAN {tahun}"
        ws["A2"].font = font_subtitle
        ws["A2"].alignment = align_center

        tahap_label = report_data.get('tahap_label', '')
        ws.merge_cells("A3:M3")
        ws["A3"] = f"SUMBER DANA: {jenis_dana_label.upper()}" + (f"  |  {tahap_label}" if tahap_label else "")
        ws["A3"].font = font_subtitle
        ws["A3"].alignment = align_center

        ws.append([])  # Baris 4 kosong

        # Table Column Headers (13 kolom: tambah Tahap)
        headers = [
            "No",
            "SKPD",
            "Kegiatan",
            "Sub Rincian Kegiatan",
            "Tahap",
            "Keterangan SP2D",
            "Nomor SP2D",
            "Nominal SP2D (Rp)",
            "Tanggal SP2D",
            "Rencana Output",
            "Output",
            "Satuan Output",
            "Keterangan"
        ]
        ws.append(headers)
        header_row = 5

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=header_row, column=col_idx)
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = align_center
            cell.border = border_subtotal

        current_row = 6
        kegiatan_list = report_data.get('kegiatan_list', [])

        for keg in kegiatan_list:
            for sub in keg.get('sub_rincian_list', []):
                for it in sub.get('items', []):
                    tgl_str = ''
                    if isinstance(it.get('tanggal_sp2d'), (date, datetime)):
                        tgl_str = it['tanggal_sp2d'].strftime('%d/%m/%Y')

                    # Nomor SP2D: Untuk dana kelurahan, tampilkan info LPJ + SP2D TU
                    nomor_display = it.get('nomor_sp2d', '-')
                    if it.get('is_dankel') and it.get('sp2d_tu_nomor'):
                        tgl_tu_str = ''
                        tgl_tu = it.get('sp2d_tu_tanggal')
                        if isinstance(tgl_tu, (date, datetime)):
                            tgl_tu_str = tgl_tu.strftime('%d/%m/%Y')
                        sp2d_tu_nominal = float(it.get('sp2d_tu_nominal') or 0)
                        nomor_display = (
                            f"LPJ: {nomor_display}\n"
                            f"(SP2D TU: {it.get('sp2d_tu_nomor', '-')} | "
                            f"Rp {sp2d_tu_nominal:,.2f} | Tgl {tgl_tu_str})"
                        )

                    row_vals = [
                        it.get('no', ''),
                        it.get('skpd', '-'),
                        it.get('kegiatan', '-'),
                        it.get('sub_rincian', '-'),
                        it.get('tahap', '-'),
                        it.get('keterangan_sp2d', '-'),
                        nomor_display,
                        float(it.get('nominal_sp2d') or 0),
                        tgl_str,
                        float(it.get('rencana_output') or 0),
                        float(it.get('output') or 0),
                        it.get('satuan_output', '-'),
                        it.get('keterangan', '-')
                    ]
                    ws.append(row_vals)

                    # Styling baris data (13 kolom)
                    for c_idx in range(1, 14):
                        cell = ws.cell(row=current_row, column=c_idx)
                        cell.font = font_data
                        cell.border = border_cell

                        if c_idx in (1, 5, 9, 12):
                            cell.alignment = align_center
                        elif c_idx in (8, 10, 11):
                            cell.alignment = align_right
                            cell.number_format = '#,##0.00'
                        else:
                            cell.alignment = align_left

                    # Baris SP2D TU dankel bisa tinggi — wrap text untuk kolom nomor SP2D (col 7)
                    ws.cell(row=current_row, column=7).alignment = Alignment(
                        horizontal="left", vertical="top", wrap_text=True
                    )

                    current_row += 1

                # Sub Total Sub Rincian Kegiatan (13 kolom)
                ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=7)
                cell_lbl = ws.cell(row=current_row, column=1)
                cell_lbl.value = f"Sub Total Sub Rincian: {sub.get('sub_rincian_nama', '')}"
                cell_lbl.font = font_subtotal_sub
                cell_lbl.alignment = Alignment(horizontal="right", vertical="center")

                cell_nom = ws.cell(row=current_row, column=8)
                cell_nom.value = float(sub.get('subtotal_nominal') or 0)
                cell_nom.font = font_subtotal_sub
                cell_nom.alignment = align_right
                cell_nom.number_format = '#,##0.00'

                ws.cell(row=current_row, column=9).value = ""

                cell_renc_out = ws.cell(row=current_row, column=10)
                cell_renc_out.value = float(sub.get('subtotal_rencana_output') or 0)
                cell_renc_out.font = font_subtotal_sub
                cell_renc_out.alignment = align_right
                cell_renc_out.number_format = '#,##0.00'

                cell_out = ws.cell(row=current_row, column=11)
                cell_out.value = float(sub.get('subtotal_output') or 0)
                cell_out.font = font_subtotal_sub
                cell_out.alignment = align_right
                cell_out.number_format = '#,##0.00'

                cell_sat = ws.cell(row=current_row, column=12)
                cell_sat.value = sub.get('satuan', '')
                cell_sat.font = font_subtotal_sub
                cell_sat.alignment = align_center

                ws.cell(row=current_row, column=13).value = ""

                for c_idx in range(1, 14):
                    c = ws.cell(row=current_row, column=c_idx)
                    c.fill = fill_subtotal_sub
                    c.border = border_subtotal

                current_row += 1

            # Sub Total Kegiatan
            ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=7)
            cell_lbl_keg = ws.cell(row=current_row, column=1)
            cell_lbl_keg.value = f"SUB TOTAL KEGIATAN: {keg.get('kegiatan_nama', '')}"
            cell_lbl_keg.font = font_subtotal_keg
            cell_lbl_keg.alignment = Alignment(horizontal="right", vertical="center")

            cell_nom_keg = ws.cell(row=current_row, column=8)
            cell_nom_keg.value = float(keg.get('subtotal_nominal') or 0)
            cell_nom_keg.font = font_subtotal_keg
            cell_nom_keg.alignment = align_right
            cell_nom_keg.number_format = '#,##0.00'

            ws.cell(row=current_row, column=9).value = ""

            cell_renc_out_keg = ws.cell(row=current_row, column=10)
            cell_renc_out_keg.value = float(keg.get('subtotal_rencana_output') or 0)
            cell_renc_out_keg.font = font_subtotal_keg
            cell_renc_out_keg.alignment = align_right
            cell_renc_out_keg.number_format = '#,##0.00'

            cell_out_keg = ws.cell(row=current_row, column=11)
            cell_out_keg.value = float(keg.get('subtotal_output') or 0)
            cell_out_keg.font = font_subtotal_keg
            cell_out_keg.alignment = align_right
            cell_out_keg.number_format = '#,##0.00'

            ws.cell(row=current_row, column=12).value = ""
            ws.cell(row=current_row, column=13).value = ""

            for c_idx in range(1, 14):
                c = ws.cell(row=current_row, column=c_idx)
                c.fill = fill_subtotal_keg
                c.border = border_subtotal

            current_row += 1

        # Grand Total
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=7)
        cell_lbl_gt = ws.cell(row=current_row, column=1)
        cell_lbl_gt.value = "TOTAL KESELURUHAN"
        cell_lbl_gt.font = font_grand_total
        cell_lbl_gt.alignment = Alignment(horizontal="right", vertical="center")

        cell_nom_gt = ws.cell(row=current_row, column=8)
        cell_nom_gt.value = float(report_data.get('grand_total_nominal') or 0)
        cell_nom_gt.font = font_grand_total
        cell_nom_gt.alignment = align_right
        cell_nom_gt.number_format = '#,##0.00'

        ws.cell(row=current_row, column=9).value = ""

        cell_renc_out_gt = ws.cell(row=current_row, column=10)
        cell_renc_out_gt.value = float(report_data.get('grand_total_rencana_output') or 0)
        cell_renc_out_gt.font = font_grand_total
        cell_renc_out_gt.alignment = align_right
        cell_renc_out_gt.number_format = '#,##0.00'

        cell_out_gt = ws.cell(row=current_row, column=11)
        cell_out_gt.value = float(report_data.get('grand_total_output') or 0)
        cell_out_gt.font = font_grand_total
        cell_out_gt.alignment = align_right
        cell_out_gt.number_format = '#,##0.00'

        ws.cell(row=current_row, column=12).value = ""
        ws.cell(row=current_row, column=13).value = ""

        for c_idx in range(1, 14):
            c = ws.cell(row=current_row, column=c_idx)
            c.fill = fill_grand_total
            c.border = border_grand_total

        # Set Column Widths (13 kolom)
        column_widths = {
            'A': 6,    # No
            'B': 22,   # SKPD
            'C': 30,   # Kegiatan
            'D': 30,   # Sub Rincian Kegiatan
            'E': 8,    # Tahap
            'F': 42,   # Keterangan SP2D
            'G': 35,   # Nomor SP2D
            'H': 20,   # Nominal SP2D
            'I': 14,   # Tanggal SP2D
            'J': 14,   # Rencana Output
            'K': 12,   # Output
            'L': 14,   # Satuan Output
            'M': 28,   # Keterangan
        }
        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width

        # Simpan ke buffer memory dan kembalikan HttpResponse
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        filename = f"Laporan_SP2D_{tahun}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

