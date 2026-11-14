from pathlib import Path
import csv
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from collections import defaultdict
import pandas as pd

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

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

MAX_LEN_MAP = {
    "kode_sub_skpd": 50,
    "nama_sub_skpd": 255,
    "kode_program": 50,
    "kode_kegiatan": 50,
    "kode_sub_kegiatan": 50,
    "kode_rekening": 50,
    "nomor_dokumen": 100,
    "jenis_dokumen": 50,
    "jenis_transaksi": 50,
    "nomor_dpt": 100,
    "nomor_spp": 100,
    "nomor_spm": 100,
    "nomor_sp2d": 100,
}

MONTH_MAP = {
    "januari": 1, "jan": 1, "january": 1,
    "februari": 2, "pebruari": 2, "feb": 2, "peb": 2, "february": 2,
    "maret": 3, "mar": 3, "march": 3,
    "april": 4, "apr": 4,
    "mei": 5, "may": 5,
    "juni": 6, "jun": 6, "june": 6,
    "juli": 7, "jul": 7, "july": 7,
    "agustus": 8, "agt": 8, "agu": 8, "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "oktober": 10, "okt": 10, "october": 10, "oct": 10,
    "november": 11, "nopember": 11, "nov": 11, "nop": 11,
    "desember": 12, "des": 12, "december": 12, "dec": 12,
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

    s = str(val).strip().replace("\xa0", " ")
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

    # Hapus prefix Rp atau IDR jika ada
    s = re.sub(r"^(?:[Rr][Pp]\.?|[Ii][Dd][Rr]\.?)\s*", "", s).strip()

    # Cek minus jika letaknya setelah simbol mata uang, contoh: "Rp -1.096,00"
    if s.startswith("-"):
        is_negative = True
        s = s[1:].strip()

    # Hapus suffix rupiah seperti ",-" atau ",--" (contoh: Rp. 1.096,-)
    s = re.sub(r",\s*-+$", "", s).strip()

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
    if isinstance(val, date):
        return val
    if hasattr(val, "date") and callable(getattr(val, "date")):
        try:
            return val.date()
        except Exception:
            pass

    # Tangani angka Excel serial date (e.g. 45340 -> 2024-02-18)
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        if 20000 <= val <= 80000:
            try:
                return pd.to_datetime(val, unit="D", origin="1899-12-30").date()
            except Exception:
                pass

    s = str(val).strip().replace("\xa0", " ")
    if not s or s.lower() in ("none", "nan", "-", "null", "", "0"):
        return None

    # Bersihkan nama hari Indonesia di awal: 'Kamis, 18 Februari 2026' -> '18 Februari 2026'
    s = re.sub(r"^(?:senin|selasa|rabu|kamis|jumat|jum'?at|sabtu|minggu)[,\s]+", "", s, flags=re.IGNORECASE).strip()

    # Bersihkan zona waktu di akhir: WIB, WITA, WIT, UTC, GMT
    s = re.sub(r"\b(?:wib|wita|wit|utc|gmt)\b", "", s, flags=re.IGNORECASE).strip()

    # 1. Format teks bulan Indonesia/Inggris: '18 Februari 2026', '9 Januari 2026', '18 Feb 2026 14.30'
    m_text = re.match(r"^(\d{1,2})[\s\-\/\.]*([a-zA-Z]+)[\s\-\/\.]*(\d{2,4})", s)
    if m_text:
        day_s, m_str, yr_s = m_text.groups()
        m_num = MONTH_MAP.get(m_str.lower())
        if m_num:
            yr = int(yr_s)
            if yr < 100:
                yr += 2000 if yr < 70 else 1900
            try:
                return date(yr, m_num, int(day_s))
            except ValueError:
                pass

    # 2. Format ISO: YYYY-MM-DD / YYYY/MM/DD / YYYY.MM.DD (dengan waktu HH:MM[:SS] atau HH.MM[.SS])
    m_iso = re.match(r"^(\d{4})[\-\/\.](\d{1,2})[\-\/\.](\d{1,2})", s)
    if m_iso:
        yr, mo, dy = map(int, m_iso.groups())
        try:
            return date(yr, mo, dy)
        except ValueError:
            pass

    # 3. Format Indonesia: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY (dengan waktu HH:MM[:SS] atau HH.MM[.SS])
    m_indo = re.match(r"^(\d{1,2})[\-\/\.](\d{1,2})[\-\/\.](\d{2,4})", s)
    if m_indo:
        dy, mo, yr = map(int, m_indo.groups())
        if yr < 100:
            yr += 2000 if yr < 70 else 1900
        try:
            return date(yr, mo, dy)
        except ValueError:
            pass

    # 4. Fallback pandas parser
    try:
        p = pd.to_datetime(s, errors="coerce", dayfirst=True)
        if not pd.isna(p):
            return p.date()
    except Exception:
        pass

    return None


def load_sipd_dataframe(file_path: str):
    """
    Membaca file Excel atau CSV SIPD secara otomatis mendeteksi baris header
    meskipun terdapat baris judul/metadata di bagian atas file, serta
    menyaring baris total/footer di bagian bawah.
    """
    file_str = str(file_path).lower()
    target_keywords = ["nomor dokumen", "kode sub skpd", "nomor sp2d", "kode rekening"]

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

    # Bersihkan nama kolom
    df.columns = [str(c).strip() for c in df.columns]

    # Filter baris footer / total / baris kosong
    keep_indices = []
    col_map = {str(c).strip().lower(): c for c in df.columns}
    col_dok = col_map.get("nomor dokumen")
    col_sp2d = col_map.get("nomor sp2d")
    col_sub_skpd = col_map.get("kode sub skpd")

    for idx, row in df.iterrows():
        dok = clean_str(row.get(col_dok)) if col_dok else ""
        sp2d = clean_str(row.get(col_sp2d)) if col_sp2d else ""
        sub_skpd = clean_str(row.get(col_sub_skpd)) if col_sub_skpd else ""
        first_val = clean_str(row.iloc[0] if len(row) > 0 else "").lower()

        # Lewati baris total/jumlah di bawah tabel
        if first_val in ("total", "jumlah", "grand total", "subtotal", "sub total"):
            continue
        # Jika kolom identifikasi dokumen kosong semua, lewati (bukan data transaksi)
        if not dok and not sp2d and not sub_skpd:
            continue
        keep_indices.append(idx)

    df = df.loc[keep_indices].reset_index(drop=True)
    return df, header_idx


# ================= IMPORT FUNCTION =================
def import_sipd_excel(file_path: str, tahun: int, cache_key: str):
    """
    Import Excel SIPD dengan tracking data baru, diperbaharui, dan dilewati.
    Mendukung file asli SIPD tanpa perlu menghapus header judul atau baris total.
    """
    df, header_offset = load_sipd_dataframe(file_path)
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

    # Pemetaan kolom case-insensitive
    col_name_map = {str(col).strip().lower(): col for col in df.columns}

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
                excel_row_num = header_offset + processed + 1

                if processed % 150 == 0:
                    cache.set(
                        cache_key,
                        {"current": processed, "total": total_rows, "done": False},
                        3600
                    )

                try:
                    data = {"tahun": tahun}

                    # mapping kolom dengan normalisasi nama kolom
                    for excel_col, model_field in EXCEL_FIELD_MAPPING.items():
                        actual_col = col_name_map.get(excel_col.strip().lower())
                        val = row.get(actual_col) if actual_col else None

                        if "nilai" in model_field:
                            data[model_field] = parse_indonesian_decimal(val)
                        elif model_field in DATE_FIELDS:
                            data[model_field] = to_date(val)
                        else:
                            max_len = MAX_LEN_MAP.get(model_field)
                            data[model_field] = clean_str(val, max_len)

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
                        data["updated_at"] = timezone.now()
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
