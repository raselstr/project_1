import django_tables2 as tables
from django.utils.html import format_html
from decimal import Decimal
from .models import RegisterSP2D


def format_rupiah(value):
    if value is None or value == "":
        return "0,00"
    try:
        val = Decimal(str(value))
        return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(value)


class RegisterSP2DTable(tables.Table):
    no = tables.Column(
        empty_values=(),
        verbose_name="No",
        orderable=False,
        attrs={"th": {"class": "text-center", "style": "width: 45px;"}, "td": {"class": "text-center text-muted font-weight-bold"}}
    )
    tanggal_pembuatan = tables.DateColumn(
        format="d-m-Y",
        verbose_name="Tgl Pembuatan",
        attrs={"th": {"class": "text-center", "style": "width: 110px;"}, "td": {"class": "text-center", "style": "white-space: nowrap;"}}
    )
    tanggal_pencairan = tables.DateColumn(
        format="d-m-Y",
        verbose_name="Tgl Pencairan",
        attrs={"th": {"class": "text-center", "style": "width: 110px;"}, "td": {"class": "text-center", "style": "white-space: nowrap;"}}
    )
    nomor_sp2d = tables.Column(
        verbose_name="Nomor SP2D",
        attrs={"td": {"style": "font-family: monospace; font-size: 11.5px; white-space: nowrap;"}}
    )
    jenis_sp2d = tables.Column(
        verbose_name="Jenis",
        attrs={"th": {"class": "text-center", "style": "width: 70px;"}, "td": {"class": "text-center"}}
    )
    nilai_bruto = tables.Column(
        verbose_name="Nilai Bruto (Rp)",
        attrs={"th": {"class": "text-right", "style": "width: 140px;"}, "td": {"class": "text-right font-weight-600", "style": "white-space: nowrap;"}}
    )
    nilai_potongan = tables.Column(
        verbose_name="Potongan (Rp)",
        attrs={"th": {"class": "text-right", "style": "width: 120px;"}, "td": {"class": "text-right text-muted", "style": "white-space: nowrap;"}}
    )
    nilai_neto = tables.Column(
        verbose_name="Nilai Neto (Rp)",
        attrs={"th": {"class": "text-right", "style": "width: 140px;"}, "td": {"class": "text-right font-weight-bold text-success", "style": "white-space: nowrap;"}}
    )

    class Meta:
        model = RegisterSP2D
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "no",
            "tanggal_pembuatan",
            "tanggal_pencairan",
            "nomor_sp2d",
            "unit_skpd",
            "nama_penerima",
            "jenis_sp2d",
            "nilai_bruto",
            "nilai_potongan",
            "nilai_neto",
        )
        attrs = {
            "class": "table table-bordered table-striped table-hover table-sm mb-0",
            "style": "font-size: 12.5px;",
        }

    def before_render(self, request):
        self.row_counter = 0

    def render_no(self, record):
        self.row_counter += 1
        return self.row_counter

    def render_jenis_sp2d(self, value):
        colors = {
            "GU": "primary",
            "LS": "success",
            "UP": "info",
            "TU": "warning",
        }
        badge_color = colors.get(str(value).upper(), "secondary")
        return format_html(
            '<span class="badge badge-{} font-weight-600">{}</span>', badge_color, value
        )

    def render_nilai_bruto(self, value):
        return format_rupiah(value)

    def render_nilai_potongan(self, value):
        return format_rupiah(value)

    def render_nilai_neto(self, value):
        return format_rupiah(value)
