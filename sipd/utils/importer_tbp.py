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

from sipd.models import TBP
from .mapping import EXCEL_FIELD_MAPPING_TBP


READ_CHUNK = 2000
DB_CHUNK = 500

DATE_FIELDS = {"tanggal_tbp"}

UNIQUE_FIELDS = ("tahun", "nomor_tbp")


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
def import_tbp_excel(file_path: str, tahun: int, cache_key: str):
    df = pd.read_excel(file_path)
    total_rows = len(df)

    processed = 0
    saved = 0
    updated = 0
    skipped = 0

    seen_in_file = set()

    # Pre-load existing map
    existing_map = {
        (obj.tahun, obj.nomor_tbp): obj
        for obj in TBP.objects.filter(tahun=tahun)
    }

    log_path = Path(settings.MEDIA_ROOT) / "import" / f"tbp_log_{tahun}.csv"
    skipped_path = Path(settings.MEDIA_ROOT) / "import" / f"tbp_skipped_{tahun}.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    updated_items = []
    skipped_items = []
    skipped_reason_counts = defaultdict(int)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, "w", newline="", encoding="utf-8") as f_log, \
         open(skipped_path, "w", newline="", encoding="utf-8") as f_skip:

        writer_log = csv.writer(f_log)
        writer_log.writerow(["row_excel", "nomor_tbp", "status_tbp", "status", "alasan", "tanggal_import"])

        writer_skip = csv.writer(f_skip)
        writer_skip.writerow(["row", "reason", "tanggal_import"])

        insert_batch = []
        update_batch = []

        for start in range(0, total_rows, READ_CHUNK):
            df_chunk = df.iloc[start:start + READ_CHUNK]

            for idx, row in df_chunk.iterrows():
                processed += 1
                excel_row_num = processed + 1

                if processed % 150 == 0:
                    cache.set(
                        cache_key,
                        {"current": processed, "total": total_rows, "done": False},
                        3600
                    )

                try:
                    data = {"tahun": tahun}

                    # mapping excel → model
                    for excel_col, model_field in EXCEL_FIELD_MAPPING_TBP.items():
                        val = row.get(excel_col)

                        if "nilai" in model_field:
                            data[model_field] = parse_indonesian_decimal(val)
                        elif model_field in DATE_FIELDS:
                            data[model_field] = to_date(val)
                        else:
                            data[model_field] = clean_str(val)

                    # validasi unique kosong
                    if any(data.get(f, "") == "" for f in UNIQUE_FIELDS):
                        reason = "Kolom nomor TBP kosong / draft"
                        skipped += 1
                        skipped_reason_counts[reason] += 1
                        if len(skipped_items) < 100:
                            skipped_items.append({
                                "excel_row": excel_row_num,
                                "nomor_tbp": data.get("nomor_tbp") or "-",
                                "keterangan": data.get("keterangan_tbp") or "-",
                                "status": "DILEWATI",
                                "reason": reason,
                            })
                        writer_skip.writerow([excel_row_num, reason, now_str])
                        writer_log.writerow([excel_row_num, data.get("nomor_tbp") or "-", data.get("status_tbp") or "-", "DILEWATI", reason, now_str])
                        continue

                    key = tuple(data[f] for f in UNIQUE_FIELDS)

                    # skip duplicate dalam file
                    if key in seen_in_file:
                        reason = "Nomor TBP ganda dalam file Excel yang sama"
                        skipped += 1
                        skipped_reason_counts[reason] += 1
                        if len(skipped_items) < 100:
                            skipped_items.append({
                                "excel_row": excel_row_num,
                                "nomor_tbp": data.get("nomor_tbp") or "-",
                                "keterangan": data.get("keterangan_tbp") or "-",
                                "status": "DILEWATI",
                                "reason": reason,
                            })
                        writer_skip.writerow([excel_row_num, reason, now_str])
                        writer_log.writerow([excel_row_num, data.get("nomor_tbp") or "-", data.get("status_tbp") or "-", "DILEWATI", reason, now_str])
                        continue
                    seen_in_file.add(key)

                    # CREATE / UPDATE
                    if key in existing_map:
                        obj = existing_map[key]
                        obj.tanggal_tbp = data.get("tanggal_tbp")
                        obj.keterangan_tbp = data.get("keterangan_tbp")
                        obj.status_tbp = data.get("status_tbp")
                        obj.nilai_tbp = data.get("nilai_tbp")

                        update_batch.append(obj)
                        updated += 1
                        reason = f"Nomor TBP sudah ada di database Tahun {tahun}. Data diperbarui (Nilai: Rp {data.get('nilai_tbp', 0):,.0f})."
                        if len(updated_items) < 100:
                            updated_items.append({
                                "excel_row": excel_row_num,
                                "nomor_tbp": data.get("nomor_tbp") or "-",
                                "keterangan": data.get("keterangan_tbp") or "-",
                                "status": "DIPERBARUI",
                                "reason": reason,
                            })
                        writer_log.writerow([excel_row_num, data.get("nomor_tbp") or "-", data.get("status_tbp") or "-", "DIPERBARUI", reason, now_str])
                    else:
                        obj = TBP(**data)
                        insert_batch.append(obj)
                        existing_map[key] = obj
                        saved += 1
                        writer_log.writerow([excel_row_num, data.get("nomor_tbp") or "-", data.get("status_tbp") or "-", "BARU", "Data baru berhasil disimpan", now_str])

                except Exception as e:
                    reason = f"Format data error: {str(e)}"
                    skipped += 1
                    skipped_reason_counts["Format data error"] += 1
                    if len(skipped_items) < 100:
                        skipped_items.append({
                            "excel_row": excel_row_num,
                            "nomor_tbp": data.get("nomor_tbp", "-"),
                            "keterangan": data.get("keterangan_tbp", "-"),
                            "status": "DILEWATI",
                            "reason": reason,
                        })
                    writer_skip.writerow([excel_row_num, reason, now_str])
                    writer_log.writerow([excel_row_num, data.get("nomor_tbp", "-"), data.get("status_tbp", "-"), "DILEWATI", reason, now_str])
                    continue

                if len(insert_batch) >= DB_CHUNK:
                    with transaction.atomic():
                        TBP.objects.bulk_create(insert_batch, batch_size=DB_CHUNK)
                    insert_batch.clear()

                if len(update_batch) >= DB_CHUNK:
                    with transaction.atomic():
                        TBP.objects.bulk_update(
                            update_batch,
                            ["tanggal_tbp", "keterangan_tbp", "status_tbp", "nilai_tbp", "updated_at"],
                            batch_size=DB_CHUNK
                        )
                    update_batch.clear()

            if insert_batch:
                with transaction.atomic():
                    TBP.objects.bulk_create(insert_batch, batch_size=DB_CHUNK)
                insert_batch.clear()

            if update_batch:
                with transaction.atomic():
                    TBP.objects.bulk_update(
                        update_batch,
                        ["tanggal_tbp", "keterangan_tbp", "status_tbp", "nilai_tbp", "updated_at"],
                        batch_size=DB_CHUNK
                    )
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
        "updated_reason": f"Nomor TBP sudah terdaftar di database untuk Tahun {tahun}. Sistem memperbarui tanggal, keterangan, status, dan nilai TBP dengan data terbaru dari file Excel.",
        "skipped_summary": skipped_summary,
        "updated_items": updated_items,
        "skipped_items": skipped_items,
    }

    cache.set(cache_key, result, 3600)
    return result
