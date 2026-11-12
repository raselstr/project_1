import django_tables2 as tables
from django.utils.html import format_html
from .models import RegisterSP2D


class RegisterSP2DTable(tables.Table):
    no = tables.Column(empty_values=(), verbose_name="No", orderable=False)
    nilai_bruto    = tables.Column(verbose_name="Nilai Bruto (Rp)")
    nilai_potongan = tables.Column(verbose_name="Potongan (Rp)")
    nilai_neto     = tables.Column(verbose_name="Nilai Neto (Rp)")

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
            "class": "table table-bordered table-striped table-hover table-sm",
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
            '<span class="badge badge-{}">{}</span>', badge_color, value
        )

    def render_nilai_bruto(self, value):
        return f"{value:,.0f}"

    def render_nilai_potongan(self, value):
        return f"{value:,.0f}"

    def render_nilai_neto(self, value):
        return f"{value:,.0f}"
