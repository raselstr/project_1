from pathlib import Path
import csv
from decimal import Decimal
from datetime import datetime
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
    if pd.isna(val):
        return ""
    val = str(val).strip()
    if val.lower() in ("", "nan", "none", "null", "draft", "-"):
        return ""
    return val


def to_decimal(val):
    try:
        if pd.isna(val):
            return Decimal("0")
        return Decimal(str(val).replace(",", ""))
    except Exception:
        return Decimal("0")


def to_date(val):
    try:
        if pd.isna(val):
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

    # 🔥 ambil data existing sekali saja (hemat query)
    existing_map = {
        (obj.tahun, obj.nomor_tbp): obj
        for obj in TBP.objects.filter(tahun=tahun)
    }

    skipped_path = Path(settings.MEDIA_ROOT) / "import" / f"tbp_skipped_{tahun}.csv"
    skipped_path.parent.mkdir(parents=True, exist_ok=True)

    with open(skipped_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["row", "reason", "tanggal_import"])

        insert_batch = []
        update_batch = []

        for start in range(0, total_rows, READ_CHUNK):
            df_chunk = df.iloc[start:start + READ_CHUNK]

            for _, row in df_chunk.iterrows():
                processed += 1

                # progress update
                if processed % 200 == 0:
                    cache.set(cache_key, {
                        "current": processed,
                        "total": total_rows
                    }, 3600)

                try:
                    data = {"tahun": tahun}

                    # mapping excel → model
                    for excel_col, model_field in EXCEL_FIELD_MAPPING_TBP.items():
                        val = row.get(excel_col)

                        if "nilai" in model_field:
                            data[model_field] = to_decimal(val)
                        elif model_field in DATE_FIELDS:
                            data[model_field] = to_date(val)
                        else:
                            data[model_field] = clean_str(val)

                    # validasi unique kosong
                    if any(data.get(f, "") == "" for f in UNIQUE_FIELDS):
                        skipped += 1
                        writer.writerow([
                            processed,
                            "unique kosong/draft",
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ])
                        continue

                    key = tuple(data[f] for f in UNIQUE_FIELDS)

                    # skip duplicate dalam file
                    if key in seen_in_file:
                        continue
                    seen_in_file.add(key)

                    # ======================
                    # CREATE / UPDATE
                    # ======================
                    if key in existing_map:
                        obj = existing_map[key]

                        obj.tanggal_tbp = data.get("tanggal_tbp")
                        obj.keterangan_tbp = data.get("keterangan_tbp")
                        obj.status_tbp = data.get("status_tbp")
                        obj.nilai_tbp = data.get("nilai_tbp")

                        update_batch.append(obj)
                    else:
                        obj = TBP(**data)
                        insert_batch.append(obj)
                        existing_map[key] = obj  # biar gak double insert

                except Exception as e:
                    skipped += 1
                    writer.writerow([
                        processed,
                        f"error: {str(e)}",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ])
                    continue

                # ======================
                # EXECUTE BULK
                # ======================
                if len(insert_batch) >= DB_CHUNK:
                    with transaction.atomic():
                        TBP.objects.bulk_create(insert_batch, batch_size=DB_CHUNK)
                    saved += len(insert_batch)
                    insert_batch.clear()

                if len(update_batch) >= DB_CHUNK:
                    with transaction.atomic():
                        TBP.objects.bulk_update(
                            update_batch,
                            ["tanggal_tbp", "keterangan_tbp", "status_tbp", "nilai_tbp"],
                            batch_size=DB_CHUNK
                        )
                    updated += len(update_batch)
                    update_batch.clear()

        # ======================
        # SISA DATA
        # ======================
        if insert_batch:
            with transaction.atomic():
                TBP.objects.bulk_create(insert_batch, batch_size=DB_CHUNK)
            saved += len(insert_batch)

        if update_batch:
            with transaction.atomic():
                TBP.objects.bulk_update(
                    update_batch,
                    ["tanggal_tbp", "keterangan_tbp", "status_tbp", "nilai_tbp"],
                    batch_size=DB_CHUNK
                )
            updated += len(update_batch)

    # ======================
    # FINAL CACHE
    # ======================
    cache.set(cache_key, {
        "done": True,
        "saved": saved,
        "updated": updated,
        "skipped": skipped,
        "total": total_rows,
    }, 600)

    return {
        "saved": saved,
        "updated": updated,
        "skipped": skipped,
        "total": total_rows
    }