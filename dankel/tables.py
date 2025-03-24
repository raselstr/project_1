import django_tables2 as tables
from .models import RencDankel, RealisasiDankelsisa
from django.urls import reverse
from django.utils.html import format_html

model = RencDankel
model_sisa = RealisasiDankelsisa

class totalrealisasi(tables.Column):
    def render_footer(self, bound_column, table):
        return sum(bound_column.accessor.resolve(row) for row in table.data)


class BaseRencanaTable(tables.Table):
    rencdankel_pagu = totalrealisasi(attrs={"td": {"class": "text-right"}})
    nomor = tables.Column(verbose_name="No", empty_values=())
    program = tables.Column(verbose_name="Program", accessor="get_program")
    kegiatan = tables.Column(verbose_name="Kegiatan", accessor="get_kegiatan")
    subkegiatan = tables.Column(verbose_name="Sub Kegiatan", accessor="get_subkegiatan", footer="Total Keseluruhan")
    satuan_kegiatan = tables.Column(verbose_name="Satuan Kegiatan", accessor="get_satuan_kegiatan")
    rencdankel_ket = tables.Column(verbose_name="Keterangan")
    
    def render_nomor(self, record, table):
        return list(table.data).index(record) + 1
    class Meta:
        template_name = "django_tables2/bootstrap4.html"  # Menggunakan template bootstrap
        attrs = {
            "class": "table table-bordered",
            # "id":"tabel1",
            'th': {
                'style':"text-align: center;"
                },
            'tf': {
                'style':"text-align: right;"
                },
            }
class RencanaTable(BaseRencanaTable):
    class Meta(BaseRencanaTable.Meta):
        model = model
        order_by = ("rencdankel_subopd", "rencdankel_kegiatan")
        fields = (
            "nomor",
            "rencdankel_subopd",
            "program",
            "kegiatan",
            "subkegiatan",
            "rencdankel_pagu",
            "rencdankel_output",
            "satuan_kegiatan",
            "rencdankel_ket",
        )
        exclude = ("rencdankel_kegiatan",)
        
class RencanasisaTable(BaseRencanaTable):
    class Meta(BaseRencanaTable.Meta):
        model = model_sisa
        order_by = ("rencdankelsisa_subopd", "rencdankelsisa_kegiatan")
        fields = (
            "nomor",
            "rencdankelsisa_subopd",
            "progra,",
            "kegiatan",
            "subkegiatan",
            "rencdankelsisa_pagu",
            "rencdankelsisa_output",
            "satuan_kegiatan",
            "rencdankelsisa_ket",
        )
        exclude = ("rencdankelsisa_kegiatan",)