import django_tables2 as tables
from .models import Realisasikesehatan, Realisasikesehatansisa
from django.urls import reverse
from django.utils.html import format_html

model = Realisasikesehatan
model_sisa = Realisasikesehatansisa

class TotalRealisasiColumn(tables.Column):
    def render_footer(self, bound_column, table):
        return sum(bound_column.accessor.resolve(row) for row in table.data)

class BaseRealisasiTable(tables.Table):
    aksi = tables.Column(empty_values=(), orderable=False, verbose_name='Aksi')
    verif = tables.Column(empty_values=(), orderable=False, verbose_name='Verifikasi')
    output_satuan = tables.Column(empty_values=(), verbose_name='Output dan Satuan')
    realisasi_tgl = tables.Column(footer="Total Realisasi:")
    realisasi_nilai = TotalRealisasiColumn()

    class Meta:
        template_name = "django_tables2/bootstrap4.html"
        attrs = {
            "class": "display table-bordered",
            "id": "tabel1",
            "width": "100%",
            'th': {'style': "text-align: center;"},
            'tf': {'style': "text-align: right;"},
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Ambil request dari kwargs
        super().__init__(*args, **kwargs)  # Panggil inisialisasi superclass

    def render_aksi(self, record):
        opd = self.request.session.get('idsubopd', None)
        if opd not in [70, 67, None] and record.realisasi_verif != 1:
            edit_url = reverse(f'{self.model_name}_update', args=[record.id])
            delete_url = reverse(f'{self.model_name}_delete', args=[record.id])
            return format_html(
                '<a href="{}" class="btn btn-info btn-sm"><i class="fas fa-pencil-alt"></i></a> '
                '<a href="{}" class="btn btn-danger btn-sm"><i class="fas fa-trash"></i></a>',
                edit_url,
                delete_url
            )
        return format_html('<span class="text-muted">Tindakan tidak tersedia</span>')

    def render_verif(self, record):
        akun = self.request.session.get('level', None)
        verif_status = {0: 'Diinput Dinas', 1: 'Disetujui APIP'}
        badge_class = {0: 'badge-warning', 1: 'badge-success'}

        status = verif_status.get(record.realisasi_verif, 'Status Tidak Diketahui')
        badge = badge_class.get(record.realisasi_verif, 'badge-secondary')

        if akun == 'APIP':
            verif_url = reverse(f'{self.model_name}_modal', args=[record.id])
            return format_html(
                '<a href="#" hx-get="{}" hx-target="#verifikasiModal .modal-body" hx-trigger="click" '
                'data-toggle="modal" data-target="#verifikasiModal">'
                '<span class="badge {}">{}</span></a>',
                verif_url, badge, status
            )
        else:
            return format_html('<span class="badge {}">{}</span>', badge, status)

    def render_output_satuan(self, record):
        satuan = getattr(record.realisasi_subkegiatan, 'dausgkesehatansub_satuan', '')
        return format_html('{} {}'.format(record.realisasi_output, satuan))


class RealisasikesehatanTable(BaseRealisasiTable):
    class Meta(BaseRealisasiTable.Meta):
        model = model
        fields = ("aksi", "realisasi_subopd", "realisasi_rencanaposting", "realisasi_sp2d", 
                  "realisasi_tgl", "realisasi_nilai", "output_satuan", "verif")

    model_name = 'realisasi_kesehatan'


class RealisasikesehatanTablesisa(BaseRealisasiTable):
    class Meta(BaseRealisasiTable.Meta):
        model = model_sisa
        fields = ("aksi", "realisasi_subopd", "realisasi_rencanaposting", "realisasi_sp2d", 
                  "realisasi_tgl", "realisasi_nilai", "output_satuan", "verif")

    model_name = 'realisasi_kesehatansisa'

class RekapPaguTable(tables.Table):
    # Mendefinisikan kolom yang akan ditampilkan
    subopd = tables.Column(verbose_name="Sub OPD", footer="Total")
    pagu = TotalRealisasiColumn(verbose_name="Total Pagu", attrs={"td": {"class": "text-right"}})
    total_rencana = TotalRealisasiColumn(verbose_name="Total Rencana", attrs={"td": {"class": "text-right"}})
    total_posting = TotalRealisasiColumn(verbose_name="Total Rencana TerValidasi", attrs={"td": {"class": "text-right"}})
    
    total_tahap1 = TotalRealisasiColumn(verbose_name="Tahap 1", attrs={"td": {"class": "text-right"}})
    total_tahap2 = TotalRealisasiColumn(verbose_name="Tahap 2", attrs={"td": {"class": "text-right"}})
    total_tahap3 = TotalRealisasiColumn(verbose_name="Tahap 3", attrs={"td": {"class": "text-right"}})
    
    total_realisasi = TotalRealisasiColumn(verbose_name="Total Realisasi", attrs={"td": {"class": "text-right"}})
    total_sisa = TotalRealisasiColumn(verbose_name="Sisa Dana", attrs={"td": {"class": "text-right"}})

    class Meta:
        template_name = "django_tables2/bootstrap4-responsive.html"
        attrs = {
            "class": "table table-bordered border-primary table-sm",
            'th': {
                'style': "text-align: center;",
                },
            'tf': {
                'style':"text-align: right;"
                },
            }

class BaseSp2dTable (tables.Table):
    realisasi_tgl = tables.Column(footer="Total")
    realisasi_nilai = TotalRealisasiColumn(attrs={"td": {"class": "text-right"}})
    class Meta:
        template_name = "django_tables2/bootstrap4.html"  # Menggunakan template bootstrap
        fields = ("realisasi_subopd","realisasi_sp2d","realisasi_tgl", "realisasi_nilai","realisasi_tahap_id","realisasi_verif")  # Kolom-kolom yang akan ditampilkan
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

class Sp2dTable(BaseSp2dTable):
    class Meta(BaseSp2dTable.Meta):
        model = model

class Sp2dTablesisa(BaseSp2dTable):
    class Meta(BaseSp2dTable.Meta):
        model = model_sisa
        

