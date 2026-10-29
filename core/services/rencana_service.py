from decimal import Decimal
from jadwal.models import Jadwal


def enrich_rencana_with_perubahan(
    data,
    tahun,
    posting_model,
    fk_rencana_field,
    pagu_field,
    output_field,
    jadwal_field='posting_jadwal',
    rencana_pagu_field=None,
    rencana_output_field=None,
):
    """
    Memeriksa apakah terdapat lebih dari 1 jadwal posting pada tahun yang bersangkutan.
    Jika ada lebih dari 1 jadwal (misalnya Induk dan Perubahan):
      - Mengambil jadwal Induk (ID terkecil) dan jadwal Perubahan (ID terbesar).
      - Menghubungkan setiap rencana ke data posting Induk dan Perubahan.
      - Menambahkan atribut ke setiap objek rencana:
          item.induk_pagu
          item.induk_output
          item.perubahan_pagu
          item.perubahan_output
          item.selisih_pagu
          item.selisih_output
      - Mengembalikan: is_perubahan, context_extra, data (list rencana yang telah diperkaya)
    Jika hanya ada 1 jadwal atau tidak ada jadwal:
      - Mengembalikan: is_perubahan=False, context_extra={}, data
    """
    if not tahun:
        return False, {}, data

    tbljadwal = Jadwal.objects.filter(jadwal_tahun=tahun).order_by('id')
    if tbljadwal.count() <= 1:
        return False, {}, data

    j_induk = tbljadwal.first()
    j_perubahan = tbljadwal.last()

    rencana_list = list(data)
    if not rencana_list:
        return True, {
            'is_perubahan': True,
            'jadwal_induk': j_induk,
            'jadwal_perubahan': j_perubahan,
            'total_induk_pagu': Decimal(0),
            'total_induk_output': Decimal(0),
            'total_perubahan_pagu': Decimal(0),
            'total_perubahan_output': Decimal(0),
            'total_selisih_pagu': Decimal(0),
            'total_selisih_output': Decimal(0),
        }, []

    rencana_ids = [item.id for item in rencana_list]

    filter_induk = {
        jadwal_field: j_induk.id,
        f"{fk_rencana_field}__in": rencana_ids,
    }
    filter_perubahan = {
        jadwal_field: j_perubahan.id,
        f"{fk_rencana_field}__in": rencana_ids,
    }

    induk_qs = posting_model.objects.filter(**filter_induk)
    perubahan_qs = posting_model.objects.filter(**filter_perubahan)

    induk_map = {getattr(p, f"{fk_rencana_field}_id"): p for p in induk_qs}
    perubahan_map = {getattr(p, f"{fk_rencana_field}_id"): p for p in perubahan_qs}

    rec_pagu = rencana_pagu_field or pagu_field
    rec_out = rencana_output_field or output_field

    for item in rencana_list:
        p_induk = induk_map.get(item.id)
        p_perubahan = perubahan_map.get(item.id)

        if p_induk:
            induk_pagu = getattr(p_induk, pagu_field, Decimal(0)) or Decimal(0)
            induk_output = getattr(p_induk, output_field, Decimal(0)) or Decimal(0)
        else:
            induk_pagu = Decimal(0)
            induk_output = Decimal(0)

        if p_perubahan:
            perubahan_pagu = getattr(p_perubahan, pagu_field, Decimal(0)) or Decimal(0)
            perubahan_output = getattr(p_perubahan, output_field, Decimal(0)) or Decimal(0)
        else:
            perubahan_pagu = getattr(item, rec_pagu, Decimal(0)) or Decimal(0)
            perubahan_output = getattr(item, rec_out, Decimal(0)) or Decimal(0)

        selisih_pagu = Decimal(perubahan_pagu) - Decimal(induk_pagu)
        selisih_output = Decimal(perubahan_output) - Decimal(induk_output)

        item.induk_pagu = Decimal(induk_pagu)
        item.induk_output = Decimal(induk_output)
        item.perubahan_pagu = Decimal(perubahan_pagu)
        item.perubahan_output = Decimal(perubahan_output)
        item.selisih_pagu = selisih_pagu
        item.selisih_output = selisih_output

    total_induk_pagu = sum(item.induk_pagu for item in rencana_list)
    total_induk_output = sum(item.induk_output for item in rencana_list)
    total_perubahan_pagu = sum(item.perubahan_pagu for item in rencana_list)
    total_perubahan_output = sum(item.perubahan_output for item in rencana_list)
    total_selisih_pagu = sum(item.selisih_pagu for item in rencana_list)
    total_selisih_output = sum(item.selisih_output for item in rencana_list)

    context_extra = {
        'is_perubahan': True,
        'jadwal_induk': j_induk,
        'jadwal_perubahan': j_perubahan,
        'total_induk_pagu': total_induk_pagu,
        'total_induk_output': total_induk_output,
        'total_perubahan_pagu': total_perubahan_pagu,
        'total_perubahan_output': total_perubahan_output,
        'total_selisih_pagu': total_selisih_pagu,
        'total_selisih_output': total_selisih_output,
    }

    return True, context_extra, rencana_list

