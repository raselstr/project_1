import pandas as pd
import csv
from decimal import Decimal
from pathlib import Path
from datetime import date

from django.conf import settings
from django.core.cache import cache
from django.db import transaction

from sipd.models import Sipd
from .mapping import EXCEL_FIELD_MAPPING

# ================= CONFIG =================
READ_CHUNK = 2000   # jumlah baris per chunk RAM-safe
DB_CHUNK = 500      # jumlah baris untuk bulk_create DB

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
    if pd.isna(val):
        return None
    val = str(val).strip()
    if val.lower() in ("", "nan", "none", "null", "draft", "-"):
        return None
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
        # pandas Timestamp / datetime
        if hasattr(val, "date"):
            return val.date()
        # string → parse pakai pandas
        parsed = pd.to_datetime(val, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date()
    except Exception:
        return None

# ================= IMPORT FUNCTION =================
def import_sipd_excel(file_path: str, tahun: int, cache_key: str):
    """
    Import Excel SIPD per chunk tanpa menggunakan chunksize (RAM-safe).
    Menyimpan progress ke cache dan skipped rows ke CSV.
    """

    # total rows
    total_rows = pd.read_excel(file_path, usecols=[0]).shape[0]
    processed = 0
    saved = 0
    skipped = 0

    # existing unique keys di DB
    existing_keys = set(Sipd.objects.values_list(*UNIQUE_FIELDS))

    # duplikat di file
    seen_in_file = set()

    # skipped CSV
    skipped_path = Path(settings.MEDIA_ROOT) / f"sipd_skipped_{tahun}.csv"
    skipped_path.parent.mkdir(parents=True, exist_ok=True)

    with open(skipped_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["row", "reason"])

        # ===== baca per-chunk =====
        for start in range(0, total_rows, READ_CHUNK):
            df_chunk = pd.read_excel(
                file_path,
                skiprows=range(1, start + 1),  # skip header + processed rows
                nrows=READ_CHUNK
            )

            batch = []

            for idx, row in df_chunk.iterrows():
                processed += 1
                # update progress cache
                cache.set(cache_key, {"current": processed, "total": total_rows}, 3600)

                try:
                    data = {"tahun": tahun}

                    # mapping kolom Excel → model
                    for excel_col, model_field in EXCEL_FIELD_MAPPING.items():
                        val = row.get(excel_col)

                        if "nilai" in model_field:
                            data[model_field] = to_decimal(val)
                        elif model_field in DATE_FIELDS:
                            data[model_field] = to_date(val)
                        else:
                            data[model_field] = clean_str(val)

                    # validasi unique kosong
                    if any(not data.get(f) for f in UNIQUE_FIELDS):
                        skipped += 1
                        writer.writerow([processed, "unique kosong/draft"])
                        continue

                    key = tuple(data[f] for f in UNIQUE_FIELDS)

                    # duplikat di file
                    if key in seen_in_file:
                        skipped += 1
                        writer.writerow([processed, "duplikat di file excel"])
                        continue
                    seen_in_file.add(key)

                    # duplikat di DB
                    if key in existing_keys:
                        skipped += 1
                        writer.writerow([processed, "sudah ada di database"])
                        continue

                    batch.append(Sipd(**data))

                except Exception as e:
                    skipped += 1
                    writer.writerow([processed, str(e)])
                    continue

                # bulk insert per DB_CHUNK
                if len(batch) >= DB_CHUNK:
                    with transaction.atomic():
                        Sipd.objects.bulk_create(batch, ignore_conflicts=True)
                    saved += len(batch)
                    batch.clear()

            # proses sisa batch di chunk
            if batch:
                with transaction.atomic():
                    Sipd.objects.bulk_create(batch, ignore_conflicts=True)
                saved += len(batch)

    # final progress
    cache.set(
        cache_key,
        {"done": True, "saved": saved, "skipped": skipped, "total": total_rows},
        600,
    )

    return {"saved": saved, "skipped": skipped, "total": total_rows}
