import pandas as pd
from datetime import datetime
from django.db import transaction
from sipd.models import Sipd
from .mapping import EXCEL_FIELD_MAPPING  # sesuaikan path


REQUIRED_FIELDS = [
    "tahun",
    "kode_sub_skpd",
    "kode_sub_kegiatan",
    "kode_rekening",
    "nomor_dokumen",
]

def contains_draft(value):
    if not value:
        return False
    return "draft" in str(value).lower()

def parse_date(value):
    if pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def parse_decimal(value):
    if pd.isna(value):
        return 0
    try:
        return float(value)
    except Exception:
        return 0


@transaction.atomic
def import_sipd_excel(file_path, tahun, chunk_size=10000):
    created = 0
    updated = 0
    skipped = 0

    df = pd.read_excel(file_path)
    df = df.dropna(how="all")

    batch = []

    for _, row in df.iterrows():
        data = {"tahun": tahun}

        for excel_col, model_field in EXCEL_FIELD_MAPPING.items():
            value = row.get(excel_col)

            if model_field.startswith("tanggal"):
                data[model_field] = parse_date(value)
            elif model_field.startswith("nilai"):
                data[model_field] = parse_decimal(value)
            else:
                data[model_field] = (
                    None if pd.isna(value) else str(value).strip()
                )

        # ❌ VALIDASI
        invalid = False
        for field in REQUIRED_FIELDS:
            val = data.get(field)
            if val in (None, "","DRAFT", 0) or contains_draft(val):
                invalid = True
                break

        if invalid:
            skipped += 1
            continue

        batch.append(Sipd(**data))

        # 💥 flush batch
        if len(batch) >= chunk_size:
            Sipd.objects.bulk_create(
                batch,
                update_conflicts=True,
                update_fields=list(data.keys()),
                unique_fields=[
                    "tahun",
                    "kode_sub_skpd",
                    "kode_sub_kegiatan",
                    "kode_rekening",
                    "nomor_dokumen",
                ],
            )
            batch.clear()

    # flush sisa
    if batch:
        Sipd.objects.bulk_create(
            batch,
            update_conflicts=True,
            update_fields=list(data.keys()),
            unique_fields=[
                "tahun",
                "kode_sub_skpd",
                "kode_sub_kegiatan",
                "kode_rekening",
                "nomor_dokumen",
            ],
        )

    return {
        "created": created,  # PostgreSQL tidak bisa hitung pasti
        "updated": updated,
        "skipped": skipped,
        "total": created + updated,
    }
