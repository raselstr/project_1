import django_tables2 as tables
from .models import Realisasikesehatan
from django.urls import reverse
from django.utils.html import format_html

class totalrealisasi(tables.Column):
    def render_footer(self, bound_column, table):
        return sum(bound_column.accessor.resolve(row) for row in table.data)

class RealisasikesehatanTable(tables.Table):
    aksi = tables.Column(empty_values=(), orderable=False, verbose_name='Aksi')
    verif = tables.Column(empty_values=(), orderable=False, verbose_name='Verifikasi')
    output_satuan = tables.Column(empty_values=(), verbose_name='Output dan Satuan')
    realisasi_tgl = tables.Column(footer="Total Realisasi:")
    realisasi_nilai = totalrealisasi()

    class Meta:
        model = Realisasikesehatan
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
            edit_url = reverse('realisasi_pendidikan_update', args=[record.id])  # Ganti dengan nama url Anda
            delete_url = reverse('realisasi_pendidikan_delete', args=[record.id])  # Ganti dengan nama url Anda
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
            verif_url = reverse('realisasi_kesehatan_modal', args=[record.id])  # URL untuk verifikasi
            return format_html(
                '<a href="#" hx-get="{}" hx-target="#verifikasiModal .modal-body" hx-trigger="click" data-toggle="modal" data-target="#verifikasiModal">'
                '<span class="badge {}">{}</span></a>',
                verif_url, badge, status
            )
        else:
            # Jika bukan 'APIP', tampilkan status tanpa link
            return format_html('<span class="badge {}">{}</span>', badge, status)
    
    def render_output_satuan(self, record):
        satuan = record.realisasi_subkegiatan.dausgkesehatansub_satuan  # Ganti 'satuan' dengan nama field yang sesuai dari model Subkegiatan
        return format_html(
            '{} {}'.format(record.realisasi_output, satuan)  # Gabungkan output dan satuan
        )
    def render_footer(self, bound_column, table):
        return sum(bound_column.accessor.resolve(row) for row in table.data)