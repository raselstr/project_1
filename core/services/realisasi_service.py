from collections import defaultdict
from decimal import Decimal
from django.db.models import Sum, F

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
    Universal Realisasi Service (FINAL)

    PERUBAHAN UTAMA:
    ----------------
    - Tidak lagi memakai "jadwal tertinggi"
    - Menggunakan jadwal dengan:
          posting_jadwal__jadwal_aktif = True

    HASIL PERHITUNGAN:
    ------------------
    ✔ Tetap sama secara bisnis
    ✔ Query lebih ringan
    ✔ Lebih aman secara administrasi
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

    # ======================================================
    # INTERNAL FILTER
    # ======================================================

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
            qs = qs.filter(
                posting_tahun=tahun,
                posting_jadwal__jadwal_tahun=tahun,
            )

        if dana:
            qs = qs.filter(posting_dana_id=dana)

        # hanya jadwal aktif pada tahun tersebut
        return qs.filter(posting_jadwal__jadwal_aktif=True)

    # ======================================================
    # TOTAL REALISASI
    # ======================================================

    @classmethod
    def get_total_realisasi(cls, tahun=None, dana=None, tahap=None):
        total = Decimal(0)

        for model in cls.REALISASI_MODELS:
            qs = cls._filter_realisasi(model.objects.all(), tahun, dana, tahap)
            total += qs.aggregate(total=Sum("realisasi_nilai"))["total"] or Decimal(0)

        return total

    # ======================================================
    # TOTAL PAGU (JADWAL AKTIF)
    # ======================================================

    @classmethod
    def get_total_pagu(cls, tahun=None, dana=None):
        total = Decimal(0)

        for model in cls.PAGU_MODELS:
            qs = model.objects.all()

            if dana:
                qs = qs.filter(posting_dana_id=dana)

            # ======================================
            # FILTER HANYA DATA YANG JADWALNYA VALID
            # ======================================
            qs = qs.filter(
                posting_jadwal__isnull=False,          # harus punya relasi
                posting_jadwal__jadwal_aktif=True      # jadwal aktif
            )

            # ===============================
            # JIKA FILTER 1 TAHUN
            # ===============================
            if tahun:
                qs = qs.filter(
                    posting_tahun=tahun,
                    posting_jadwal__jadwal_tahun=tahun,   # tahun harus sama
                )

                total += qs.aggregate(
                    total=Sum("posting_pagu")
                )["total"] or Decimal(0)

            # ===============================
            # JIKA SEMUA TAHUN
            # ===============================
            else:
                data = (
                    qs
                    .filter(posting_jadwal__jadwal_tahun=F("posting_tahun"))
                    .values("posting_tahun")
                    .annotate(total=Sum("posting_pagu"))
                )

                for row in data:
                    total += row["total"] or Decimal(0)

        return total


    # ======================================================
    # DETAIL PAGU PER DANA (UNTUK AUDIT)
    # ======================================================

    @classmethod
    def debug_rincian_pagu_per_dana(cls, dana_id, tahun=None):
        grand_total = Decimal(0)

        for model in cls.PAGU_MODELS:
            qs = model.objects.filter(posting_dana_id=dana_id)

            if tahun:
                qs = qs.filter(posting_tahun=tahun)

            qs = qs.filter(posting_jadwal__jadwal_aktif=True)

            if not qs.exists():
                continue

            print(f"\n===== MODEL: {model.__name__} =====")

            subtotal = qs.aggregate(total=Sum("posting_pagu"))["total"] or Decimal(0)
            grand_total += subtotal

            print("Subtotal:", subtotal)

            for row in qs.values(
                "id",
                "posting_subopd_id",
                "posting_subkegiatan_id",
                "posting_pagu",
                "posting_tahun",
                "posting_jadwal_id",
                "posting_dana_id",
            ):
                print(row)

        print("\n==============================")
        print("GRAND TOTAL DANA", dana_id, ":", grand_total)
        print("==============================\n")

        return grand_total

    # ======================================================
    # TOTAL PAGU PER DANA
    # ======================================================

    @classmethod
    def get_detail_total_pagu_per_dana(cls, tahun=None):
        hasil = defaultdict(Decimal)

        for model in cls.PAGU_MODELS:
            qs = cls._filter_pagu(model.objects.all(), tahun, None)

            data = qs.values("posting_dana_id").annotate(total=Sum("posting_pagu"))

            for row in data:
                hasil[row["posting_dana_id"]] += row["total"] or Decimal(0)

        return dict(hasil)

    # ======================================================
    # SISA ANGGARAN
    # ======================================================

    @classmethod
    def get_total_sisa(cls, tahun=None, dana=None, tahap=None):
        return cls.get_total_pagu(tahun, dana) - cls.get_total_realisasi(
            tahun, dana, tahap
        )

    # ======================================================
    # REKAP PER TAHAP
    # ======================================================

    @classmethod
    def get_rekap_per_tahap(cls, tahun=None, dana=None):
        hasil = {}

        # --- preload pagu aktif ---
        pagu_lookup = {}

        for model in cls.PAGU_MODELS:
            qs = cls._filter_pagu(model.objects.all(), tahun, dana)

            for p in qs.values(
                "posting_subopd_id",
                "posting_subkegiatan_id",
                "posting_dana_id",
                "posting_tahun",
            ).annotate(total_pagu=Sum("posting_pagu")):

                key = (
                    p["posting_subopd_id"],
                    p["posting_subkegiatan_id"],
                    p["posting_dana_id"],
                    p["posting_tahun"],
                )

                pagu_lookup[key] = pagu_lookup.get(key, Decimal(0)) + (
                    p["total_pagu"] or Decimal(0)
                )

        # --- realisasi ---
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

    # ======================================================
    # REKAP PER OPD
    # ======================================================

    @classmethod
    def get_rekap_per_opd(cls, tahun=None, dana=None, tahap=None):
        hasil = defaultdict(Decimal)

        for model in cls.REALISASI_MODELS:
            qs = cls._filter_realisasi(
                model.objects.select_related("realisasi_subopd"),
                tahun,
                dana,
                tahap,
            )

            data = (
                qs.values(
                    "realisasi_subopd_id",
                    "realisasi_subopd__sub_nama",
                )
                .annotate(total=Sum("realisasi_nilai"))
            )

            for row in data:
                key = (
                    row["realisasi_subopd_id"],
                    row["realisasi_subopd__sub_nama"],
                )
                hasil[key] += row["total"] or Decimal(0)

        return sorted(
            [
                {
                    "subopd_id": k[0],
                    "subopd_nama": k[1],
                    "realisasi": v,
                }
                for k, v in hasil.items()
            ],
            key=lambda x: x["realisasi"],
            reverse=True,
        )

    # ======================================================
    # DROPDOWN HELPERS
    # ======================================================

    @classmethod
    def get_available_tahun(cls):
        tahun_set = set()

        for model in cls.PAGU_MODELS:
            tahun_set.update(
                model.objects.values_list("posting_tahun", flat=True).distinct()
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
