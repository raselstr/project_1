from decimal import Decimal

from django.db.models import Q

from jadwal.models import Jadwal
from core.forms.budget_opd import is_special_opd


SPECIAL_OPD_IDS = {124, 70, 67}


def get_session_scope(request):
    return {
        'opd_id': request.session.get('idsubopd'),
        'tahun': request.session.get('tahun'),
        'jadwal_id': request.session.get('jadwal'),
    }


def get_active_jadwal_ids(tahun):
    jadwal = Jadwal.objects.filter(jadwal_tahun=tahun).order_by('id')
    if not jadwal.exists():
        return None, None

    induk_id = jadwal.first().id
    perubahan_id = jadwal.last().id if jadwal.count() > 1 else None
    return induk_id, perubahan_id


def build_posting_filters(prefix, opd_id=None, tahun=None):
    filters = Q()
    if opd_id and not is_special_opd(opd_id):
        filters &= Q(**{f'{prefix}_subopd_id': opd_id})
    if tahun:
        filters &= Q(**{f'{prefix}_tahun': tahun})
    return filters


def build_combined_posting_data(model, prefix, jadwal_ids, filters):
    jadwal_field = f'{prefix}_jadwal'
    subopd_field = f'{prefix}_subopd_id'
    tahun_field = f'{prefix}_tahun'
    dana_field = f'{prefix}_dana_id'
    sub_field = f'{prefix}_sub_id'
    pagu_field = f'{prefix}_pagu'

    induk_id, perubahan_id = jadwal_ids
    induk = model.objects.filter(**{jadwal_field: induk_id}).filter(filters).order_by(subopd_field)
    perubahan = model.objects.filter(**{jadwal_field: perubahan_id}).filter(filters).order_by(subopd_field)

    def item_key(item):
        return (
            getattr(item, subopd_field),
            getattr(item, tahun_field),
            getattr(item, dana_field),
            getattr(item, sub_field),
        )

    induk_dict = {item_key(item): item for item in induk}
    perubahan_dict = {item_key(item): item for item in perubahan}

    combined_data = []
    for key in set(induk_dict).union(perubahan_dict):
        item_induk = induk_dict.get(key)
        item_perubahan = perubahan_dict.get(key)

        if item_induk and item_perubahan:
            selisih_pagu = getattr(item_perubahan, pagu_field) - getattr(item_induk, pagu_field)
        elif item_perubahan:
            selisih_pagu = getattr(item_perubahan, pagu_field)
        elif item_induk:
            selisih_pagu = getattr(item_induk, pagu_field)
        else:
            selisih_pagu = Decimal(0)

        combined_data.append({
            'item_induk': item_induk,
            'item_perubahan': item_perubahan,
            'selisih_pagu': selisih_pagu,
        })

    return combined_data


def post_rencana_to_jadwal(source_model, target_model, prefix, jadwal, opd, tahun, opd_ids=None, dana_slug=None):
    rencana = source_model.objects.filter(**{
        f'{prefix}_tahun': tahun,
    })
    if dana_slug:
        rencana = rencana.filter(**{f'{prefix}_dana__sub_slug': dana_slug})
    if opd is not None:
        rencana = rencana.filter(**{f'{prefix}_subopd': opd})
    elif opd_ids is not None:
        rencana = rencana.filter(**{f'{prefix}_subopd_id__in': opd_ids})

    posted_count = 0
    for item in rencana:
        target_model.objects.update_or_create(
            **{
                f'{prefix}_id': item,
                f'{prefix}_jadwal': jadwal,
            },
            defaults={
                f'{prefix}_tahun': getattr(item, f'{prefix}_tahun'),
                f'{prefix}_dana': getattr(item, f'{prefix}_dana'),
                f'{prefix}_subopd': getattr(item, f'{prefix}_subopd'),
                f'{prefix}_sub': getattr(item, f'{prefix}_sub'),
                f'{prefix}_pagu': getattr(item, f'{prefix}_pagu'),
                f'{prefix}_output': getattr(item, f'{prefix}_output'),
                f'{prefix}_ket': getattr(item, f'{prefix}_ket'),
            },
        )
        posted_count += 1
    return posted_count
