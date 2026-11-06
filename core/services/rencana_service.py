from decimal import Decimal
from jadwal.models import Jadwal


def _detect_rencana_fields(rencana_list, rencana_pagu_field, rencana_output_field, pagu_field, output_field):
    """
    Mendeteksi nama field pagu dan output pada objek model Rencana secara otomatis.
    """
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

    return rec_pagu, rec_out


def _build_context_extra(j_semula, j_menjadi, rencana_list,
                         posting_model, fk_rencana_field,
                         pagu_field, output_field,
                         jadwal_field, rencana_pagu_field, rencana_output_field,
                         mode='perubahan'):
    """
    Helper bersama: memperkaya objek di rencana_list dengan atribut:
      - item.induk_pagu
      - item.induk_output
      - item.perubahan_pagu
      - item.perubahan_output
      - item.selisih_pagu
      - item.selisih_output
    
    mode='perubahan':
      Semula (Induk)  = posting j_semula
      Menjadi (Perubahan) = posting j_menjadi (atau draft rencana jika belum diposting pada j_menjadi)
    
    mode='draft':
      Semula (Induk)  = posting terakhir (j_semula)
      Menjadi (Perubahan) = draft rencana user saat ini
    """
    rencana_ids = [item.id for item in rencana_list]
    rec_pagu, rec_out = _detect_rencana_fields(
        rencana_list, rencana_pagu_field, rencana_output_field, pagu_field, output_field
    )

    # 1. Semula = data posting j_semula (rencana posting terakhir)
    if j_semula:
        filter_semula = {jadwal_field: j_semula.id, f"{fk_rencana_field}__in": rencana_ids}
        semula_qs = posting_model.objects.filter(**filter_semula)
        semula_map = {getattr(p, f"{fk_rencana_field}_id"): p for p in semula_qs}
    else:
        semula_map = {}

    # 2. Menjadi = posting j_menjadi (mode 'perubahan') ATAU draft rencana (mode 'draft')
    if mode == 'perubahan' and j_menjadi:
        filter_menjadi = {jadwal_field: j_menjadi.id, f"{fk_rencana_field}__in": rencana_ids}
        menjadi_qs = posting_model.objects.filter(**filter_menjadi)
        menjadi_map = {getattr(p, f"{fk_rencana_field}_id"): p for p in menjadi_qs}
        use_draft = False
    else:
        menjadi_map = {}
        use_draft = True  # gunakan nilai draft dari objek rencana itu sendiri

    any_diff = False

    for item in rencana_list:
        p_semula = semula_map.get(item.id)
        p_menjadi = menjadi_map.get(item.id) if not use_draft else None

        if p_semula:
            induk_pagu = getattr(p_semula, pagu_field, Decimal(0)) or Decimal(0)
            induk_output = getattr(p_semula, output_field, Decimal(0)) or Decimal(0)
        else:
            induk_pagu = Decimal(0)
            induk_output = Decimal(0)

        if use_draft:
            perubahan_pagu = getattr(item, rec_pagu, Decimal(0)) or Decimal(0)
            perubahan_output = getattr(item, rec_out, Decimal(0)) or Decimal(0)
        elif p_menjadi:
            perubahan_pagu = getattr(p_menjadi, pagu_field, Decimal(0)) or Decimal(0)
            perubahan_output = getattr(p_menjadi, output_field, Decimal(0)) or Decimal(0)
        else:
            # Fallback jika j_menjadi belum pernah diposting untuk item ini
            perubahan_pagu = getattr(item, rec_pagu, Decimal(0)) or Decimal(0)
            perubahan_output = getattr(item, rec_out, Decimal(0)) or Decimal(0)

        selisih_pagu = Decimal(perubahan_pagu) - Decimal(induk_pagu)
        selisih_output = Decimal(perubahan_output) - Decimal(induk_output)

        if use_draft and (p_semula is None or selisih_pagu != 0 or selisih_output != 0):
            any_diff = True

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

    return any_diff, {
        'jadwal_induk': j_semula,
        'jadwal_perubahan': j_menjadi,
        'total_induk_pagu': total_induk_pagu,
        'total_induk_output': total_induk_output,
        'total_perubahan_pagu': total_perubahan_pagu,
        'total_perubahan_output': total_perubahan_output,
        'total_selisih_pagu': total_selisih_pagu,
        'total_selisih_output': total_selisih_output,
        'rec_pagu': rec_pagu,
        'rec_out': rec_out,
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
    selected_jadwal=None,
):
    """
    Menyelaraskan data rencana dan membangun konteks perbandingan jadwal/draft:

    1. Tampilan List Rencana Default (selected_jadwal is None):
       - Jika jadwal > 1: data yang ditampilkan adalah data rencana terakhir yang diposting untuk jadwal yang aktif.
       - Jika jadwal aktif & rencana sudah diposting lalu user mengubah rencana:
           Induk = rencana yang diposting paling akhir
           Perubahan = data perubahan yang dilakukan user (draft) walaupun belum diposting.
       - Saat perubahan rencana sudah diposting: data induknya menjadi rencana kegiatan yang sudah diposting
         (dan data list selaras dengan postingan tersebut).

    2. Eksport PDF & Excel (selected_jadwal diberikan):
       - User memilih jadwal 1 (Induk):
           Tampilkan rencana kegiatan posting jadwal induk (format normal 8 kolom).
       - User memilih jadwal 2 (Perubahan 1):
           Tampilkan perbandingan Induk: Jadwal 1 dan Perubahan: Jadwal 2.
       - User memilih jadwal 3 (Perubahan 2):
           Tampilkan perbandingan Induk: Jadwal 2 dan Perubahan: Jadwal 3.
       - Begitu seterusnya (Induk: Jadwal N-1, Perubahan: Jadwal N).
       - User memilih 'draft':
           Tampilkan perbandingan Induk: Rencana posting terakhir dan Perubahan: Draft belum posting.
    """
    if not tahun:
        return False, {}, data

    tbljadwal = list(Jadwal.objects.filter(jadwal_tahun=tahun).order_by('id'))
    jumlah_jadwal = len(tbljadwal)

    if jumlah_jadwal == 0:
        return False, {'list_pilihan_jadwal': []}, data

    # 1. Tentukan jadwal yang aktif pada tahun berkenaan
    j_aktif = next((j for j in tbljadwal if j.jadwal_aktif), tbljadwal[-1])

    rencana_list = list(data)
    if not rencana_list:
        list_pilihan_jadwal = [
            {'id': str(j.id), 'nama': j.jadwal_keterangan, 'keterangan': f'Jadwal {j.jadwal_keterangan}'}
            for j in tbljadwal
        ]
        return False, {
            'is_perubahan': False,
            'is_draft_changed': False,
            'jadwal_induk': j_aktif,
            'jadwal_perubahan': None,
            'list_pilihan_jadwal': list_pilihan_jadwal,
        }, []

    rencana_ids = [item.id for item in rencana_list]
    rec_pagu, rec_out = _detect_rencana_fields(
        rencana_list, rencana_pagu_field, rencana_output_field, pagu_field, output_field
    )

    # 2. Cek jadwal mana saja yang sudah pernah diposting untuk rencana-rencana ini
    filter_check = {
        f"{jadwal_field}__in": [j.id for j in tbljadwal],
        f"{fk_rencana_field}__in": rencana_ids,
    }
    posted_raw = posting_model.objects.filter(**filter_check).values_list(jadwal_field, flat=True).distinct()
    posted_jadwal_ids = set(posted_raw)

    posted_jadwals = [j for j in tbljadwal if j.id in posted_jadwal_ids]
    latest_posted_jadwal = posted_jadwals[-1] if posted_jadwals else None

    # Baseline posting untuk membandingkan perubahan draft
    if j_aktif and j_aktif.id in posted_jadwal_ids:
        baseline_jadwal = j_aktif
    else:
        baseline_jadwal = latest_posted_jadwal

    # 3. Cek apakah ada perubahan draft vs baseline posting
    has_draft_diff = False
    draft_extra = {}
    if baseline_jadwal:
        has_draft_diff, draft_extra = _build_context_extra(
            baseline_jadwal, None, rencana_list,
            posting_model, fk_rencana_field,
            pagu_field, output_field,
            jadwal_field, rencana_pagu_field, rencana_output_field,
            mode='draft',
        )

    # 4. Susun daftar pilihan jadwal untuk modal Cetak PDF & Export Excel
    list_pilihan_jadwal = []
    for i, j in enumerate(tbljadwal):
        is_posted = (j.id in posted_jadwal_ids)
        if i == 0:
            label = f"{j.jadwal_keterangan} (Induk)"
            ket = f"Rencana kegiatan posting jadwal induk ({j.jadwal_keterangan})"
        else:
            j_prev = tbljadwal[i - 1]
            label = f"{j.jadwal_keterangan} (Perubahan vs {j_prev.jadwal_keterangan})"
            ket = f"Induk: {j_prev.jadwal_keterangan} | Perubahan: {j.jadwal_keterangan}"

        list_pilihan_jadwal.append({
            'id': str(j.id),
            'nama': label,
            'keterangan': ket,
            'index': i,
            'is_active': (j.id == j_aktif.id),
            'is_posted': is_posted,
            'is_draft': False,
        })

    if has_draft_diff:
        nama_induk_draft = baseline_jadwal.jadwal_keterangan if baseline_jadwal else 'Induk'
        list_pilihan_jadwal.append({
            'id': 'draft',
            'nama': 'Draft (Usulan Rencana Kegiatan Penganggaran - Belum Posting)',
            'keterangan': f'Induk: {nama_induk_draft} | Perubahan: Draft Rencana Saat Ini',
            'index': len(tbljadwal),
            'is_active': False,
            'is_posted': False,
            'is_draft': True,
        })

    # =========================================================================
    # KASUS A: User memilih opsi 'draft' secara spesifik
    # =========================================================================
    if str(selected_jadwal).lower() == 'draft':
        if baseline_jadwal:
            _, extra = _build_context_extra(
                baseline_jadwal, None, rencana_list,
                posting_model, fk_rencana_field,
                pagu_field, output_field,
                jadwal_field, rencana_pagu_field, rencana_output_field,
                mode='draft',
            )
        else:
            extra = {}
        extra['is_perubahan'] = False
        extra['is_draft_changed'] = True
        extra['jadwal_induk'] = baseline_jadwal
        extra['jadwal_perubahan'] = None
        extra['list_pilihan_jadwal'] = list_pilihan_jadwal
        extra['selected_jadwal'] = 'draft'
        return False, extra, rencana_list

    # =========================================================================
    # KASUS B: User memilih ID Jadwal tertentu (misal: '1', '2', '3')
    # =========================================================================
    if selected_jadwal is not None and str(selected_jadwal).strip() != '':
        target_idx = next((idx for idx, j in enumerate(tbljadwal) if str(j.id) == str(selected_jadwal)), None)
        if target_idx is not None:
            # Subkasus B.1: Jadwal 1 (Induk) -> format normal 8 kolom sesuai postingan jadwal induk
            if target_idx == 0:
                j_induk_target = tbljadwal[0]
                filter_target = {jadwal_field: j_induk_target.id, f"{fk_rencana_field}__in": rencana_ids}
                postings = {getattr(p, f"{fk_rencana_field}_id"): p for p in posting_model.objects.filter(**filter_target)}
                for item in rencana_list:
                    p_item = postings.get(item.id)
                    pagu_val = getattr(p_item, pagu_field, Decimal(0)) if p_item else Decimal(0)
                    out_val = getattr(p_item, output_field, Decimal(0)) if p_item else Decimal(0)
                    setattr(item, rec_pagu, pagu_val)
                    setattr(item, rec_out, out_val)
                    item.rencana_pagu = pagu_val
                    item.rencana_output = out_val
                    item.induk_pagu = pagu_val
                    item.induk_output = out_val

                total_pagu = sum(getattr(item, rec_pagu, Decimal(0)) or Decimal(0) for item in rencana_list)
                total_out = sum(getattr(item, rec_out, Decimal(0)) or Decimal(0) for item in rencana_list)

                extra = {
                    'is_perubahan': False,
                    'is_draft_changed': False,
                    'jadwal_terpilih': j_induk_target,
                    'jadwal_induk': j_induk_target,
                    'total_induk_pagu': total_pagu,
                    'total_induk_output': total_out,
                    'list_pilihan_jadwal': list_pilihan_jadwal,
                    'selected_jadwal': str(j_induk_target.id),
                }
                return False, extra, rencana_list

            # Subkasus B.2: Jadwal N (N > 0) -> format perbandingan: Induk = Jadwal N-1, Perubahan = Jadwal N
            else:
                j_induk_target = tbljadwal[target_idx - 1]
                j_perubahan_target = tbljadwal[target_idx]
                _, extra = _build_context_extra(
                    j_induk_target, j_perubahan_target, rencana_list,
                    posting_model, fk_rencana_field,
                    pagu_field, output_field,
                    jadwal_field, rencana_pagu_field, rencana_output_field,
                    mode='perubahan',
                )
                extra['is_perubahan'] = True
                extra['is_draft_changed'] = False
                extra['jadwal_induk'] = j_induk_target
                extra['jadwal_perubahan'] = j_perubahan_target
                extra['list_pilihan_jadwal'] = list_pilihan_jadwal
                extra['selected_jadwal'] = str(j_perubahan_target.id)
                return True, extra, rencana_list

    # =========================================================================
    # KASUS C: Tampilan List Rencana Default di Browser (selected_jadwal is None)
    # =========================================================================
    # Jika belum pernah posting sama sekali:
    if not posted_jadwal_ids:
        for item in rencana_list:
            pagu_val = getattr(item, rec_pagu, Decimal(0)) or Decimal(0)
            out_val = getattr(item, rec_out, Decimal(0)) or Decimal(0)
            item.rencana_pagu = pagu_val
            item.rencana_output = out_val
            item.induk_pagu = pagu_val
            item.induk_output = out_val
        total_pagu = sum(getattr(item, rec_pagu, Decimal(0)) or Decimal(0) for item in rencana_list)
        total_out = sum(getattr(item, rec_out, Decimal(0)) or Decimal(0) for item in rencana_list)
        extra = {
            'is_perubahan': False,
            'is_draft_changed': False,
            'jadwal_terpilih': j_aktif,
            'jadwal_induk': j_aktif,
            'total_induk_pagu': total_pagu,
            'total_induk_output': total_out,
            'list_pilihan_jadwal': list_pilihan_jadwal,
            'selected_jadwal': str(j_aktif.id) if j_aktif else None,
        }
        return False, extra, rencana_list

    # Jika sudah ada postingan dan ada perbedaan draft (user melakukan perubahan yang belum diposting):
    if has_draft_diff:
        draft_extra['is_perubahan'] = False
        draft_extra['is_draft_changed'] = True
        draft_extra['jadwal_induk'] = baseline_jadwal
        draft_extra['jadwal_perubahan'] = None
        draft_extra['list_pilihan_jadwal'] = list_pilihan_jadwal
        draft_extra['selected_jadwal'] = 'draft'
        return False, draft_extra, rencana_list

    # Jika tidak ada perbedaan draft (data rencana selaras dengan rencana posting terakhir):
    # Selaraskan nilai pagu & output objek dengan postingan baseline
    if baseline_jadwal:
        filter_base = {jadwal_field: baseline_jadwal.id, f"{fk_rencana_field}__in": rencana_ids}
        postings = {getattr(p, f"{fk_rencana_field}_id"): p for p in posting_model.objects.filter(**filter_base)}
        for item in rencana_list:
            p_item = postings.get(item.id)
            if p_item:
                pagu_val = getattr(p_item, pagu_field, Decimal(0)) or Decimal(0)
                out_val = getattr(p_item, output_field, Decimal(0)) or Decimal(0)
            else:
                pagu_val = getattr(item, rec_pagu, Decimal(0)) or Decimal(0)
                out_val = getattr(item, rec_out, Decimal(0)) or Decimal(0)
            setattr(item, rec_pagu, pagu_val)
            setattr(item, rec_out, out_val)
            item.rencana_pagu = pagu_val
            item.rencana_output = out_val
            item.induk_pagu = pagu_val
            item.induk_output = out_val

    total_pagu = sum(getattr(item, rec_pagu, Decimal(0)) or Decimal(0) for item in rencana_list)
    total_out = sum(getattr(item, rec_out, Decimal(0)) or Decimal(0) for item in rencana_list)

    draft_extra['is_perubahan'] = False
    draft_extra['is_draft_changed'] = False
    draft_extra['jadwal_terpilih'] = baseline_jadwal
    draft_extra['jadwal_induk'] = baseline_jadwal
    draft_extra['total_induk_pagu'] = total_pagu
    draft_extra['total_induk_output'] = total_out
    draft_extra['list_pilihan_jadwal'] = list_pilihan_jadwal
    draft_extra['selected_jadwal'] = str(baseline_jadwal.id) if baseline_jadwal else None
    return False, draft_extra, rencana_list
