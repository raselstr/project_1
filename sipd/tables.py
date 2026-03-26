# sipd/tables.py
import django_tables2 as tables
from .models import Sipd
from .models import TBP

class SipdTable(tables.Table):
    no = tables.Column(empty_values=(), verbose_name="No")

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

    def render_no(self):
        return self.row_counter

    def before_render(self, request):
        self.row_counter = 0

    def render_no(self, record):
        self.row_counter += 1
        return self.row_counter

class TBPTable(tables.Table):
    no = tables.Column(empty_values=(), verbose_name="No")

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

    # nomor urut
    def before_render(self, request):
        self.row_counter = 0

    def render_no(self, record):
        self.row_counter += 1
        return self.row_counter

    # format nilai jadi rupiah (opsional tapi recommended 🔥)
    # def render_nilai_tbp(self, value):
    #     return f"Rp {value:,.2f}"