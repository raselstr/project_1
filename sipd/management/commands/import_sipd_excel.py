from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.cache import cache
from sipd.models import Sipd
from sipd.utils.mapping import EXCEL_FIELD_MAPPING

import pandas as pd
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
import csv
import os

BATCH_SIZE = 1000


class Command(BaseCommand):
    help = "Import Excel SIPD + CSV log baris dilewati"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)
        parser.add_argument("--tahun", type=int, required=True)

    def handle(self, *args, **options):
        file_path = options["file_path"]
        tahun = options["tahun"]

        self.stdout.write(f"⏳ Import SIPD dimulai | Tahun {tahun}")

        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stderr.write(f"❌ Gagal membaca Excel: {e}")
            return

        TOTAL = len(df)

        # ================= UTIL =================
        def clean_text(val):
            if pd.isna(val):
                return None
            val = str(val).strip()
            if val == "" or val.lower() == "draft":
                return None
            return val

        def clean_decimal(val):
            if pd.isna(val) or val == "":
                return Decimal("0")
            try:
                return Decimal(str(val))
            except InvalidOperation:
                return Decimal("0")

        def clean_date(val):
            if pd.isna(val) or val == "":
                return None
            if isinstance(val, datetime):
                return val.date()
            if isinstance(val, date):
                return val
            try:
                return pd.to_datetime(val).date()
            except Exception:
                return None

        buffer = {}
        skipped_rows = []
        skipped = 0
        errors = 0

        # ================= LOOP =================
        for idx, row in df.iterrows():

            # progress cache
            cache.set(
                f"sipd_import_{tahun}",
                {"current": idx + 1, "total": TOTAL},
                timeout=600
            )

            try:
                data = {"tahun": tahun}

                for excel_col, model_field in EXCEL_FIELD_MAPPING.items():
                    val = row.get(excel_col)

                    if model_field.startswith("nilai_"):
                        data[model_field] = clean_decimal(val)
                    elif model_field.startswith("tanggal_"):
                        data[model_field] = clean_date(val)
                    else:
                        data[model_field] = clean_text(val)

                # ===== VALIDASI FIELD KUNCI =====
                required_keys = (
                    "kode_sub_skpd",
                    "kode_sub_kegiatan",
                    "kode_rekening",
                    "nomor_dokumen",
                    "nomor_spm",
                    "nomor_sp2d",
                )

                missing = [f for f in required_keys if not data.get(f)]
                if missing:
                    skipped += 1
                    skipped_rows.append({
                        "baris_excel": idx + 2,
                        "alasan": f"Field kosong/draft: {', '.join(missing)}"
                    })
                    continue

                # ===== VALIDASI SIPD KHUSUS =====
                if data["nilai_sp2d"] <= 0:
                    skipped += 1
                    skipped_rows.append({
                        "baris_excel": idx + 2,
                        "alasan": "Nilai SP2D <= 0"
                    })
                    continue

                if data["nilai_realisasi"] > data["nilai_sp2d"]:
                    skipped += 1
                    skipped_rows.append({
                        "baris_excel": idx + 2,
                        "alasan": "Nilai realisasi > SP2D"
                    })
                    continue

                key = (
                    tahun,
                    data["kode_sub_skpd"],
                    data["kode_sub_kegiatan"],
                    data["kode_rekening"],
                    data["nomor_dokumen"],
                    data["nomor_spm"],
                    data["nomor_sp2d"],
                )

                buffer[key] = Sipd(**data)

            except Exception as e:
                errors += 1
                skipped_rows.append({
                    "baris_excel": idx + 2,
                    "alasan": str(e),
                })

        # ================= UPSERT =================
        objects = list(buffer.values())
        saved = 0

        for i in range(0, len(objects), BATCH_SIZE):
            chunk = objects[i:i + BATCH_SIZE]

            with transaction.atomic():
                Sipd.objects.bulk_create(
                    chunk,
                    batch_size=BATCH_SIZE,
                    update_conflicts=True,
                    unique_fields=[
                        "tahun",
                        "kode_sub_skpd",
                        "kode_sub_kegiatan",
                        "kode_rekening",
                        "nomor_dokumen",
                        "nomor_spm",
                        "nomor_sp2d",
                    ],
                    update_fields=[
                        f for f in EXCEL_FIELD_MAPPING.values()
                        if f not in (
                            "kode_sub_skpd",
                            "kode_sub_kegiatan",
                            "kode_rekening",
                            "nomor_dokumen",
                            "nomor_spm",
                            "nomor_sp2d",
                        )
                    ] + ["updated_at"],
                )

            saved += len(chunk)

        cache.delete(f"sipd_import_{tahun}")

        # ================= CSV SKIPPED =================
        if skipped_rows:
            csv_path = os.path.join(
                os.path.dirname(file_path),
                f"sipd_skipped_{tahun}.csv"
            )

            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=skipped_rows[0].keys()
                )
                writer.writeheader()
                writer.writerows(skipped_rows)

            self.stdout.write(f"📄 CSV skip dibuat: {csv_path}")

        self.stdout.write("✅ IMPORT SELESAI")
        self.stdout.write(f"✔️ Disimpan / Update : {saved}")
        self.stdout.write(f"⏭️ Dilewati           : {skipped}")
        self.stdout.write(f"❌ Error              : {errors}")
