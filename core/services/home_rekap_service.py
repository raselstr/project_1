from decimal import Decimal
from django.db.models import Sum, Count, Q

from pagu.models import Pagudausg
from dana.models import Subkegiatan, TahapDana
from opd.models import Subopd
from jadwal.models import Jadwal
from core.forms.budget_opd import scoped_opd_id

from pendidikan.models import (
    Rencana as RencPend,
    Rencanaposting as PostPend,
    Realisasi as RealPend,
)
from kesehatan.models import (
    Rencanakesehatan as RencKes,
    Rencanakesehatanposting as PostKes,
    Realisasikesehatan as RealKes,
)
from pu.models import (
    Rencanapu as RencPU,
    Rencanapuposting as PostPU,
    Realisasipu as RealPU,
)
from dankel.models import (
    RencDankel,
    RencDankeljadwal,
    RealisasiDankel,
)


class HomeRekapService:
    """
    Service untuk menghasilkan data rekapitulasi pada Home Rencana dan Home Realisasi:
    1. Rekap Nilai Rencana (Pagu, Rencana Semula/Induk, Menjadi/Perubahan, Selisih, Sisa Pagu, %)
    2. Rekap Realisasi SP2D per OPD (Nilai SP2D dan Jumlah Berkas SP2D per Tahap serta Total)
    """

    BIDANG_MAP = {
        'pendidikan': {
            'slug': 'dau-dukungan-bidang-pendidikan',
            'renc_model': RencPend,
            'post_model': PostPend,
            'real_model': RealPend,
            'renc_col_opd': 'rencana_subopd',
            'renc_col_pagu': 'rencana_pagu',
            'renc_col_thn': 'rencana_tahun',
            'post_col_opd': 'posting_subopd',
            'post_col_pagu': 'posting_pagu',
            'post_col_jadwal': 'posting_jadwal',
            'post_col_thn': 'posting_tahun',
            'real_col_opd': 'realisasi_subopd',
            'real_col_nilai': 'realisasi_nilai',
            'real_col_tahap': 'realisasi_tahap',
            'real_col_thn': 'realisasi_tahun',
        },
        'kesehatan': {
            'slug': 'dau-dukungan-bidang-kesehatan',
            'renc_model': RencKes,
            'post_model': PostKes,
            'real_model': RealKes,
            'renc_col_opd': 'rencana_subopd',
            'renc_col_pagu': 'rencana_pagu',
            'renc_col_thn': 'rencana_tahun',
            'post_col_opd': 'posting_subopd',
            'post_col_pagu': 'posting_pagu',
            'post_col_jadwal': 'posting_jadwal',
            'post_col_thn': 'posting_tahun',
            'real_col_opd': 'realisasi_subopd',
            'real_col_nilai': 'realisasi_nilai',
            'real_col_tahap': 'realisasi_tahap',
            'real_col_thn': 'realisasi_tahun',
        },
        'pu': {
            'slug': 'dau-dukungan-bidang-pekerjaan-umum',
            'renc_model': RencPU,
            'post_model': PostPU,
            'real_model': RealPU,
            'renc_col_opd': 'rencana_subopd',
            'renc_col_pagu': 'rencana_pagu',
            'renc_col_thn': 'rencana_tahun',
            'post_col_opd': 'posting_subopd',
            'post_col_pagu': 'posting_pagu',
            'post_col_jadwal': 'posting_jadwal',
            'post_col_thn': 'posting_tahun',
            'real_col_opd': 'realisasi_subopd',
            'real_col_nilai': 'realisasi_nilai',
            'real_col_tahap': 'realisasi_tahap',
            'real_col_thn': 'realisasi_tahun',
        },
        'dankel': {
            'slug': 'dana-kelurahan',
            'renc_model': RencDankel,
            'post_model': RencDankeljadwal,
            'real_model': RealisasiDankel,
            'renc_col_opd': 'rencdankel_subopd',
            'renc_col_pagu': 'rencdankel_pagu',
            'renc_col_thn': 'rencdankel_tahun',
            'post_col_opd': 'rencdankel_subopd',
            'post_col_pagu': 'rencdankel_pagu',
            'post_col_jadwal': 'rencdankel_jadwal',
            'post_col_thn': 'rencdankel_tahun',
            'real_col_opd': 'realisasidankel_subopd',
            'real_col_nilai': 'realisasidankel_nilai',
            'real_col_tahap': 'realisasidankel_tahap',
            'real_col_thn': 'realisasidankel_tahun',
        },
    }

    @classmethod
    def get_rekap_rencana(cls, bidang, tahun, subopd_id=None):
        """
        Menghasilkan rekap nilai rencana per OPD termasuk jika terjadi perubahan.
        """
        cfg = cls.BIDANG_MAP.get(bidang.lower())
        if not cfg or not tahun:
            return {}

        dana = Subkegiatan.objects.filter(sub_slug=cfg['slug']).first()
        if not dana:
            return {}

        # Jadwal perubahan check
        tbljadwal = Jadwal.objects.filter(jadwal_tahun=tahun).order_by('id')
        is_perubahan = tbljadwal.count() > 1
        j_induk = tbljadwal.first() if is_perubahan else None
        j_perubahan = tbljadwal.last() if is_perubahan else None

        scoped_opd = scoped_opd_id(subopd_id)

        # Filter pagu per OPD
        pagu_q = Q(pagudausg_tahun=tahun, pagudausg_dana=dana)
        if scoped_opd:
            pagu_q &= Q(pagudausg_opd=scoped_opd)

        pagus = Pagudausg.objects.filter(pagu_q).select_related('pagudausg_opd').order_by('pagudausg_opd__sub_nama')

        rekap_list = []
        tot_pagu = Decimal(0)
        tot_induk = Decimal(0)
        tot_perubahan = Decimal(0)
        tot_selisih = Decimal(0)
        tot_sisa = Decimal(0)

        for p in pagus:
            opd = p.pagudausg_opd
            pagu_val = Decimal(str(p.pagudausg_nilai or 0))
            tot_pagu += pagu_val

            if is_perubahan:
                # 1. Nilai Induk dari jadwal awal
                induk_f = {cfg['post_col_opd']: opd, cfg['post_col_jadwal']: j_induk, cfg['post_col_thn']: tahun}
                if bidang != 'dankel':
                    induk_f['posting_dana'] = dana
                induk_val = cfg['post_model'].objects.filter(**induk_f).aggregate(s=Sum(cfg['post_col_pagu']))['s'] or Decimal(0)

                # 2. Nilai Perubahan dari jadwal akhir
                perub_f = {cfg['post_col_opd']: opd, cfg['post_col_jadwal']: j_perubahan, cfg['post_col_thn']: tahun}
                if bidang != 'dankel':
                    perub_f['posting_dana'] = dana
                perub_val = cfg['post_model'].objects.filter(**perub_f).aggregate(s=Sum(cfg['post_col_pagu']))['s'] or Decimal(0)

                # Fallback jika perubahan belum di-posting, gunakan nilai rencana aktif
                if perub_val == 0:
                    renc_f = {cfg['renc_col_opd']: opd, cfg['renc_col_thn']: tahun}
                    if bidang != 'dankel':
                        renc_f['rencana_dana'] = dana
                    perub_val = cfg['renc_model'].objects.filter(**renc_f).aggregate(s=Sum(cfg['renc_col_pagu']))['s'] or Decimal(0)

                selisih_val = perub_val - induk_val
                rencana_akhir = perub_val
            else:
                renc_f = {cfg['renc_col_opd']: opd, cfg['renc_col_thn']: tahun}
                if bidang != 'dankel':
                    renc_f['rencana_dana'] = dana
                induk_val = cfg['renc_model'].objects.filter(**renc_f).aggregate(s=Sum(cfg['renc_col_pagu']))['s'] or Decimal(0)
                perub_val = induk_val
                selisih_val = Decimal(0)
                rencana_akhir = induk_val

            sisa_val = pagu_val - rencana_akhir
            persen = (float(rencana_akhir) / float(pagu_val) * 100) if pagu_val > 0 else 0.0

            tot_induk += induk_val
            tot_perubahan += perub_val
            tot_selisih += selisih_val
            tot_sisa += sisa_val

            rekap_list.append({
                'opd': opd.sub_nama,
                'pagu': pagu_val,
                'rencana_induk': induk_val,
                'rencana_perubahan': perub_val,
                'selisih': selisih_val,
                'rencana_akhir': rencana_akhir,
                'sisa_pagu': sisa_val,
                'persen': persen,
            })

        tot_akhir = tot_perubahan if is_perubahan else tot_induk
        tot_persen = (float(tot_akhir) / float(tot_pagu) * 100) if tot_pagu > 0 else 0.0

        return {
            'is_perubahan': is_perubahan,
            'jadwal_induk_nama': j_induk.jadwal_keterangan if j_induk else 'Induk',
            'jadwal_perubahan_nama': j_perubahan.jadwal_keterangan if j_perubahan else 'Perubahan APBD',
            'rekap_rencana_list': rekap_list,
            'rekap_rencana_total': {
                'pagu': tot_pagu,
                'induk': tot_induk,
                'perubahan': tot_perubahan,
                'selisih': tot_selisih,
                'sisa': tot_sisa,
                'persen': tot_persen,
            },
        }

    @classmethod
    def get_rekap_realisasi_sp2d(cls, bidang, tahun, subopd_id=None):
        """
        Menghasilkan rekap total nilai SP2D per OPD dan jumlah data SP2D yang diinput setiap tahap.
        """
        cfg = cls.BIDANG_MAP.get(bidang.lower())
        if not cfg or not tahun:
            return {}

        dana = Subkegiatan.objects.filter(sub_slug=cfg['slug']).first()
        tahaps = list(TahapDana.objects.all().order_by('id'))

        base_filter = {cfg['real_col_thn']: tahun}
        if bidang != 'dankel' and dana:
            base_filter['realisasi_dana'] = dana

        scoped_opd = scoped_opd_id(subopd_id)
        if scoped_opd:
            base_filter[f"{cfg['real_col_opd']}_id"] = scoped_opd

        qs = cfg['real_model'].objects.filter(**base_filter)

        # Tahap-tahap yang aktif (minimal 3 tahap ditampilkan: Tahap 1, 2, 3)
        max_tahap = qs.values_list(f"{cfg['real_col_tahap']}_id", flat=True).order_by(f"-{cfg['real_col_tahap']}_id").first() or 3
        active_tahaps = [t for t in tahaps if t.id <= max(max_tahap, 3)]

        opd_ids = list(qs.values_list(f"{cfg['real_col_opd']}_id", flat=True).distinct())
        opds = Subopd.objects.filter(id__in=opd_ids).order_by('sub_nama')

        rekap_list = []
        tahap_totals = {t.id: {'nilai': Decimal(0), 'jumlah': 0} for t in active_tahaps}
        grand_total_nilai = Decimal(0)
        grand_total_jumlah = 0

        for opd in opds:
            opd_qs = qs.filter(**{cfg['real_col_opd']: opd})
            opd_tahap_data = []
            opd_total_nilai = Decimal(0)
            opd_total_jumlah = 0

            for t in active_tahaps:
                t_qs = opd_qs.filter(**{cfg['real_col_tahap']: t})
                t_val = t_qs.aggregate(s=Sum(cfg['real_col_nilai']))['s'] or Decimal(0)
                t_cnt = t_qs.count()

                opd_tahap_data.append({
                    'tahap_id': t.id,
                    'nilai': t_val,
                    'jumlah': t_cnt,
                })
                opd_total_nilai += t_val
                opd_total_jumlah += t_cnt

                tahap_totals[t.id]['nilai'] += t_val
                tahap_totals[t.id]['jumlah'] += t_cnt

            grand_total_nilai += opd_total_nilai
            grand_total_jumlah += opd_total_jumlah

            rekap_list.append({
                'opd': opd.sub_nama,
                'tahap_data': opd_tahap_data,
                'total_nilai': opd_total_nilai,
                'total_jumlah': opd_total_jumlah,
            })

        tahap_headers = [{'id': t.id, 'nama': f'Tahap {t.id}'} for t in active_tahaps]
        tahap_totals_list = [tahap_totals[t.id] for t in active_tahaps]

        return {
            'tahap_headers': tahap_headers,
            'rekap_sp2d_list': rekap_list,
            'rekap_sp2d_total': {
                'tahap_totals': tahap_totals_list,
                'grand_total_nilai': grand_total_nilai,
                'grand_total_jumlah': grand_total_jumlah,
            },
            'total_columns': 2 + (len(active_tahaps) * 2) + 2,
        }

