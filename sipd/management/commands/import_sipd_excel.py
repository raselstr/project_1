import os

from django.core.management.base import BaseCommand, CommandError
from sipd.utils.excel_importer import import_sipd_excel


class Command(BaseCommand):
    help = "Import data SIPD dari file Excel ke database (tahun diisi manual)"

    def add_arguments(self, parser):
        # file excel
        parser.add_argument(
            "file",
            type=str,
            help="Path file Excel (.xlsx)"
        )

        # tahun anggaran
        parser.add_argument(
            "--tahun",
            type=int,
            required=True,
            help="Tahun anggaran (contoh: 2024)"
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        tahun = options["tahun"]

        # 🔎 validasi file
        if not os.path.exists(file_path):
            raise CommandError(f"File tidak ditemukan: {file_path}")

        # 🔎 validasi tahun
        if tahun < 2000 or tahun > 2100:
            raise CommandError("Tahun anggaran tidak valid")

        self.stdout.write(
            self.style.WARNING(
                f"⏳ Memulai import SIPD dari file '{file_path}' untuk tahun {tahun}..."
            )
        )

        try:
            result = import_sipd_excel(file_path, tahun)
        except Exception as e:
            raise CommandError(f"Gagal import SIPD: {e}")

