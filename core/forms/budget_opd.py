from django.db.models import Q

from opd.models import Subopd
from pagu.models import Pagudausg


SPECIAL_OPD_IDS = {124, 70, 67}
ALL_BUDGETED_OPD_LABEL = 'Semua OPD yang memiliki pagu'
EMPTY_OPD_VALUES = {None, '', 'None', 'none', 'NULL', 'null'}


def normalize_opd_id(opd_id):
    if hasattr(opd_id, 'pk'):
        opd_id = opd_id.pk
    if isinstance(opd_id, str):
        opd_id = opd_id.strip()
    if opd_id in EMPTY_OPD_VALUES:
        return None
    return opd_id


def is_special_opd(opd_id):
    opd_id = normalize_opd_id(opd_id)
    try:
        return int(opd_id) in SPECIAL_OPD_IDS
    except (TypeError, ValueError):
        return False


def scoped_opd_id(opd_id):
    opd_id = normalize_opd_id(opd_id)
    if opd_id is None or is_special_opd(opd_id):
        return None
    return opd_id


def budgeted_subopd_queryset(tahun=None, dana_slug=None, opd_id=None):
    opd_id = normalize_opd_id(opd_id)
    pagu_filters = Q()

    if tahun:
        pagu_filters &= Q(pagudausg_tahun=tahun)
    if dana_slug:
        pagu_filters &= Q(pagudausg_dana__sub_slug=dana_slug)

    if dana_slug and 'sisa' in dana_slug:
        pagu_filters &= Q(pagudausg_nilai__gt=0) | Q(pagudausg_sisa__gt=0)
    else:
        pagu_filters &= Q(pagudausg_nilai__gt=0)

    opd_ids = Pagudausg.objects.filter(pagu_filters).values('pagudausg_opd_id')
    queryset = Subopd.objects.filter(id__in=opd_ids).distinct().order_by('sub_nama')

    if opd_id is not None and not is_special_opd(opd_id):
        queryset = queryset.filter(id=opd_id)

    return queryset


def allow_all_budgeted_subopd(field, label=ALL_BUDGETED_OPD_LABEL):
    field.required = False
    field.empty_label = label
    field.initial = None
    field.widget.attrs['data-placeholder'] = label
    field.widget.attrs['data-allow-clear'] = 'true'
