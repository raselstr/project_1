from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum, Q

from jadwal.models import Jadwal

from pendidikan.models import (
    Rencanaposting,
    Rencanapostingsisa,
)

from kesehatan.models import (
    Rencanakesehatanposting,
    Rencanakesehatanpostingsisa,
)

from pu.models import (
    Rencanapuposting,
    Rencanapupostingsisa,
)

from dankel.models import (
    RencDankeljadwal,
    RencDankeljadwalsisa,
)


class PaguService:

    COMMON_PAGU_FIELDS = {
        "tahun": "posting_tahun",
        "dana": "posting_dana_id",
        "subopd": "posting_subopd_id",
        "subkegiatan": "posting_subkegiatan_id",
        "nilai": "posting_pagu",
        "jadwal": "posting_jadwal_id",
    }

    PAGU_MODELS = {
        Rencanaposting: COMMON_PAGU_FIELDS,
        Rencanapostingsisa: COMMON_PAGU_FIELDS,

        Rencanakesehatanposting: COMMON_PAGU_FIELDS,
        Rencanakesehatanpostingsisa: COMMON_PAGU_FIELDS,

        Rencanapuposting: COMMON_PAGU_FIELDS,
        Rencanapupostingsisa: COMMON_PAGU_FIELDS,

        RencDankeljadwal: {
            "tahun": "rencdankel_tahun",
            "dana": "rencdankel_dana_id",
            "subopd": "rencdankel_subopd_id",
            "subkegiatan": "rencdankel_sub_id",
            "nilai": "rencdankel_pagu",
            "jadwal": "rencdankel_jadwal_id",
        },

        RencDankeljadwalsisa: {
            "tahun": "rencdankelsisa_tahun",
            "dana": "rencdankelsisa_dana_id",
            "subopd": "rencdankelsisa_subopd_id",
            "subkegiatan": "rencdankelsisa_sub",
            "nilai": "rencdankelsisa_pagu",
            "jadwal": "rencdankelsisa_jadwal_id",
        },
    }

    # ==========================================
    # AMBIL JADWAL AKTIF
    # ==========================================

    @staticmethod
    def get_active_jadwal():

        qs = Jadwal.objects.filter(
            jadwal_aktif=True
        ).values_list("jadwal_tahun", "id")

        result = defaultdict(list)

        for tahun, jadwal_id in qs:
            result[tahun].append(jadwal_id)

        return dict(result)


    # ==========================================
    # FILTER QUERYSET BERDASARKAN
    # TAHUN + JADWAL
    # ==========================================

    @classmethod
    def filter_queryset(cls, qs, field, jadwal_map):

        tahun_field = field["tahun"]
        jadwal_field = field["jadwal"]

        q_filter = Q()

        for tahun, jadwal_ids in jadwal_map.items():

            q_filter |= Q(
                **{
                    tahun_field: tahun,
                    f"{jadwal_field}__in": jadwal_ids,
                }
            )

        return qs.filter(q_filter)



    @classmethod
    def aggregate_by_fields(cls, group_fields):

        jadwal_map = cls.get_active_jadwal()

        if not jadwal_map:
            return []

        result_map = defaultdict(Decimal)

        for model, field in cls.PAGU_MODELS.items():

            qs = model.objects.all()

            qs = cls.filter_queryset(
                qs,
                field,
                jadwal_map
            )

            # mapping nama field model
            model_group_fields = [
                field[g] for g in group_fields
            ]

            data = (
                qs.values(*model_group_fields)
                .annotate(total=Sum(field["nilai"]))
            )

            for row in data:

                key = tuple(row[f] for f in model_group_fields)

                result_map[key] += row["total"] or Decimal(0)

        results = []

        for key, total in result_map.items():

            item = {}

            for i, g in enumerate(group_fields):
                item[g] = key[i]

            item["total"] = total

            results.append(item)

        return results
    
    
   
    # ==========================================
    # TOTAL KESELURUHAN PAGU
    # ==========================================

    @classmethod
    def get_total_pagu(cls, tahun=None, dana=None):

        jadwal_map = cls.get_active_jadwal()

        if not jadwal_map:
            return Decimal(0)

        total = Decimal(0)

        for model, field in cls.PAGU_MODELS.items():

            qs = model.objects.all()

            qs = cls.filter_queryset(
                qs,
                field,
                jadwal_map
            )
            
            # filter tambahan
            if tahun is not None:
                qs = qs.filter(**{field["tahun"]: tahun})

            if dana is not None:
                qs = qs.filter(**{field["dana"]: dana})

            result = qs.aggregate(
                total=Sum(field["nilai"])
            )["total"] or Decimal(0)

            total += result

        return total
    
    @classmethod
    def get_available_tahun(cls):
        tahun_set = set()

        for model, field in cls.PAGU_MODELS.items():
            tahun_set.update(
                model.objects.values_list(field["tahun"], flat=True).distinct()
            )

        return sorted(tahun_set, reverse=True)