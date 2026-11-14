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
from django.utils import timezone

from sipd.models import TBP
from .mapping import EXCEL_FIELD_MAPPING_TBP


READ_CHUNK = 2000
DB_CHUNK = 500

DATE_FIELDS = {"tanggal_tbp"}

UNIQUE_FIELDS = ("tahun", "nomor_tbp")

MAX_LEN_MAP_TBP = {
    "nomor_tbp": 100,
    "status_tbp": 255,
}

MONTH_MAP = {
    "januari": 1, "jan": 1,
    "februari": 2, "pebruari": 2, "feb": 2, "peb": 2,
    "maret": 3, "mar": 3,
    "april": 4, "apr": 4,
    "mei": 5, "may": 5,
    "juni": 6, "jun": 6,
    "juli": 7, "jul": 7,
    "agustus": 8, "agt": 8, "agu": 8,
    "september": 9, "sep": 9,
    "oktober": 10, "okt": 10,
    "november": 11, "nopember": 11, "nov": 11,
    "desember": 12, "des": 12,
}


# ================= HELPERS =================
def clean_str(val, max_len=None):
    if pd.isna(val) or val is None:
        return ""
    if isinstance(val, float) and val.is_integer():
        val = int(val)
    val = str(val).strip()
    if val.lower() in ("", "nan", "none", "null", "draft", "-"):
        return ""
    if max_len and len(val) > max_len:
        val = val[:max_len]
    return val


def parse_indonesian_decimal(val):
    if val is None or pd.isna(val):
        return Decimal("0")
    if isinstance(val, (int, Decimal)):
        return Decimal(str(val))
    if isinstance(val, float):
        return Decimal(f"{val:.6f}").normalize()

    s = str(val).strip()
    if not s or s.lower() in ("none", "nan", "-", "null", ""):
        return Decimal("0")

    # Format akuntansi dalam tanda kurung: (123.450) -> -123450
    is_negative = False
    if s.startswith("(") and s.endswith(")"):
        is_negative = True
        s = s[1:-1].strip()
    elif s.startswith("-"):
        is_negative = True
        s = s[1:].strip()

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
        dec = Decimal(s)
        return -dec if is_negative else dec
    except (InvalidOperation, ValueError):
        return Decimal("0")


def to_date(val):
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.date()
    if hasattr(val, "date") and callable(getattr(val, "date")):
        try:
            return val.date()
        except Exception:
            pass

    s = str(val).strip()
    if not s or s.lower() in ("none", "nan", "-", "null", ""):
        return None

    # Format teks Indonesia e.g. "18 Februari 2026", "9 Januari 2026", "18-Februari-2026"
    m = re.match(r"^(\d{1,2})[\s\-\/]+([a-zA-Z]+)[\s\-\/]+(\d{4})", s)
    if m:
        day, m_str, year = m.groups()
        m_num = MONTH_MAP.get(m_str.lower())
        if m_num:
            try:
                return datetime(int(year), m_num, int(day)).date()
            except ValueError:
                return None

    # Format ISO: YYYY-MM-DD
    if re.match(r"^\d{4}-\d{1,2}-\d{1,2}", s):
        try:
            return datetime.strptime(s[:10], "%Y-%m-%d").date()
        except ValueError:
            pass

    # Format tanggal standar DD/MM/YYYY atau DD-MM-YYYY
    try:
        p = pd.to_datetime(s, errors="coerce", dayfirst=True)
        if not pd.isna(p):
            return p.date()
    except Exception:
        pass

    return None


def load_tbp_dataframe(file_path: str):
    """
    Membaca file Excel atau CSV TBP secara otomatis mendeteksi baris header
    meskipun terdapat baris judul/metadata di bagian atas file, serta
    menyaring baris total/footer di bagian bawah.
    """
    file_str = str(file_path).lower()
    target_keywords = ["nomor tbp", "tanggal tbp", "status tbp", "nilai tbp"]

    if file_str.endswith(".csv"):
        df_preview = pd.read_csv(file_path, header=None, nrows=30, dtype=str)
        header_idx = 0
        for idx, row in df_preview.iterrows():
            vals = [str(v).strip().lower() for v in row if pd.notna(v)]
            if any(k in vals for k in target_keywords):
                header_idx = idx
                break
        df = pd.read_csv(file_path, header=header_idx)
    else:
        excel_obj = pd.ExcelFile(file_path)
        sheet_name = excel_obj.sheet_names[0]
        df_preview = pd.read_excel(excel_obj, sheet_name=sheet_name, header=None, nrows=30, dtype=str)
        header_idx = 0
        for idx, row in df_preview.iterrows():
            vals = [str(v).strip().lower() for v in row if pd.notna(v)]
            if any(k in vals for k in target_keywords):
                header_idx = idx
                break
        df = pd.read_excel(excel_obj, sheet_name=sheet_name, header=header_idx)

    df.columns = [str(c).strip() for c in df.columns]

    # Filter baris footer / total / baris kosong
    keep_indices = []
    col_map = {str(c).strip().lower(): c for c in df.columns}
    col_nomor_tbp = col_map.get("nomor tbp")

    for idx, row in df.iterrows():
        nomor_tbp = clean_str(row.get(col_nomor_tbp)) if col_nomor_tbp else ""
        first_val = clean_str(row.iloc[0] if len(row) > 0 else "").lower()

        if first_val in ("total", "jumlah", "grand total", "subtotal", "sub total"):
            continue
        if not nomor_tbp:
            continue
        keep_indices.append(idx)

    df = df.loc[keep_indices].reset_index(drop=True)
    return df, header_idx


# ================= IMPORT FUNCTION =================
def import_tbp_excel(file_path: str, tahun: int, cache_key: str):
    """
    Import Excel TBP dengan tracking data baru, diperbaharui, dan dilewati.
    Mendukung file asli SIPD tanpa perlu menghapus header judul atau baris total.
    """
    df, header_offset = load_tbp_dataframe(file_path)
    total_rows = len(df)

    processed = 0
    saved = 0
    updated = 0
    skipped = 0

    seen_in_file = set()

    # Pre-load existing map
    existing_map = {
        (obj.tahun, clean_str(obj.nomor_tbp)): obj
        for obj in TBP.objects.filter(tahun=tahun)
    }

    log_path = Path(settings.MEDIA_ROOT) / "import" / f"tbp_log_{tahun}.csv"
    skipped_path = Path(settings.MEDIA_ROOT) / "import" / f"tbp_skipped_{tahun}.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    updated_items = []
    skipped_items = []
    skipped_reason_counts = defaultdict(int)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Pemetaan kolom case-insensitive
    col_name_map = {str(col).strip().lower(): col for col in df.columns}

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
                excel_row_num = header_offset + processed + 1

                if processed % 150 == 0:
                    cache.set(
                        cache_key,
                        {"current": processed, "total": total_rows, "done": False},
                        3600
                    )

                try:
                    data = {"tahun": tahun}

                    # mapping excel → model dengan normalisasi nama kolom
                    for excel_col, model_field in EXCEL_FIELD_MAPPING_TBP.items():
                        actual_col = col_name_map.get(excel_col.strip().lower())
                        val = row.get(actual_col) if actual_col else None

                        if "nilai" in model_field:
                            data[model_field] = parse_indonesian_decimal(val)
                        elif model_field in DATE_FIELDS:
                            data[model_field] = to_date(val)
                        else:
                            max_len = MAX_LEN_MAP_TBP.get(model_field)
                            data[model_field] = clean_str(val, max_len)

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

                    key = (data["tahun"], data["nomor_tbp"])

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
                        obj.updated_at = timezone.now()

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
                        TBP.objects.bulk_create(insert_batch, batch_size=DB_CHUNK, ignore_conflicts=True)
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
                    TBP.objects.bulk_create(insert_batch, batch_size=DB_CHUNK, ignore_conflicts=True)
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
