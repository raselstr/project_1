from pathlib import Path
import csv
from decimal import Decimal
from datetime import datetime
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
    Import Excel SIPD per chunk tanpa chunksize.
    Hanya menulis CSV skipped untuk baris kosong/invalid,
    tidak menulis baris yang sudah ada di DB.
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

    # lokasi CSV skipped
    skipped_path = Path(settings.MEDIA_ROOT) / "import" / f"sipd_skipped_{tahun}.csv"
    skipped_path.parent.mkdir(parents=True, exist_ok=True)

    with open(skipped_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["row", "reason", "tanggal_import"])

        for start in range(0, total_rows, READ_CHUNK):
            df_chunk = pd.read_excel(
                file_path,
                skiprows=range(1, start + 1),
                nrows=READ_CHUNK
            )

            batch = []

            for idx, row in df_chunk.iterrows():
                processed += 1
                cache.set(cache_key, {"current": processed, "total": total_rows}, 3600)

                try:
                    data = {"tahun": tahun}

                    # mapping kolom
                    for excel_col, model_field in EXCEL_FIELD_MAPPING.items():
                        val = row.get(excel_col)
                        if "nilai" in model_field:
                            data[model_field] = to_decimal(val)
                        elif model_field in DATE_FIELDS:
                            data[model_field] = to_date(val)
                        else:
                            data[model_field] = clean_str(val)

                    # validasi unique kosong → HANYA INI yang masuk CSV
                    if any(not data.get(f) for f in UNIQUE_FIELDS):
                        skipped += 1
                        writer.writerow([
                            processed,
                            "unique kosong/draft",
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ])
                        continue

                    key = tuple(data[f] for f in UNIQUE_FIELDS)

                    # duplikat di file → skip, tapi tidak masuk CSV
                    if key in seen_in_file:
                        continue
                    seen_in_file.add(key)

                    # duplikat di DB → skip, tapi tidak masuk CSV
                    if key in existing_keys:
                        continue

                    # jika lolos semua, tambahkan ke batch
                    batch.append(Sipd(**data))

                except Exception as e:
                    skipped += 1
                    writer.writerow([
                        processed,
                        f"error: {str(e)}",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ])
                    continue

                # bulk insert per DB_CHUNK
                if len(batch) >= DB_CHUNK:
                    with transaction.atomic():
                        Sipd.objects.bulk_create(batch, ignore_conflicts=True)
                    saved += len(batch)
                    batch.clear()

            # sisa batch tiap chunk
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
