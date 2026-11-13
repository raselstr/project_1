# ============================================================
# Importer Excel Register SP2D
# Format file: Laporan Register SP2D dari SIPD
# Baris 1-7  : header / judul (dilewati)
# Baris 8+   : data (kolom A..K)
# ============================================================
import csv
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import transaction

import openpyxl


READ_CHUNK = 500
DB_CHUNK   = 300

# kolom index (0-based) → field model
#   A=0  No.
#   B=1  Tgl Pembuatan
#   C=2  Tgl Pencairan
#   D=3  Nomor SP2D
#   E=4  Unit SKPD
#   F=5  Nama Penerima
#   G=6  Keterangan
#   H=7  Jenis SP2D
#   I=8  Nilai Bruto
#   J=9  Nilai Potongan
#   K=10 Nilai Neto

COL_TGL_PEMBUATAN   = 1
COL_TGL_PENCAIRAN   = 2
COL_NOMOR_SP2D      = 3
COL_UNIT_SKPD       = 4
COL_NAMA_PENERIMA   = 5
COL_KETERANGAN      = 6
COL_JENIS_SP2D      = 7
COL_NILAI_BRUTO     = 8
COL_NILAI_POTONGAN  = 9
COL_NILAI_NETO      = 10

HEADER_ROWS = 7   # baris 1-7 adalah judul/header, skip


MONTH_MAP_ID = {
    'januari': 1, 'februari': 2, 'maret': 3, 'april': 4,
    'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
    'september': 9, 'oktober': 10, 'november': 11, 'desember': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
    'jul': 7, 'agu': 8, 'agt': 8, 'sep': 9, 'okt': 10, 'nov': 11, 'des': 12,
}


def _clean_str(val):
    if val is None:
        return ""
    s = str(val).strip()
    if s.lower() in ("none", "nan", "-", ""):
        return ""
    return s


def _to_decimal(val):
    if val is None:
        return Decimal("0")
    if isinstance(val, (int, float, Decimal)):
        return Decimal(str(val))
    s = str(val).strip()
    if not s or s.lower() in ("none", "nan", "-", "null"):
        return Decimal("0")

    # Hapus prefix Rp jika ada
    s = re.sub(r"^[Rr][Pp]\.?\s*", "", s).strip()

    # Deteksi format ribuan / desimal
    if "." in s and "," in s:
        # Contoh: 1.234.567,89 (Format Indo)
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:  # 1,234,567.89 (Format US)
            s = s.replace(",", "")
    elif "." in s:
        # Contoh: 50.000.000 atau 126.180 (Format ribuan Indo dengan titik)
        parts = s.split(".")
        if len(parts) > 2 or all(len(p) == 3 for p in parts[1:]):
            s = s.replace(".", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts) > 2 or all(len(p) == 3 for p in parts[1:]):
            s = s.replace(",", "")
        else:
            s = s.replace(",", ".")

    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _to_date(val):
    from datetime import date as d_date
    if val is None:
        return None
    if isinstance(val, d_date):
        return val
    if hasattr(val, "date"):      # datetime object dari openpyxl
        return val.date()
    s = str(val).strip()
    if not s or s.lower() in ("none", "nan", "-"):
        return None

    # Coba parsing format Indonesia seperti "3 Agustus 2026"
    parts = s.split()
    if len(parts) == 3:
        try:
            day = int(parts[0])
            m_str = parts[1].lower()
            year = int(parts[2])
            if m_str in MONTH_MAP_ID:
                return d_date(year, MONTH_MAP_ID[m_str], day)
        except (ValueError, TypeError):
            pass

    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def import_register_sp2d_excel(file_path: str, tahun: int, cache_key: str):
    from collections import defaultdict
    from register_sp2d.models import RegisterSP2D

    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    ws = wb.active

    # Ambil semua baris setelah header
    all_rows = list(ws.iter_rows(min_row=HEADER_ROWS + 1, values_only=True))
    wb.close()

    total_rows = len(all_rows)

    # Pra-load data existing untuk upsert
    existing_map = {
        obj.nomor_sp2d: obj
        for obj in RegisterSP2D.objects.filter(tahun=tahun)
    }

    log_path = Path(settings.MEDIA_ROOT) / "import" / f"register_sp2d_log_{tahun}.csv"
    skipped_path = Path(settings.MEDIA_ROOT) / "import" / f"register_sp2d_skipped_{tahun}.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    saved = updated = skipped = processed = 0
    seen_in_file = set()

    insert_batch = []
    update_batch = []

    updated_items = []
    skipped_items = []
    skipped_reason_counts = defaultdict(int)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, "w", newline="", encoding="utf-8") as f_log, \
         open(skipped_path, "w", newline="", encoding="utf-8") as f_skip:

        writer_log = csv.writer(f_log)
        writer_log.writerow(["row_excel", "nomor_sp2d", "unit_skpd", "status", "alasan", "tanggal_import"])

        writer_skip = csv.writer(f_skip)
        writer_skip.writerow(["row", "reason", "tanggal_import"])

        for idx, row in enumerate(all_rows, start=1):
            processed += 1
            excel_row_num = idx + HEADER_ROWS

            # progress setiap 50 baris
            if processed % 50 == 0:
                cache.set(cache_key, {"current": processed, "total": total_rows}, 3600)

            try:
                # Ambil nilai kolom
                nomor_sp2d = _clean_str(row[COL_NOMOR_SP2D] if len(row) > COL_NOMOR_SP2D else None)
                unit_skpd  = _clean_str(row[COL_UNIT_SKPD]  if len(row) > COL_UNIT_SKPD  else None)

                # Skip baris kosong / baris total / formula
                if not nomor_sp2d:
                    has_formula = any(str(c).strip().startswith("=") for c in row if c is not None)
                    is_all_empty = all(c is None or str(c).strip() == "" for c in row)

                    if has_formula:
                        reason = "Baris Rumus / Formula Total Excel (tidak memiliki nomor SP2D valid)"
                    elif is_all_empty:
                        reason = "Baris kosong dalam file Excel"
                    else:
                        reason = "Nomor SP2D kosong / bukan format SP2D yang valid"

                    skipped += 1
                    skipped_reason_counts[reason] += 1
                    skipped_items.append({
                        "excel_row": excel_row_num,
                        "nomor_sp2d": "-",
                        "unit_skpd": unit_skpd or "-",
                        "status": "DILEWATI",
                        "reason": reason,
                    })
                    writer_log.writerow([excel_row_num, "-", unit_skpd or "-", "DILEWATI", reason, now_str])
                    writer_skip.writerow([excel_row_num, reason, now_str])
                    continue

                # Skip baris duplikat dalam file
                if nomor_sp2d in seen_in_file:
                    reason = f"Nomor SP2D '{nomor_sp2d}' duplikat dalam file Excel (sudah diproses pada baris sebelumnya)"
                    skipped += 1
                    skipped_reason_counts["Duplikat Nomor SP2D dalam file Excel"] += 1
                    skipped_items.append({
                        "excel_row": excel_row_num,
                        "nomor_sp2d": nomor_sp2d,
                        "unit_skpd": unit_skpd or "-",
                        "status": "DILEWATI",
                        "reason": reason,
                    })
                    writer_log.writerow([excel_row_num, nomor_sp2d, unit_skpd or "-", "DILEWATI", reason, now_str])
                    writer_skip.writerow([excel_row_num, reason, now_str])
                    continue
                seen_in_file.add(nomor_sp2d)

                # Parsing seluruh kolom
                tgl_pembuatan = _to_date(row[COL_TGL_PEMBUATAN]  if len(row) > COL_TGL_PEMBUATAN  else None)
                tgl_pencairan = _to_date(row[COL_TGL_PENCAIRAN]  if len(row) > COL_TGL_PENCAIRAN  else None)
                nama_penerima = _clean_str(row[COL_NAMA_PENERIMA] if len(row) > COL_NAMA_PENERIMA  else None)
                keterangan    = _clean_str(row[COL_KETERANGAN]    if len(row) > COL_KETERANGAN     else None)
                jenis_sp2d    = _clean_str(row[COL_JENIS_SP2D]    if len(row) > COL_JENIS_SP2D     else None)
                nilai_bruto   = _to_decimal(row[COL_NILAI_BRUTO]    if len(row) > COL_NILAI_BRUTO    else 0)
                nilai_potongan= _to_decimal(row[COL_NILAI_POTONGAN] if len(row) > COL_NILAI_POTONGAN else 0)
                nilai_neto    = _to_decimal(row[COL_NILAI_NETO]     if len(row) > COL_NILAI_NETO     else 0)

                bulan = tgl_pembuatan.month if tgl_pembuatan else None

                data = dict(
                    tahun             = tahun,
                    bulan             = bulan,
                    tanggal_pembuatan = tgl_pembuatan,
                    tanggal_pencairan = tgl_pencairan,
                    nomor_sp2d        = nomor_sp2d,
                    unit_skpd         = unit_skpd,
                    nama_penerima     = nama_penerima,
                    keterangan        = keterangan,
                    jenis_sp2d        = jenis_sp2d,
                    nilai_bruto       = nilai_bruto,
                    nilai_potongan    = nilai_potongan,
                    nilai_neto        = nilai_neto,
                )

                if nomor_sp2d in existing_map:
                    obj = existing_map[nomor_sp2d]
                    for k, v in data.items():
                        setattr(obj, k, v)
                    update_batch.append(obj)
                    updated += 1
                    reason = f"Nomor SP2D sudah ada di database Tahun {tahun}. Data diperbarui (Bruto: Rp {nilai_bruto:,.0f})."
                    updated_items.append({
                        "excel_row": excel_row_num,
                        "nomor_sp2d": nomor_sp2d,
                        "unit_skpd": unit_skpd or "-",
                        "status": "DIPERBARUI",
                        "reason": reason,
                    })
                    writer_log.writerow([excel_row_num, nomor_sp2d, unit_skpd or "-", "DIPERBARUI", reason, now_str])
                else:
                    obj = RegisterSP2D(**data)
                    insert_batch.append(obj)
                    existing_map[nomor_sp2d] = obj
                    saved += 1
                    writer_log.writerow([excel_row_num, nomor_sp2d, unit_skpd or "-", "BARU", "Data baru berhasil disimpan", now_str])

            except Exception as e:
                reason = f"Format data error: {str(e)}"
                skipped += 1
                skipped_reason_counts["Format data error"] += 1
                skipped_items.append({
                    "excel_row": excel_row_num,
                    "nomor_sp2d": nomor_sp2d or "-",
                    "unit_skpd": unit_skpd or "-",
                    "status": "DILEWATI",
                    "reason": reason,
                })
                writer_log.writerow([excel_row_num, nomor_sp2d or "-", unit_skpd or "-", "DILEWATI", reason, now_str])
                writer_skip.writerow([excel_row_num, reason, now_str])
                continue

            # Flush batch
            if len(insert_batch) >= DB_CHUNK:
                with transaction.atomic():
                    RegisterSP2D.objects.bulk_create(insert_batch, batch_size=DB_CHUNK)
                insert_batch.clear()

            if len(update_batch) >= DB_CHUNK:
                UPDATE_FIELDS = [
                    "bulan", "tanggal_pembuatan", "tanggal_pencairan",
                    "unit_skpd", "nama_penerima", "keterangan", "jenis_sp2d",
                    "nilai_bruto", "nilai_potongan", "nilai_neto", "updated_at",
                ]
                with transaction.atomic():
                    RegisterSP2D.objects.bulk_update(update_batch, UPDATE_FIELDS, batch_size=DB_CHUNK)
                update_batch.clear()

    # Sisa data
    if insert_batch:
        with transaction.atomic():
            RegisterSP2D.objects.bulk_create(insert_batch, batch_size=DB_CHUNK)

    if update_batch:
        UPDATE_FIELDS = [
            "bulan", "tanggal_pembuatan", "tanggal_pencairan",
            "unit_skpd", "nama_penerima", "keterangan", "jenis_sp2d",
            "nilai_bruto", "nilai_potongan", "nilai_neto", "updated_at",
        ]
        with transaction.atomic():
            RegisterSP2D.objects.bulk_update(update_batch, UPDATE_FIELDS, batch_size=DB_CHUNK)

    skipped_summary = [
        {"reason": r, "count": c}
        for r, c in skipped_reason_counts.items()
    ]

    cache.set(cache_key, {
        "done": True,
        "saved": saved,
        "updated": updated,
        "skipped": skipped,
        "total": total_rows,
        "updated_reason": f"Nomor SP2D sudah terdaftar di database untuk Tahun {tahun}. Sistem memperbarui nilai bruto, potongan, neto, dan informasi penerima dengan data terbaru dari file Excel.",
        "skipped_summary": skipped_summary,
        "updated_items": updated_items[:100],
        "skipped_items": skipped_items[:100],
    }, 3600)

    return {
        "saved": saved,
        "updated": updated,
        "skipped": skipped,
        "total": total_rows,
        "updated_reason": f"Nomor SP2D sudah terdaftar di database untuk Tahun {tahun}. Sistem memperbarui nilai bruto, potongan, neto, dan informasi penerima dengan data terbaru dari file Excel.",
        "skipped_summary": skipped_summary,
        "updated_items": updated_items[:100],
        "skipped_items": skipped_items[:100],
    }
