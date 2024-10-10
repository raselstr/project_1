import django_tables2 as tables
from .models import Realisasipu
from django.urls import reverse
from django.utils.html import format_html

class totalrealisasi(tables.Column):
    def render_footer(self, bound_column, table):
        return sum(bound_column.accessor.resolve(row) for row in table.data)

class RealisasipuTable(tables.Table):
    aksi = tables.Column(empty_values=(), orderable=False, verbose_name='Aksi')
    verif = tables.Column(empty_values=(), orderable=False, verbose_name='Verifikasi')
    output_satuan = tables.Column(empty_values=(), verbose_name='Output dan Satuan')
    realisasi_tgl = tables.Column(footer="Total Realisasi:")
    realisasi_nilai = totalrealisasi()

    class Meta:
        model = Realisasipu
        template_name = "django_tables2/bootstrap4.html"  # Menggunakan template bootstrap
        fields = ("aksi","realisasi_subopd", "realisasi_rencanaposting", "realisasi_sp2d", "realisasi_tgl", "realisasi_nilai", "output_satuan","verif")  # Kolom-kolom yang akan ditampilkan
        attrs = {
            "class": "display table-bordered",
            "id":"tabel1",
            'th': {
                'style':"text-align: center;"
                },
            'tf': {
                'style':"text-align: right;"
                },
            }
    
    def render_aksi(self, record):
        opd = self.request.session.get('idsubopd', None)
        
        # Jika akun == 'Pengguna' dan status verif != 1, maka tampilkan tombol edit dan delete
        if opd not in [70,67,None] and record.realisasi_verif != 1:
            edit_url = reverse('realisasi_pu_update', args=[record.id])  # Ganti dengan nama url Anda
            delete_url = reverse('realisasi_pu_delete', args=[record.id])  # Ganti dengan nama url Anda
            return format_html(
                '<a href="{}" class="btn btn-info btn-sm"><i class="fas fa-pencil-alt"></i></a> '
                '<a href="{}" class="btn btn-danger btn-sm"><i class="fas fa-trash"></i></a>',
                edit_url,
                delete_url
            )
        
        # Jika status verif sudah 1 (disetujui), maka tombol tidak ditampilkan
        return format_html('<span class="text-muted">Tindakan tidak tersedia</span>')

    def render_verif(self, record):
        akun = self.request.session.get('level', None)
        verif_status = {
            0: 'Diinput Dinas',
            1: 'Disetujui APIP'
        }
        badge_class = {
            0: 'badge-warning',
            1: 'badge-success'
        }

        # Ambil status verifikasi
        status = verif_status.get(record.realisasi_verif, 'Status Tidak Diketahui')
        badge = badge_class.get(record.realisasi_verif, 'badge-secondary')

        # Jika akun adalah 'APIP', berikan link verifikasi
        if akun == 'APIP':
            verif_url = reverse('realisasi_pu_modal', args=[record.id])  # URL untuk verifikasi
            return format_html(
                '<a href="#" hx-get="{}" hx-target="#verifikasiModal .modal-body" hx-trigger="click" data-toggle="modal" data-target="#verifikasiModal">'
                '<span class="badge {}">{}</span></a>',
                verif_url, badge, status
            )
        else:
            # Jika bukan 'APIP', tampilkan status tanpa link
            return format_html('<span class="badge {}">{}</span>', badge, status)
    
    def render_output_satuan(self, record):
        satuan = record.realisasi_subkegiatan.dausgpusub_satuan  # Ganti 'satuan' dengan nama field yang sesuai dari model Subkegiatan
        return format_html(
            '{} {}'.format(record.realisasi_output, satuan)  # Gabungkan output dan satuan
        )
    def render_footer(self, bound_column, table):
        return sum(bound_column.accessor.resolve(row) for row in table.data)
    
class RekapPaguTable(tables.Table):
    # Mendefinisikan kolom yang akan ditampilkan
    subopd = tables.Column(verbose_name="Sub OPD", footer="Total")
    pagu = totalrealisasi(verbose_name="Total Pagu", attrs={"td": {"class": "text-right"}})
    total_rencana = totalrealisasi(verbose_name="Total Rencana", attrs={"td": {"class": "text-right"}})
    total_posting = totalrealisasi(verbose_name="Total Rencana TerValidasi", attrs={"td": {"class": "text-right"}})
    total_tahap1 = totalrealisasi(verbose_name="Tahap 1", attrs={"td": {"class": "text-right"}})
    total_tahap2 = totalrealisasi(verbose_name="Tahap 2", attrs={"td": {"class": "text-right"}})
    total_tahap3 = totalrealisasi(verbose_name="Tahap 3", attrs={"td": {"class": "text-right"}})
    total_realisasi = totalrealisasi(verbose_name="Total Realisasi", attrs={"td": {"class": "text-right"}})

    class Meta:
        template_name = "django_tables2/bootstrap4-responsive.html"
        attrs = {
            "class": "table table-bordered border-primary table-sm",
            'th': {
                'style':"text-align: center;"
                },
            'tf': {
                'style':"text-align: right;"
                },
            }
        