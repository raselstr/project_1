# sipd/tables.py
from decimal import Decimal
import django_tables2 as tables
from .models import Sipd
from .models import TBP


def format_rupiah(value):
    if value is None:
        return "0"
    try:
        val = Decimal(str(value))
        if val % 1 == 0:
            return f"{int(val):,}".replace(",", ".")
        else:
            return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(value)


class SipdTable(tables.Table):
    no = tables.Column(empty_values=(), verbose_name="No", attrs={"th": {"class": "text-center"}, "td": {"class": "text-center"}})
    nilai_realisasi = tables.Column(
        verbose_name="Nilai Realisasi (Rp)",
        attrs={"th": {"class": "text-right"}, "td": {"class": "text-right font-weight-bold", "style": "white-space: nowrap;"}}
    )

    class Meta:
        model = Sipd
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "no",
            "nama_sub_skpd",
            "kode_sub_kegiatan",
            "nama_sub_kegiatan",
            "kode_rekening",
            "nama_rekening",
            "nomor_dokumen",
            "nomor_sp2d",
            "tanggal_sp2d",
            "nilai_realisasi",
        )
        attrs = {
            "class": "table table-bordered table-striped table-hover table-sm"
        }

    def before_render(self, request):
        self.row_counter = 0

    def render_no(self, record):
        self.row_counter = getattr(self, "row_counter", 0) + 1
        return self.row_counter

    def render_nilai_realisasi(self, value):
        return format_rupiah(value)


class TBPTable(tables.Table):
    no = tables.Column(empty_values=(), verbose_name="No", attrs={"th": {"class": "text-center"}, "td": {"class": "text-center"}})
    tahun = tables.Column(verbose_name="Tahun", attrs={"th": {"class": "text-center"}, "td": {"class": "text-center"}})
    nilai_tbp = tables.Column(
        verbose_name="Nilai TBP (Rp)",
        attrs={"th": {"class": "text-right"}, "td": {"class": "text-right font-weight-bold", "style": "white-space: nowrap;"}}
    )

    class Meta:
        model = TBP
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "no",
            "tahun",
            "tanggal_tbp",
            "nomor_tbp",
            "keterangan_tbp",
            "status_tbp",
            "nilai_tbp",
        )
        attrs = {
            "class": "table table-bordered table-striped table-hover table-sm"
        }

    def before_render(self, request):
        self.row_counter = 0

    def render_no(self, record):
        self.row_counter = getattr(self, "row_counter", 0) + 1
        return self.row_counter

    def render_tahun(self, value):
        return str(value) if value else "-"

    def render_nilai_tbp(self, value):
        return format_rupiah(value)