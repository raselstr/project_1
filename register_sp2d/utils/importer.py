# ============================================================
# Importer Excel Register SP2D
# Format file: Laporan Register SP2D dari SIPD
# Baris 1-7  : header / judul (dilewati)
# Baris 8+   : data (kolom A..K)
# ============================================================
import csv
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
    try:
        if val is None:
            return Decimal("0")
        s = str(val).replace(",", "").strip()
        if not s or s.lower() in ("none", "nan"):
            return Decimal("0")
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

    skipped_path = Path(settings.MEDIA_ROOT) / "import" / f"register_sp2d_skipped_{tahun}.csv"
    skipped_path.parent.mkdir(parents=True, exist_ok=True)

    saved = updated = skipped = processed = 0
    seen_in_file = set()

    insert_batch = []
    update_batch = []

    with open(skipped_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["row", "reason", "tanggal_import"])

        for idx, row in enumerate(all_rows, start=1):
            processed += 1

            # progress setiap 100 baris
            if processed % 100 == 0:
                cache.set(cache_key, {"current": processed, "total": total_rows}, 3600)

            try:
                # Ambil nilai kolom
                nomor_sp2d = _clean_str(row[COL_NOMOR_SP2D] if len(row) > COL_NOMOR_SP2D else None)

                # Skip baris kosong / baris total (tidak ada nomor SP2D)
                if not nomor_sp2d:
                    skipped += 1
                    writer.writerow([idx, "nomor_sp2d kosong", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                    continue

                # Skip baris duplikat dalam file
                if nomor_sp2d in seen_in_file:
                    skipped += 1
                    writer.writerow([idx, "duplikat dalam file", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                    continue
                seen_in_file.add(nomor_sp2d)

                # Parsing seluruh kolom
                tgl_pembuatan = _to_date(row[COL_TGL_PEMBUATAN]  if len(row) > COL_TGL_PEMBUATAN  else None)
                tgl_pencairan = _to_date(row[COL_TGL_PENCAIRAN]  if len(row) > COL_TGL_PENCAIRAN  else None)
                unit_skpd     = _clean_str(row[COL_UNIT_SKPD]    if len(row) > COL_UNIT_SKPD      else None)
                nama_penerima = _clean_str(row[COL_NAMA_PENERIMA] if len(row) > COL_NAMA_PENERIMA  else None)
                keterangan    = _clean_str(row[COL_KETERANGAN]    if len(row) > COL_KETERANGAN     else None)
                jenis_sp2d    = _clean_str(row[COL_JENIS_SP2D]    if len(row) > COL_JENIS_SP2D     else None)
                nilai_bruto   = _to_decimal(row[COL_NILAI_BRUTO]    if len(row) > COL_NILAI_BRUTO    else 0)
                nilai_potongan= _to_decimal(row[COL_NILAI_POTONGAN] if len(row) > COL_NILAI_POTONGAN else 0)
                nilai_neto    = _to_decimal(row[COL_NILAI_NETO]     if len(row) > COL_NILAI_NETO     else 0)

                # Ambil bulan dari tanggal pembuatan
                bulan = tgl_pembuatan.month if tgl_pembuatan else None

                data = dict(
                    tahun          = tahun,
                    bulan          = bulan,
                    tanggal_pembuatan = tgl_pembuatan,
                    tanggal_pencairan = tgl_pencairan,
                    nomor_sp2d     = nomor_sp2d,
                    unit_skpd      = unit_skpd,
                    nama_penerima  = nama_penerima,
                    keterangan     = keterangan,
                    jenis_sp2d     = jenis_sp2d,
                    nilai_bruto    = nilai_bruto,
                    nilai_potongan = nilai_potongan,
                    nilai_neto     = nilai_neto,
                )

                if nomor_sp2d in existing_map:
                    obj = existing_map[nomor_sp2d]
                    for k, v in data.items():
                        setattr(obj, k, v)
                    update_batch.append(obj)
                else:
                    obj = RegisterSP2D(**data)
                    insert_batch.append(obj)
                    existing_map[nomor_sp2d] = obj

            except Exception as e:
                skipped += 1
                writer.writerow([idx, f"error: {str(e)}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                continue

            # Flush batch
            if len(insert_batch) >= DB_CHUNK:
                with transaction.atomic():
                    RegisterSP2D.objects.bulk_create(insert_batch, batch_size=DB_CHUNK)
                saved += len(insert_batch)
                insert_batch.clear()

            if len(update_batch) >= DB_CHUNK:
                UPDATE_FIELDS = [
                    "bulan", "tanggal_pembuatan", "tanggal_pencairan",
                    "unit_skpd", "nama_penerima", "keterangan", "jenis_sp2d",
                    "nilai_bruto", "nilai_potongan", "nilai_neto", "updated_at",
                ]
                with transaction.atomic():
                    RegisterSP2D.objects.bulk_update(update_batch, UPDATE_FIELDS, batch_size=DB_CHUNK)
                updated += len(update_batch)
                update_batch.clear()

    # Sisa data
    if insert_batch:
        with transaction.atomic():
            RegisterSP2D.objects.bulk_create(insert_batch, batch_size=DB_CHUNK)
        saved += len(insert_batch)

    if update_batch:
        UPDATE_FIELDS = [
            "bulan", "tanggal_pembuatan", "tanggal_pencairan",
            "unit_skpd", "nama_penerima", "keterangan", "jenis_sp2d",
            "nilai_bruto", "nilai_potongan", "nilai_neto", "updated_at",
        ]
        with transaction.atomic():
            RegisterSP2D.objects.bulk_update(update_batch, UPDATE_FIELDS, batch_size=DB_CHUNK)
        updated += len(update_batch)

    cache.set(cache_key, {
        "done": True,
        "saved": saved,
        "updated": updated,
        "skipped": skipped,
        "total": total_rows,
    }, 600)

    return {"saved": saved, "updated": updated, "skipped": skipped, "total": total_rows}
