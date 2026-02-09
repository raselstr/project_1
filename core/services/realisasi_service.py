from decimal import Decimal
from django.db.models import Sum, Q, Max

from pendidikan.models import (
    Realisasi, Realisasisisa, Rencanaposting, Rencanapostingsisa
)
from kesehatan.models import (
    Realisasikesehatan, Realisasikesehatansisa, 
    Rencanakesehatanposting, Rencanakesehatanpostingsisa
)
from pu.models import (
    Realisasipu, Realisasipusisa,
    Rencanapuposting, Rencanapupostingsisa
)


class RealisasiService:
    """
    Service lintas app:
    - Total pagu (posting terakhir per subopd + subkegiatan + dana + tahun)
    - Total realisasi
    - Sisa anggaran
    - Rekap per dana & per tahap
    - Dropdown filter
    """

    # Semua model realisasi
    REALISASI_MODELS = [
        Realisasi, Realisasisisa,
        Realisasikesehatan, Realisasikesehatansisa,
        Realisasipu, Realisasipusisa
    ]

    # Semua model posting
    PAGU_MODELS = [
        Rencanaposting, Rencanapostingsisa,
        Rencanakesehatanposting, Rencanakesehatanpostingsisa,
        Rencanapuposting, Rencanapupostingsisa
    ]

    # ================= FILTER DASAR =================
    @classmethod
    def _filter_queryset(cls, qs, tahun=None, dana=None, tahap=None):
        if tahun:
            qs = qs.filter(realisasi_tahun=tahun)
        if dana:
            qs = qs.filter(realisasi_dana_id=dana)
        if tahap:
            qs = qs.filter(realisasi_tahap_id=tahap)
        return qs

    # ================= TOTAL REALISASI =================
    @classmethod
    def get_total_realisasi(cls, tahun=None, dana=None, tahap=None):
        total = Decimal(0)
        for model in cls.REALISASI_MODELS:
            qs = cls._filter_queryset(model.objects.all(), tahun, dana, tahap)
            total += qs.aggregate(total=Sum("realisasi_nilai"))["total"] or Decimal(0)
        return total

    # ================= TOTAL PAGU =================
    @classmethod
    def get_total_pagu(cls, tahun=None, dana=None, tahap=None):
        """
        Total pagu berdasarkan posting terakhir (id/jadwal tertinggi)
        untuk setiap kombinasi subopd + subkegiatan + dana + tahun
        """
        total = Decimal(0)
        seen_keys = set()

        for model in cls.PAGU_MODELS:
            qs = model.objects.all()
            if tahun:
                qs = qs.filter(posting_tahun=tahun)
            if dana:
                qs = qs.filter(posting_dana_id=dana)

            # urut id descending → ambil posting terakhir
            for p in qs.order_by('posting_subopd', 'posting_subkegiatan', 'posting_dana', 'posting_tahun', '-id'):
                key = (p.posting_subopd_id, p.posting_subkegiatan_id, p.posting_dana_id, p.posting_tahun)
                if key not in seen_keys:
                    total += p.posting_pagu or Decimal(0)
                    seen_keys.add(key)

        return total

    # ================= TOTAL SISA =================
    @classmethod
    def get_total_sisa(cls, tahun=None, dana=None, tahap=None):
        return cls.get_total_pagu(tahun, dana, tahap) - cls.get_total_realisasi(tahun, dana, tahap)

    # ================= REKAP PER TAHAP =================
    @classmethod
    def get_rekap_per_tahap(cls, tahun=None, dana=None):
        hasil = {}

        for model in cls.REALISASI_MODELS:
            qs = cls._filter_queryset(model.objects.all(), tahun, dana, None)
            for r in qs:
                pagu_total = Decimal(0)
                for posting_model in cls.PAGU_MODELS:
                    posting_qs = posting_model.objects.filter(
                        posting_subopd_id=r.realisasi_subopd_id,
                        posting_subkegiatan_id=r.realisasi_subkegiatan_id,
                        posting_dana_id=r.realisasi_dana_id,
                        posting_tahun=r.realisasi_tahun
                    ).order_by('-posting_jadwal')
                    last_posting = posting_qs.first()
                    if last_posting:
                        pagu_total += last_posting.posting_pagu or Decimal(0)

                key = (r.realisasi_tahap_id, r.realisasi_tahap.tahap_dana)
                if key not in hasil:
                    hasil[key] = {"pagu": Decimal(0), "realisasi": Decimal(0)}

                hasil[key]["pagu"] += pagu_total
                hasil[key]["realisasi"] += r.realisasi_nilai or Decimal(0)

        data = []
        for (tahap_id, tahap_nama), nilai in sorted(hasil.items(), key=lambda x: x[0][1]):
            data.append({
                "realisasi_tahap_id": tahap_id,
                "realisasi_tahap__tahap_dana": tahap_nama,
                "pagu": nilai["pagu"],
                "realisasi": nilai["realisasi"],
                "sisa": nilai["pagu"] - nilai["realisasi"]
            })

        return data

    # ================= DROPDOWN FILTER =================
    @classmethod
    def _collect_distinct(cls, field_id, field_name):
        hasil = {}
        for model in cls.REALISASI_MODELS:
            for r in model.objects.values(field_id, field_name).distinct():
                hasil[r[field_id]] = r[field_name]
        return sorted(hasil.items(), key=lambda x: x[1])

    @classmethod
    def get_available_tahun(cls):
        tahun_set = set()
        for model in cls.REALISASI_MODELS:
            tahun_set.update(model.objects.values_list("realisasi_tahun", flat=True).distinct())
        return sorted(tahun_set, reverse=True)

    @classmethod
    def get_available_dana(cls):
        return cls._collect_distinct("realisasi_dana_id", "realisasi_dana__sub_nama")

    @classmethod
    def get_available_tahap(cls):
        return cls._collect_distinct("realisasi_tahap_id", "realisasi_tahap__tahap_dana")
