from decimal import Decimal
from jadwal.models import Jadwal


def _build_context_extra(j_semula, j_menjadi, rencana_list,
                         posting_model, fk_rencana_field,
                         pagu_field, output_field,
                         jadwal_field, rencana_pagu_field, rencana_output_field,
                         mode='perubahan'):
    """
    Helper bersama: enriches rencana_list dengan atribut induk/perubahan/selisih.
    mode='perubahan'  → label Induk/Perubahan (jadwal > 1)
    mode='draft'      → label Semula/Menjadi  (jadwal = 1, ada posting, ada perubahan draft)
    """
    rencana_ids = [item.id for item in rencana_list]

    # Deteksi field pagu dan output pada model rencana secara dinamis
    first_item = rencana_list[0] if rencana_list else None
    if rencana_pagu_field and hasattr(first_item, rencana_pagu_field):
        rec_pagu = rencana_pagu_field
    elif first_item and hasattr(first_item, 'rencana_pagu'):
        rec_pagu = 'rencana_pagu'
    elif first_item and hasattr(first_item, 'rencdankel_pagu'):
        rec_pagu = 'rencdankel_pagu'
    elif first_item and hasattr(first_item, 'rencdankelsisa_pagu'):
        rec_pagu = 'rencdankelsisa_pagu'
    else:
        rec_pagu = pagu_field

    if rencana_output_field and hasattr(first_item, rencana_output_field):
        rec_out = rencana_output_field
    elif first_item and hasattr(first_item, 'rencana_output'):
        rec_out = 'rencana_output'
    elif first_item and hasattr(first_item, 'rencdankel_output'):
        rec_out = 'rencdankel_output'
    elif first_item and hasattr(first_item, 'rencdankelsisa_output'):
        rec_out = 'rencdankelsisa_output'
    else:
        rec_out = output_field

    # Semula = data posting terakhir (j_semula / jadwal aktif)
    filter_semula = {jadwal_field: j_semula.id, f"{fk_rencana_field}__in": rencana_ids}
    semula_qs  = posting_model.objects.filter(**filter_semula)
    semula_map = {getattr(p, f"{fk_rencana_field}_id"): p for p in semula_qs}

    # Menjadi = posting perubahan (mode 'perubahan') ATAU draft rencana (mode 'draft')
    if mode == 'perubahan' and j_menjadi:
        filter_menjadi = {jadwal_field: j_menjadi.id, f"{fk_rencana_field}__in": rencana_ids}
        menjadi_qs  = posting_model.objects.filter(**filter_menjadi)
        menjadi_map = {getattr(p, f"{fk_rencana_field}_id"): p for p in menjadi_qs}
        use_draft = False
    else:
        menjadi_map = {}
        use_draft = True  # gunakan nilai draft dari objek rencana itu sendiri

    any_diff = False  # apakah ada perbedaan antara semula vs menjadi (mode draft)

    for item in rencana_list:
        p_semula   = semula_map.get(item.id)
        p_menjadi  = menjadi_map.get(item.id) if not use_draft else None

        if p_semula:
            induk_pagu   = getattr(p_semula, pagu_field,   Decimal(0)) or Decimal(0)
            induk_output = getattr(p_semula, output_field, Decimal(0)) or Decimal(0)
        else:
            induk_pagu   = Decimal(0)
            induk_output = Decimal(0)

        if use_draft:
            perubahan_pagu   = getattr(item, rec_pagu, Decimal(0)) or Decimal(0)
            perubahan_output = getattr(item, rec_out,  Decimal(0)) or Decimal(0)
        elif p_menjadi:
            perubahan_pagu   = getattr(p_menjadi, pagu_field,   Decimal(0)) or Decimal(0)
            perubahan_output = getattr(p_menjadi, output_field, Decimal(0)) or Decimal(0)
        else:
            perubahan_pagu   = getattr(item, rec_pagu, Decimal(0)) or Decimal(0)
            perubahan_output = getattr(item, rec_out,  Decimal(0)) or Decimal(0)

        selisih_pagu   = Decimal(perubahan_pagu)   - Decimal(induk_pagu)
        selisih_output = Decimal(perubahan_output) - Decimal(induk_output)

        if use_draft and (p_semula is None or selisih_pagu != 0 or selisih_output != 0):
            any_diff = True

        item.induk_pagu       = Decimal(induk_pagu)
        item.induk_output     = Decimal(induk_output)
        item.perubahan_pagu   = Decimal(perubahan_pagu)
        item.perubahan_output = Decimal(perubahan_output)
        item.selisih_pagu     = selisih_pagu
        item.selisih_output   = selisih_output

    total_induk_pagu       = sum(item.induk_pagu       for item in rencana_list)
    total_induk_output     = sum(item.induk_output     for item in rencana_list)
    total_perubahan_pagu   = sum(item.perubahan_pagu   for item in rencana_list)
    total_perubahan_output = sum(item.perubahan_output for item in rencana_list)
    total_selisih_pagu     = sum(item.selisih_pagu     for item in rencana_list)
    total_selisih_output   = sum(item.selisih_output   for item in rencana_list)

    return any_diff, {
        'jadwal_induk'           : j_semula,
        'jadwal_perubahan'       : j_menjadi,
        'total_induk_pagu'       : total_induk_pagu,
        'total_induk_output'     : total_induk_output,
        'total_perubahan_pagu'   : total_perubahan_pagu,
        'total_perubahan_output' : total_perubahan_output,
        'total_selisih_pagu'     : total_selisih_pagu,
        'total_selisih_output'   : total_selisih_output,
        'rec_pagu'               : rec_pagu,
        'rec_out'                : rec_out,
    }


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
    Memeriksa kondisi jadwal dan posting untuk menentukan mode tampilan:

    1. Jadwal > 1  (Induk + Perubahan):
       → Mode 'perubahan': tampilkan Semula (Induk) vs Menjadi (Perubahan)
       → is_perubahan=True, is_draft_changed=False

    2. Jadwal = 1, sudah ada posting, dan data rencana draft ≠ posting:
       → Mode 'draft': tampilkan Semula (Posting terakhir) vs Menjadi (Draft rencana saat ini)
       → is_perubahan=False, is_draft_changed=True

    3. Jadwal = 1, sudah ada posting, data rencana draft = posting:
       → Tampilkan data sesuai posting (tidak ada perubahan draft)
       → is_perubahan=False, is_draft_changed=False, data = dari posting

    4. Jadwal = 1, belum ada posting SAMA SEKALI:
       → Tampilkan semua rencana biasa (apa adanya)
       → is_perubahan=False, is_draft_changed=False, data = dari Rencana

    5. Tidak ada jadwal:
       → Tampilkan semua rencana biasa
       → is_perubahan=False, is_draft_changed=False, data = dari Rencana
    """
    if not tahun:
        return False, {}, data

    tbljadwal = Jadwal.objects.filter(jadwal_tahun=tahun).order_by('id')
    jumlah_jadwal = tbljadwal.count()

    # ── CASE 5: tidak ada jadwal sama sekali ─────────────────────────────────
    if jumlah_jadwal == 0:
        return False, {}, data

    # ── CASE 1: lebih dari 1 jadwal → mode Induk vs Perubahan ────────────────
    if jumlah_jadwal > 1:
        j_induk     = tbljadwal.first()
        j_perubahan = tbljadwal.last()

        rencana_list = list(data)
        if not rencana_list:
            return True, {
                'is_perubahan': True,
                'is_draft_changed': False,
                'jadwal_induk': j_induk,
                'jadwal_perubahan': j_perubahan,
                'total_induk_pagu': Decimal(0),
                'total_induk_output': Decimal(0),
                'total_perubahan_pagu': Decimal(0),
                'total_perubahan_output': Decimal(0),
                'total_selisih_pagu': Decimal(0),
                'total_selisih_output': Decimal(0),
            }, []

        _, extra = _build_context_extra(
            j_induk, j_perubahan, rencana_list,
            posting_model, fk_rencana_field,
            pagu_field, output_field,
            jadwal_field, rencana_pagu_field, rencana_output_field,
            mode='perubahan',
        )
        extra['is_perubahan']    = True
        extra['is_draft_changed'] = False
        return True, extra, rencana_list

    # ── CASE 2–4: tepat 1 jadwal ─────────────────────────────────────────────
    j_satu = tbljadwal.first()

    rencana_list = list(data)
    if not rencana_list:
        return False, {}, []

    rencana_ids = [item.id for item in rencana_list]

    # Cek apakah sudah ada posting untuk jadwal ini
    filter_posting = {jadwal_field: j_satu.id, f"{fk_rencana_field}__in": rencana_ids}
    posting_count = posting_model.objects.filter(**filter_posting).count()

    # CASE 4: belum ada posting → tampilkan rencana biasa
    if posting_count == 0:
        return False, {}, rencana_list

    # Ada posting: cek apakah draft berbeda dari posting terakhir
    any_diff, extra = _build_context_extra(
        j_satu, None, rencana_list,
        posting_model, fk_rencana_field,
        pagu_field, output_field,
        jadwal_field, rencana_pagu_field, rencana_output_field,
        mode='draft',
    )
    extra['is_perubahan']    = False
    extra['jadwal_perubahan'] = None

    if any_diff:
        # CASE 2: ada perubahan draft vs posting → tampilkan Semula vs Menjadi
        extra['is_draft_changed'] = True
        return False, extra, rencana_list
    else:
        # CASE 3: tidak ada perubahan draft → tampilkan sesuai posting (ganti nilai draft dgn posting)
        extra['is_draft_changed'] = False
        rec_pagu = extra.get('rec_pagu', rencana_pagu_field or pagu_field)
        rec_out  = extra.get('rec_out',  rencana_output_field or output_field)
        for item in rencana_list:
            # Gunakan nilai posting (induk) sebagai nilai tampilan
            setattr(item, rec_pagu, item.induk_pagu)
            setattr(item, rec_out,  item.induk_output)
        return False, extra, rencana_list

