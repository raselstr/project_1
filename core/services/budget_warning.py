from decimal import Decimal

from django.db.models import Q, Sum


def cumulative_tahap_ids(tahap_id):
    if not tahap_id:
        return []
    try:
        tahap_id = int(tahap_id)
    except (TypeError, ValueError):
        return []
    if tahap_id < 1:
        return []
    return list(range(1, tahap_id + 1))


def build_realisasi_penerimaan_warning(
    *,
    penerimaan_model,
    realisasi_model,
    tahun,
    dana_id,
    tahap_id=None,
):
    if not tahun or not dana_id:
        return None

    penerimaan_filters = Q(penerimaan_tahun=tahun) & Q(penerimaan_dana_id=dana_id)
    realisasi_filters = Q(realisasi_tahun=tahun) & Q(realisasi_dana_id=dana_id)

    tahap_ids = cumulative_tahap_ids(tahap_id)
    if tahap_ids:
        penerimaan_filters &= Q(penerimaan_tahap_id__in=tahap_ids)
        realisasi_filters &= Q(realisasi_tahap_id__in=tahap_ids)

    total_penerimaan = penerimaan_model.objects.filter(penerimaan_filters).aggregate(
        total=Sum('penerimaan_nilai')
    )['total'] or Decimal(0)
    total_realisasi = realisasi_model.objects.filter(realisasi_filters).aggregate(
        total=Sum('realisasi_nilai')
    )['total'] or Decimal(0)

    if total_realisasi <= total_penerimaan:
        return None

    selisih = total_realisasi - total_penerimaan
    tahap_label = f' sampai tahap {tahap_id}' if tahap_ids else ''
    return {
        'message': (
            f'Total realisasi dana{tahap_label} sebesar Rp. {total_realisasi:,.2f} '
            f'melebihi total penerimaan dana sebesar Rp. {total_penerimaan:,.2f}. '
            f'Selisih sebesar Rp. {selisih:,.2f}.'
        ),
        'total_realisasi': total_realisasi,
        'total_penerimaan': total_penerimaan,
        'selisih': selisih,
    }
