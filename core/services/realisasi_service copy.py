from decimal import Decimal
from django.db.models import Sum, Max, Q

from pendidikan.models import (
    Realisasi,
    Realisasisisa,
    Rencanaposting,
    Rencanapostingsisa,
)
from kesehatan.models import (
    Realisasikesehatan,
    Realisasikesehatansisa,
    Rencanakesehatanposting,
    Rencanakesehatanpostingsisa,
)
from pu.models import (
    Realisasipu,
    Realisasipusisa,
    Rencanapuposting,
    Rencanapupostingsisa,
)


class RealisasiService:
    """
    Global Realisasi Service (optimized & reusable)

    Fitur:
    - Total pagu (posting terakhir per kombinasi)
    - Total realisasi
    - Sisa anggaran
    - Rekap per tahap
    - Dropdown filter helper
    """

    REALISASI_MODELS = [
        Realisasi,
        Realisasisisa,
        Realisasikesehatan,
        Realisasikesehatansisa,
        Realisasipu,
        Realisasipusisa,
    ]

    PAGU_MODELS = [
        Rencanaposting,
        Rencanapostingsisa,
        Rencanakesehatanposting,
        Rencanakesehatanpostingsisa,
        Rencanapuposting,
        Rencanapupostingsisa,
    ]

    # ==========================================================
    # INTERNAL HELPERS
    # ==========================================================

    @classmethod
    def _filter_realisasi(cls, qs, tahun=None, dana=None, tahap=None):
        if tahun:
            qs = qs.filter(realisasi_tahun=tahun)
        if dana:
            qs = qs.filter(realisasi_dana_id=dana)
        if tahap:
            qs = qs.filter(realisasi_tahap_id=tahap)
        return qs

    @classmethod
    def _filter_pagu(cls, qs, tahun=None, dana=None):
        if tahun:
            qs = qs.filter(posting_tahun=tahun)
        if dana:
            qs = qs.filter(posting_dana_id=dana)
        return qs

    @classmethod
    def _get_last_posting_ids(cls, qs, posting_jadwal=None):
        """
        Ambil ID posting terakhir per kombinasi unik
        dilakukan full di level database (cepat).

        Jika ada filter posting_jadwal → ikut difilter.
        """

        if posting_jadwal is not None:
            qs = qs.filter(posting_jadwal_id=posting_jadwal)

        last_postings = (
            qs.values(
                "posting_subopd_id",
                "posting_subkegiatan_id",
                "posting_dana_id",
                "posting_tahun",
            ).annotate(last_id=Max("id"))
        )

        return [p["last_id"] for p in last_postings]

    # ==========================================================
    # TOTAL REALISASI
    # ==========================================================

    @classmethod
    def get_total_realisasi(cls, tahun=None, dana=None, tahap=None):
        total = Decimal(0)

        for model in cls.REALISASI_MODELS:
            qs = cls._filter_realisasi(model.objects.all(), tahun, dana, tahap)
            total += qs.aggregate(total=Sum("realisasi_nilai"))["total"] or Decimal(0)

        return total

    # ==========================================================
    # TOTAL PAGU (POSTING TERAKHIR)
    # ==========================================================

    @classmethod
    def get_total_pagu(cls, tahun=None, dana=None):
        total = Decimal(0)

        for model in cls.PAGU_MODELS:
            qs = cls._filter_pagu(model.objects.all(), tahun, dana)

            posting_ids = cls._get_last_posting_ids(qs)

            if not posting_ids:
                continue

            total += (
                qs.filter(id__in=posting_ids).aggregate(total=Sum("posting_pagu"))["total"]
                or Decimal(0)
            )

        return total

    # ==========================================================
    # SISA ANGGARAN
    # ==========================================================

    @classmethod
    def get_total_sisa(cls, tahun=None, dana=None, tahap=None):
        return cls.get_total_pagu(tahun, dana) - cls.get_total_realisasi(
            tahun, dana, tahap
        )

    # ==========================================================
    # REKAP PER TAHAP (OPTIMIZED, TANPA N+1 BERAT)
    # ==========================================================

    @classmethod
    def get_rekap_per_tahap(cls, tahun=None, dana=None):
        hasil = {}

        # --- PRELOAD TOTAL PAGU TERAKHIR SEKALI ---
        pagu_lookup = {}

        for model in cls.PAGU_MODELS:
            qs = cls._filter_pagu(model.objects.all(), tahun, dana)
            posting_ids = cls._get_last_posting_ids(qs)

            if not posting_ids:
                continue

            for p in qs.filter(id__in=posting_ids).values(
                "posting_subopd_id",
                "posting_subkegiatan_id",
                "posting_dana_id",
                "posting_tahun",
                "posting_pagu",
            ):
                key = (
                    p["posting_subopd_id"],
                    p["posting_subkegiatan_id"],
                    p["posting_dana_id"],
                    p["posting_tahun"],
                )
                pagu_lookup[key] = pagu_lookup.get(key, Decimal(0)) + (
                    p["posting_pagu"] or Decimal(0)
                )

        # --- HITUNG REALISASI PER TAHAP ---
        for model in cls.REALISASI_MODELS:
            qs = cls._filter_realisasi(
                model.objects.select_related("realisasi_tahap"), tahun, dana, None
            )

            for r in qs:
                pagu_key = (
                    r.realisasi_subopd_id,
                    r.realisasi_subkegiatan_id,
                    r.realisasi_dana_id,
                    r.realisasi_tahun,
                )

                pagu_total = pagu_lookup.get(pagu_key, Decimal(0))

                tahap_key = (r.realisasi_tahap_id, r.realisasi_tahap.tahap_dana)

                if tahap_key not in hasil:
                    hasil[tahap_key] = {"pagu": Decimal(0), "realisasi": Decimal(0)}

                hasil[tahap_key]["pagu"] += pagu_total
                hasil[tahap_key]["realisasi"] += r.realisasi_nilai or Decimal(0)

        # --- FORMAT OUTPUT ---
        data = []

        for (tahap_id, tahap_nama), nilai in sorted(hasil.items(), key=lambda x: x[0][1]):
            data.append(
                {
                    "realisasi_tahap_id": tahap_id,
                    "realisasi_tahap__tahap_dana": tahap_nama,
                    "pagu": nilai["pagu"],
                    "realisasi": nilai["realisasi"],
                    "sisa": nilai["pagu"] - nilai["realisasi"],
                }
            )

        return data

    # ==========================================================
    # DROPDOWN FILTER HELPERS
    # ==========================================================

    @classmethod
    def get_available_tahun(cls):
        tahun_set = set()

        for model in cls.REALISASI_MODELS:
            tahun_set.update(
                model.objects.values_list("realisasi_tahun", flat=True).distinct()
            )

        return sorted(tahun_set, reverse=True)

    @classmethod
    def get_available_dana(cls):
        hasil = {}

        for model in cls.REALISASI_MODELS:
            for r in model.objects.values(
                "realisasi_dana_id", "realisasi_dana__sub_nama"
            ).distinct():
                hasil[r["realisasi_dana_id"]] = r["realisasi_dana__sub_nama"]

        return sorted(hasil.items(), key=lambda x: x[1])

    @classmethod
    def get_available_tahap(cls):
        hasil = {}

        for model in cls.REALISASI_MODELS:
            for r in model.objects.values(
                "realisasi_tahap_id", "realisasi_tahap__tahap_dana"
            ).distinct():
                hasil[r["realisasi_tahap_id"]] = r["realisasi_tahap__tahap_dana"]

        return sorted(hasil.items(), key=lambda x: x[1])
