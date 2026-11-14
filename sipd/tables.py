# sipd/tables.py
from decimal import Decimal
import django_tables2 as tables
from django.utils.html import format_html
from .models import Sipd
from .models import TBP


def format_rupiah(value):
    if value is None or value == "":
        return "0,00"
    try:
        val = Decimal(str(value))
        return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(value)


class SipdTable(tables.Table):
    no = tables.Column(
        empty_values=(),
        verbose_name="No",
        orderable=False,
        attrs={"th": {"class": "text-center", "style": "width: 45px;"}, "td": {"class": "text-center text-muted font-weight-bold align-middle"}}
    )
    nama_sub_skpd = tables.Column(
        verbose_name="Nama Sub SKPD",
        attrs={"td": {"class": "align-middle small"}}
    )
    kode_sub_kegiatan = tables.Column(
        verbose_name="Kode Sub Kegiatan",
        attrs={"th": {"class": "text-center", "style": "width: 130px;"}, "td": {"class": "text-center align-middle font-weight-bold small"}}
    )
    nama_sub_kegiatan = tables.Column(
        verbose_name="Nama Sub Kegiatan",
        attrs={"td": {"class": "align-middle small"}}
    )
    kode_rekening = tables.Column(
        verbose_name="Kode Rekening",
        attrs={"th": {"class": "text-center", "style": "width: 120px;"}, "td": {"class": "text-center align-middle small"}}
    )
    nama_rekening = tables.Column(
        verbose_name="Nama Rekening",
        attrs={"td": {"class": "align-middle small"}}
    )
    nomor_dokumen = tables.Column(
        verbose_name="No. Dokumen / TBP",
        attrs={"td": {"class": "align-middle font-weight-600", "style": "font-family: monospace; font-size: 11.5px; white-space: nowrap;"}}
    )
    nomor_sp2d = tables.Column(
        verbose_name="Nomor SP2D",
        attrs={"td": {"class": "align-middle font-weight-600 text-primary", "style": "font-family: monospace; font-size: 11.5px; white-space: nowrap;"}}
    )
    tanggal_sp2d = tables.DateColumn(
        format="d-m-Y",
        verbose_name="Tgl SP2D",
        attrs={"th": {"class": "text-center", "style": "width: 100px;"}, "td": {"class": "text-center align-middle", "style": "white-space: nowrap;"}}
    )
    nilai_realisasi = tables.Column(
        verbose_name="Nilai Realisasi (Rp)",
        attrs={"th": {"class": "text-right", "style": "width: 140px;"}, "td": {"class": "text-right font-weight-bold text-success align-middle", "style": "white-space: nowrap;"}}
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
            "class": "table table-bordered table-striped table-hover table-sm mb-0",
            "style": "font-size: 12.5px;",
        }

    def before_render(self, request):
        self.row_counter = 0

    def render_no(self, record):
        self.row_counter = getattr(self, "row_counter", 0) + 1
        return self.row_counter

    def render_nilai_realisasi(self, value):
        return format_rupiah(value)


class TBPTable(tables.Table):
    no = tables.Column(
        empty_values=(),
        verbose_name="No",
        orderable=False,
        attrs={"th": {"class": "text-center", "style": "width: 45px;"}, "td": {"class": "text-center text-muted font-weight-bold align-middle"}}
    )
    tahun = tables.Column(
        verbose_name="Tahun",
        attrs={"th": {"class": "text-center", "style": "width: 70px;"}, "td": {"class": "text-center align-middle font-weight-bold"}}
    )
    tanggal_tbp = tables.DateColumn(
        format="d-m-Y",
        verbose_name="Tgl TBP",
        attrs={"th": {"class": "text-center", "style": "width: 110px;"}, "td": {"class": "text-center align-middle", "style": "white-space: nowrap;"}}
    )
    nomor_tbp = tables.Column(
        verbose_name="Nomor TBP",
        attrs={"td": {"class": "align-middle font-weight-600 text-primary", "style": "font-family: monospace; font-size: 11.5px; white-space: nowrap;"}}
    )
    keterangan_tbp = tables.Column(
        verbose_name="Keterangan",
        attrs={"td": {"class": "align-middle small"}}
    )
    status_tbp = tables.Column(
        verbose_name="Status TBP",
        attrs={"td": {"class": "align-middle small"}}
    )
    nilai_tbp = tables.Column(
        verbose_name="Nilai TBP (Rp)",
        attrs={"th": {"class": "text-right", "style": "width: 140px;"}, "td": {"class": "text-right font-weight-bold text-success align-middle", "style": "white-space: nowrap;"}}
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
            "class": "table table-bordered table-striped table-hover table-sm mb-0",
            "style": "font-size: 12.5px;",
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

    def render_status_tbp(self, value):
        if not value:
            return "-"
        val_str = str(value)
        if "Telah Terbit SP2D" in val_str:
            badge_class = "badge-success"
        elif "Belum Dibuatkan" in val_str:
            badge_class = "badge-warning text-dark"
        else:
            badge_class = "badge-light text-dark border"
        return format_html('<span class="badge {}" style="font-size:11px;">{}</span>', badge_class, val_str)
