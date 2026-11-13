from pathlib import Path
import csv
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from collections import defaultdict
import pandas as pd

from django.conf import settings
from django.core.cache import cache
from django.db import transaction

from sipd.models import Sipd
from .mapping import EXCEL_FIELD_MAPPING


READ_CHUNK = 2000
DB_CHUNK = 500

DATE_FIELDS = {
    "tanggal_dokumen",
    "tanggal_spp",
    "tanggal_spm",
    "tanggal_sp2d",
    "tanggal_transfer",
}

UNIQUE_FIELDS = (
    "tahun",
    "kode_sub_skpd",
    "kode_sub_kegiatan",
    "kode_rekening",
    "nomor_dokumen",
    "nomor_spm",
    "nomor_sp2d",
)


# ================= HELPERS =================
def clean_str(val):
    if pd.isna(val) or val is None:
        return ""
    val = str(val).strip()
    if val.lower() in ("", "nan", "none", "null", "draft", "-"):
        return ""
    return val


def parse_indonesian_decimal(val):
    if val is None or pd.isna(val):
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
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "." in s:
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


def to_date(val):
    try:
        if pd.isna(val) or val is None:
            return None
        if hasattr(val, "date"):
            return val.date()
        parsed = pd.to_datetime(val, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date()
    except Exception:
        return None


# ================= IMPORT FUNCTION =================
def import_sipd_excel(file_path: str, tahun: int, cache_key: str):
    """
    Import Excel SIPD dengan tracking data baru, diperbaharui, dan dilewati.
    """
    df = pd.read_excel(file_path)
    total_rows = len(df)

    processed = 0
    saved = 0
    updated = 0
    skipped = 0

    seen_in_file = set()

    # Pre-load existing keys mapping: (sub_skpd, sub_keg, rek, dok, spm, sp2d) -> id
    existing_map = {
        (r[0], r[1], r[2], r[3], r[4], r[5]): r[6]
        for r in Sipd.objects.filter(tahun=tahun).values_list(
            "kode_sub_skpd",
            "kode_sub_kegiatan",
            "kode_rekening",
            "nomor_dokumen",
            "nomor_spm",
            "nomor_sp2d",
            "id",
        )
    }

    log_path = Path(settings.MEDIA_ROOT) / "import" / f"sipd_log_{tahun}.csv"
    skipped_path = Path(settings.MEDIA_ROOT) / "import" / f"sipd_skipped_{tahun}.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    updated_items = []
    skipped_items = []
    skipped_reason_counts = defaultdict(int)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, "w", newline="", encoding="utf-8") as f_log, \
         open(skipped_path, "w", newline="", encoding="utf-8") as f_skip:

        writer_log = csv.writer(f_log)
        writer_log.writerow(["row_excel", "nomor_sp2d", "nomor_dokumen", "kode_sub_kegiatan", "status", "alasan", "tanggal_import"])

        writer_skip = csv.writer(f_skip)
        writer_skip.writerow(["row", "reason", "tanggal_import"])

        insert_batch = []
        update_batch = []

        for start in range(0, total_rows, READ_CHUNK):
            df_chunk = df.iloc[start:start + READ_CHUNK]

            for idx, row in df_chunk.iterrows():
                processed += 1
                excel_row_num = processed + 1  # Baris 1 header excel

                if processed % 150 == 0:
                    cache.set(
                        cache_key,
                        {"current": processed, "total": total_rows, "done": False},
                        3600
                    )

                try:
                    data = {"tahun": tahun}

                    # mapping kolom
                    for excel_col, model_field in EXCEL_FIELD_MAPPING.items():
                        val = row.get(excel_col)

                        if "nilai" in model_field:
                            data[model_field] = parse_indonesian_decimal(val)
                        elif model_field in DATE_FIELDS:
                            data[model_field] = to_date(val)
                        else:
                            data[model_field] = clean_str(val)

                    # validasi unique kosong
                    if any(data.get(f, "") == "" for f in UNIQUE_FIELDS):
                        reason = "Kolom unik kosong / draft (dokumen/spm/sp2d tidak lengkap)"
                        skipped += 1
                        skipped_reason_counts[reason] += 1
                        if len(skipped_items) < 100:
                            skipped_items.append({
                                "excel_row": excel_row_num,
                                "nomor_sp2d": data.get("nomor_sp2d") or "-",
                                "unit_skpd": data.get("nama_sub_skpd") or data.get("kode_sub_skpd") or "-",
                                "status": "DILEWATI",
                                "reason": reason,
                            })
                        writer_skip.writerow([excel_row_num, reason, now_str])
                        writer_log.writerow([excel_row_num, data.get("nomor_sp2d") or "-", data.get("nomor_dokumen") or "-", data.get("kode_sub_kegiatan") or "-", "DILEWATI", reason, now_str])
                        continue

                    lookup_key = (
                        data["kode_sub_skpd"],
                        data["kode_sub_kegiatan"],
                        data["kode_rekening"],
                        data["nomor_dokumen"],
                        data["nomor_spm"],
                        data["nomor_sp2d"],
                    )

                    # duplikat dalam file itu sendiri
                    if lookup_key in seen_in_file:
                        reason = "Duplikat dalam file Excel yang sama"
                        skipped += 1
                        skipped_reason_counts[reason] += 1
                        if len(skipped_items) < 100:
                            skipped_items.append({
                                "excel_row": excel_row_num,
                                "nomor_sp2d": data.get("nomor_sp2d") or "-",
                                "unit_skpd": data.get("nama_sub_skpd") or "-",
                                "status": "DILEWATI",
                                "reason": reason,
                            })
                        writer_skip.writerow([excel_row_num, reason, now_str])
                        writer_log.writerow([excel_row_num, data.get("nomor_sp2d") or "-", data.get("nomor_dokumen") or "-", data.get("kode_sub_kegiatan") or "-", "DILEWATI", reason, now_str])
                        continue
                    seen_in_file.add(lookup_key)

                    if lookup_key in existing_map:
                        existing_id = existing_map[lookup_key]
                        obj = Sipd(id=existing_id, **data)
                        update_batch.append(obj)
                        updated += 1
                        reason = f"Data transaksi sudah terdaftar. Nilai realisasi diperbaharui (Rp {data.get('nilai_realisasi', 0):,.0f})."
                        if len(updated_items) < 100:
                            updated_items.append({
                                "excel_row": excel_row_num,
                                "nomor_sp2d": data.get("nomor_sp2d") or "-",
                                "unit_skpd": data.get("nama_sub_skpd") or "-",
                                "status": "DIPERBARUI",
                                "reason": reason,
                            })
                        writer_log.writerow([excel_row_num, data.get("nomor_sp2d") or "-", data.get("nomor_dokumen") or "-", data.get("kode_sub_kegiatan") or "-", "DIPERBARUI", reason, now_str])
                    else:
                        obj = Sipd(**data)
                        insert_batch.append(obj)
                        existing_map[lookup_key] = None
                        saved += 1
                        writer_log.writerow([excel_row_num, data.get("nomor_sp2d") or "-", data.get("nomor_dokumen") or "-", data.get("kode_sub_kegiatan") or "-", "BARU", "Data baru berhasil disimpan", now_str])

                except Exception as e:
                    reason = f"Error pemrosesan baris: {str(e)}"
                    skipped += 1
                    skipped_reason_counts["Error format data"] += 1
                    if len(skipped_items) < 100:
                        skipped_items.append({
                            "excel_row": excel_row_num,
                            "nomor_sp2d": data.get("nomor_sp2d", "-"),
                            "unit_skpd": data.get("nama_sub_skpd", "-"),
                            "status": "DILEWATI",
                            "reason": reason,
                        })
                    writer_skip.writerow([excel_row_num, reason, now_str])
                    writer_log.writerow([excel_row_num, data.get("nomor_sp2d", "-"), data.get("nomor_dokumen", "-"), data.get("kode_sub_kegiatan", "-"), "DILEWATI", reason, now_str])
                    continue

                # Batch insert
                if len(insert_batch) >= DB_CHUNK:
                    with transaction.atomic():
                        Sipd.objects.bulk_create(insert_batch, batch_size=DB_CHUNK, ignore_conflicts=True)
                    insert_batch.clear()

                # Batch update
                if len(update_batch) >= DB_CHUNK:
                    UPDATE_FIELDS = [
                        "nama_sub_skpd", "kode_program", "nama_program",
                        "kode_kegiatan", "nama_kegiatan", "nama_sub_kegiatan",
                        "nama_rekening", "jenis_dokumen", "jenis_transaksi",
                        "nomor_dpt", "tanggal_dokumen", "keterangan_dokumen",
                        "nilai_realisasi", "nilai_setoran", "nomor_spp",
                        "tanggal_spp", "tanggal_spm", "tanggal_sp2d",
                        "tanggal_transfer", "nilai_sp2d", "updated_at",
                    ]
                    with transaction.atomic():
                        Sipd.objects.bulk_update(update_batch, UPDATE_FIELDS, batch_size=DB_CHUNK)
                    update_batch.clear()

            # Sisa batch dalam chunk
            if insert_batch:
                with transaction.atomic():
                    Sipd.objects.bulk_create(insert_batch, batch_size=DB_CHUNK, ignore_conflicts=True)
                insert_batch.clear()

            if update_batch:
                UPDATE_FIELDS = [
                    "nama_sub_skpd", "kode_program", "nama_program",
                    "kode_kegiatan", "nama_kegiatan", "nama_sub_kegiatan",
                    "nama_rekening", "jenis_dokumen", "jenis_transaksi",
                    "nomor_dpt", "tanggal_dokumen", "keterangan_dokumen",
                    "nilai_realisasi", "nilai_setoran", "nomor_spp",
                    "tanggal_spp", "tanggal_spm", "tanggal_sp2d",
                    "tanggal_transfer", "nilai_sp2d", "updated_at",
                ]
                with transaction.atomic():
                    Sipd.objects.bulk_update(update_batch, UPDATE_FIELDS, batch_size=DB_CHUNK)
                update_batch.clear()

    skipped_summary = [
        {"reason": r, "count": c}
        for r, c in skipped_reason_counts.items()
    ]

    result = {
        "done": True,
        "saved": saved,
        "updated": updated,
        "skipped": skipped,
        "total": total_rows,
        "updated_reason": f"Data transaksi sudah ada di database untuk Tahun {tahun}. Sistem memperbarui nilai realisasi, tanggal, dan informasi terkait dengan data terbaru dari file Excel.",
        "skipped_summary": skipped_summary,
        "updated_items": updated_items,
        "skipped_items": skipped_items,
    }

    cache.set(cache_key, result, 3600)
    return result
