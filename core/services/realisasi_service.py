from collections import defaultdict
from decimal import Decimal
from django.db.models import Sum, Max, F, Subquery, OuterRef

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
    Universal Realisasi Service

    PERUBAHAN LOGIKA PAGU (FINAL SESUAI KEBUTUHAN):
    -----------------------------------------------
    - Jadwal TIDAK menjadi parameter input.
    - Sistem otomatis mencari **posting_jadwal tertinggi**
      berdasarkan kombinasi:

        ✔ tahun
        ✔ dana

    - Setelah jadwal tertinggi ditemukan → BARU dilakukan
      penjumlahan nilai pagu.

    Artinya:
        ✔ Konsisten dengan praktik laporan pemerintah
        ✔ Tidak perlu filter jadwal di UI
        ✔ Selalu pakai versi data terbaru yang sah
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
            qs = qs.filter(posting_tahun=tahun)
        if dana:
            qs = qs.filter(posting_dana_id=dana)
        return qs

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
    # AMBIL JADWAL TERTINGGI BERDASARKAN TAHUN & DANA
    # ======================================================

    @classmethod
    def _get_max_jadwal(cls, model, tahun=None, dana=None):
        qs = model.objects.all()

        if tahun:
            qs = qs.filter(posting_tahun=tahun)
        if dana:
            qs = qs.filter(posting_dana_id=dana)
            

        return qs.aggregate(max_jadwal=Max("posting_jadwal_id"))["max_jadwal"]

    # ======================================================
    # TOTAL PAGU (OTOMATIS JADWAL TERBARU)
    # ======================================================

    @classmethod
    def get_total_pagu(cls, tahun=None, dana=None):
        total = Decimal(0)

        for model in cls.PAGU_MODELS:
            base_qs = cls._filter_pagu(model.objects.all(), tahun, dana)

            # subquery ambil jadwal tertinggi per tahun + dana
            max_jadwal_sub = (
                base_qs.values("posting_tahun", "posting_dana_id")
                .annotate(max_jadwal=Max("posting_jadwal_id"))
                .values("max_jadwal")
            )

            qs = base_qs.filter(posting_jadwal_id__in=Subquery(max_jadwal_sub))

            total += qs.aggregate(total=Sum("posting_pagu"))["total"] or Decimal(0)

        return total

    # @classmethod
    # def get_total_pagu(cls, tahun=None, dana=None, debug=False):
    #     total = Decimal(0)

    #     for model in cls.PAGU_MODELS:
    #         max_jadwal = cls._get_max_jadwal(model, tahun, dana)
    #         if not max_jadwal:
    #             continue

    #         qs = cls._filter_pagu(model.objects.all(), tahun, dana)
    #         qs = qs.filter(posting_jadwal_id=max_jadwal)

    #         if debug:
    #             print(f"\nMODEL: {model.__name__}")
    #             subtotal_manual = Decimal(0)

    #             for row in qs.values(
    #                 "id",
    #                 "posting_subopd_id",
    #                 "posting_subkegiatan_id",
    #                 "posting_dana_id",
    #                 "posting_pagu",
    #             ):
    #                 pagu = row["posting_pagu"] or Decimal(0)
    #                 subtotal_manual += pagu
    #                 print(row)

    #             print("SUBTOTAL MANUAL:", subtotal_manual)

    #         total += qs.aggregate(total=Sum("posting_pagu"))["total"] or Decimal(0)

    #     return total
    
    @classmethod
    def debug_rincian_pagu_per_dana(cls, dana_id, tahun=None):
        """
        Cetak rincian lengkap pagu untuk 1 sumber dana tertentu.
        Dipakai untuk audit selisih angka.
        """
        grand_total = Decimal(0)

        for model in cls.PAGU_MODELS:
            base_qs = model.objects.filter(posting_dana_id=dana_id)

            if tahun:
                base_qs = base_qs.filter(posting_tahun=tahun)

            if not base_qs.exists():
                continue

            print(f"\n===== MODEL: {model.__name__} =====")

            # ambil jadwal tertinggi per tahun+dana
            max_jadwal_sub = (
                base_qs.values("posting_tahun", "posting_dana_id")
                .annotate(max_jadwal=Max("posting_jadwal_id"))
            )

            for item in max_jadwal_sub:
                th = item["posting_tahun"]
                jadwal = item["max_jadwal"]

                qs = base_qs.filter(
                    posting_tahun=th,
                    posting_jadwal_id=jadwal,
                )

                subtotal = qs.aggregate(total=Sum("posting_pagu"))["total"] or Decimal(0)
                grand_total += subtotal

                print(f"\nTahun: {th} | Jadwal: {jadwal}")
                print("Subtotal:", subtotal)

                # tampilkan baris detail
                for row in qs.values(
                    "id",
                    "posting_subopd_id",
                    "posting_subkegiatan_id",
                    "posting_pagu",
                ):
                    print(row)

        print("\n==============================")
        print("GRAND TOTAL DANA", dana_id, ":", grand_total)
        print("==============================\n")

        return grand_total

    
    
    @classmethod
    def get_detail_total_pagu_per_dana(cls, tahun=None):
        """
        Menghasilkan rincian total pagu per sumber dana.
        Dipakai untuk audit / deteksi selisih perhitungan.
        """
        hasil = defaultdict(Decimal)

        for model in cls.PAGU_MODELS:
            base_qs = model.objects.all()

            if tahun:
                base_qs = base_qs.filter(posting_tahun=tahun)

            # --- ambil jadwal tertinggi per tahun + dana ---
            max_jadwal_sub = (
                base_qs.values("posting_tahun", "posting_dana_id")
                .annotate(max_jadwal=Max("posting_jadwal_id"))
                .values("max_jadwal")
            )

            qs = base_qs.filter(posting_jadwal_id__in=Subquery(max_jadwal_sub))

            # --- sum per dana ---
            data = (
                qs.values("posting_dana_id")
                .annotate(total=Sum("posting_pagu"))
            )

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

        # ------------------------------
        # PRELOAD PAGU BERDASARKAN JADWAL TERBARU
        # ------------------------------
        pagu_lookup = {}

        for model in cls.PAGU_MODELS:
            max_jadwal = cls._get_max_jadwal(model, tahun, dana)

            if not max_jadwal:
                continue

            qs = cls._filter_pagu(model.objects.all(), tahun, dana)
            qs = qs.filter(posting_jadwal_id=max_jadwal)

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

        # ------------------------------
        # HITUNG REALISASI PER TAHAP
        # ------------------------------
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

        # ------------------------------
        # FORMAT OUTPUT
        # ------------------------------
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
    # REKAP PER TAHAP UNTUK DJPK (TIDAK MENGGANGGU DASHBOARD)
    # ======================================================

    @classmethod
    def get_rekap_per_tahap_djpk(cls):
        """
        Versi khusus DJPK.
        Menghasilkan data:
        - tahun
        - dana_id
        - dana_nama
        - tahap_id
        - tahap_nama
        - pagu
        - realisasi
        - sisa
        """

        from decimal import Decimal
        from django.db.models import Sum

        hasil = {}

        # ===============================
        # HITUNG PAGU TERBARU
        # ===============================
        pagu_lookup = {}

        for model in cls.PAGU_MODELS:
            qs = model.objects.all()

            max_jadwal_sub = (
                qs.values("posting_tahun", "posting_dana_id")
                .annotate(max_jadwal=Max("posting_jadwal_id"))
            )

            for item in max_jadwal_sub:
                tahun = item["posting_tahun"]
                dana_id = item["posting_dana_id"]
                jadwal = item["max_jadwal"]

                subtotal = (
                    qs.filter(
                        posting_tahun=tahun,
                        posting_dana_id=dana_id,
                        posting_jadwal_id=jadwal,
                    )
                    .aggregate(total=Sum("posting_pagu"))["total"]
                    or Decimal(0)
                )

                pagu_lookup[(tahun, dana_id)] = (
                    pagu_lookup.get((tahun, dana_id), Decimal(0)) + subtotal
                )

        # ===============================
        # HITUNG REALISASI PER TAHAP
        # ===============================
        for model in cls.REALISASI_MODELS:
            qs = model.objects.select_related(
                "realisasi_tahap",
                "realisasi_dana",
            )

            for r in qs:
                key = (
                    r.realisasi_tahun,
                    r.realisasi_dana_id,
                    r.realisasi_dana.sub_nama,
                    r.realisasi_tahap_id,
                    r.realisasi_tahap.tahap_dana,
                )

                if key not in hasil:
                    hasil[key] = {
                        "pagu": pagu_lookup.get(
                            (r.realisasi_tahun, r.realisasi_dana_id),
                            Decimal(0),
                        ),
                        "realisasi": Decimal(0),
                    }

                hasil[key]["realisasi"] += r.realisasi_nilai or Decimal(0)

        # ===============================
        # FORMAT OUTPUT
        # ===============================
        data = []

        for key, nilai in hasil.items():
            tahun, dana_id, dana_nama, tahap_id, tahap_nama = key

            data.append({
                "tahun": tahun,
                "dana_id": dana_id,
                "dana_nama": dana_nama,
                "tahap_id": tahap_id,
                "tahap_nama": tahap_nama,
                "pagu": nilai["pagu"],
                "realisasi": nilai["realisasi"],
                "sisa": nilai["pagu"] - nilai["realisasi"],
            })

        return sorted(data, key=lambda x: (x["tahun"], x["dana_nama"], x["tahap_nama"]))


    @classmethod
    def get_rekap_per_opd(cls, tahun=None, dana=None, tahap=None):
        """
        Rekap total realisasi per OPD.
        Dipakai untuk ditampilkan di dashboard samping rekap tahap.
        """
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

        # format list + urutkan terbesar
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
    # DROPDOWN FILTER HELPERS
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
