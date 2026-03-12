from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum, Q

from dana.models import TahapDana

from pendidikan.models import (
    Realisasi,
    Realisasisisa,
)

from kesehatan.models import (
    Realisasikesehatan,
    Realisasikesehatansisa,
)

from pu.models import (
    Realisasipu,
    Realisasipusisa,
)

from dankel.models import (
    RealisasiDankel,
    RealisasiDankelsisa,
)


class   RealisasiService:

    COMMON_REALISASI_FIELDS = {
        "tahun": "realisasi_tahun",
        "dana": "realisasi_dana",
        "subopd": "realisasi_subopd_id",
        "subkegiatan": "realisasi_subkegiatan_id",
        "nilai": "realisasi_nilai",
        "tahap": "realisasi_tahap_id",
    }

    REALISASI_MODELS = {
        Realisasi: COMMON_REALISASI_FIELDS,
        Realisasisisa: COMMON_REALISASI_FIELDS,
        Realisasikesehatan: COMMON_REALISASI_FIELDS,
        Realisasikesehatansisa: COMMON_REALISASI_FIELDS,
        Realisasipu: COMMON_REALISASI_FIELDS,
        Realisasipusisa: COMMON_REALISASI_FIELDS,

        RealisasiDankel: {
            "tahun": "realisasidankel_tahun",
            "dana": "realisasidankel_dana_id",
            "subopd": "realisasidankel_subopd_id",
            "subkegiatan": "realisasidankel_rencana_id",
            "nilai": "realisasidankel_lpjnilai",
            "tahap": "realisasidankel_tahap_id",
        },

        RealisasiDankelsisa: {
            "tahun": "realisasidankelsisa_tahun",
            "dana": "realisasidankelsisa_dana_id",
            "subopd": "realisasidankelsisa_subopd_id",
            "subkegiatan": "realisasidankelsisa_rencana_id",
            "nilai": "realisasidankelsisa_lpjnilai",
            "tahap": "realisasidankelsisa_tahap_id",
        },
    }

   
    @classmethod
    def filter_queryset(cls, qs, field, tahun=None, dana=None, tahap=None):

        if tahun:
            qs = qs.filter(**{field["tahun"]: tahun})

        if dana:
            qs = qs.filter(**{field["dana"]: dana})

        if tahap:
            qs = qs.filter(**{field["tahap"]: tahap})

        return qs


    # ==========================
    # TOTAL REALISASI
    # ==========================

    @classmethod
    def get_total_realisasi(cls, tahun=None, dana=None, tahap=None):

        total = Decimal(0)

        for model, field in cls.REALISASI_MODELS.items():

            qs = model.objects.all()

            qs = cls.filter_queryset(
                qs,
                field,
                tahun,
                dana,
                tahap
            )

            result = qs.aggregate(
                total=Sum(field["nilai"])
            )["total"] or Decimal(0)

            total += result

        return total
    
    @classmethod
    def get_rekap_per_tahap(cls, tahun=None, dana=None):

        hasil = {}

        for model, field in cls.REALISASI_MODELS.items():

            qs = model.objects.select_related(
                field["tahap"].replace("_id", "")
            )

            qs = cls.filter_queryset(
                qs,
                field,
                tahun,
                dana,
                None
            )

            data = (
                qs.values(
                    field["tahap"],
                    f'{field["tahap"].replace("_id","")}__tahap_dana'
                )
                .annotate(
                    realisasi=Sum(field["nilai"])
                )
            )

            for row in data:

                tahap_id = row[field["tahap"]]
                tahap_nama = row[f'{field["tahap"].replace("_id","")}__tahap_dana']

                key = (tahap_id, tahap_nama)

                if key not in hasil:
                    hasil[key] = Decimal(0)

                hasil[key] += row["realisasi"] or Decimal(0)

        data = []

        for (tahap_id, tahap_nama), total in sorted(hasil.items(), key=lambda x: x[0][0]):

            data.append({
                "realisasi_tahap_id": tahap_id,
                "realisasi_tahap__tahap_dana": tahap_nama,
                "realisasi": total
            })

        return data
    
    
    @classmethod
    def get_rekap_per_opd(cls, tahun=None, dana=None, tahap=None):

        result_map = defaultdict(lambda: {"nama": "", "total": Decimal(0)})

        for model, field in cls.REALISASI_MODELS.items():

            qs = model.objects.all()

            qs = cls.filter_queryset(
                qs,
                field,
                tahun,
                dana,
                tahap
            )

            data = (
                qs.values(
                    field["subopd"],
                    f'{field["subopd"].replace("_id","")}__sub_nama'
                )
                .annotate(total=Sum(field["nilai"]))
            )

            for row in data:

                opd_id = row[field["subopd"]]
                opd_nama = row[f'{field["subopd"].replace("_id","")}__sub_nama']

                result_map[opd_id]["nama"] = opd_nama
                result_map[opd_id]["total"] += row["total"] or Decimal(0)

        results = []

        for opd_id, val in result_map.items():

            results.append({
                "subopd_id": opd_id,
                "subopd_nama": val["nama"],
                "total": val["total"]
            })

        return sorted(results, key=lambda x: x["total"], reverse=True)
    
    
    @classmethod
    def get_available_dana(cls):
        hasil = {}

        for model, field in cls.REALISASI_MODELS.items():

            relasi = field["dana"].replace("_id", "")

            data = model.objects.values(
                field["dana"],
                f"{relasi}__sub_nama"
            ).distinct()

            for r in data:
                hasil[r[field["dana"]]] = r[f"{relasi}__sub_nama"]

        return sorted(hasil.items(), key=lambda x: x[1])


    @classmethod
    def get_available_tahap(cls):
        hasil = {}

        for model, field in cls.REALISASI_MODELS.items():

            relasi = field["tahap"].replace("_id", "")

            data = model.objects.values(
                field["tahap"],
                f"{relasi}__tahap_dana"
            ).distinct()

            for r in data:
                hasil[r[field["tahap"]]] = r[f"{relasi}__tahap_dana"]

        return sorted(hasil.items(), key=lambda x: x[1])
    