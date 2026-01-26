# sipd/tables.py
import django_tables2 as tables
from .models import Sipd

class SipdTable(tables.Table):
    no = tables.Column(empty_values=(), verbose_name="No")

    class Meta:
        model = Sipd
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "no",
            "kode_sub_skpd",
            "nama_sub_skpd",
            "kode_program",
            "nama_program",
            "kode_kegiatan",
            "nama_kegiatan",
            "nilai_realisasi",
        )
        attrs = {
            "class": "table table-bordered table-striped table-hover table-sm"
        }

    def render_no(self):
        return self.row_counter

    def before_render(self, request):
        self.row_counter = 0

    def render_no(self, record):
        self.row_counter += 1
        return self.row_counter
