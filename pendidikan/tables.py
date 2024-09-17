import django_tables2 as tables
from .models import Realisasi
from django.urls import reverse
from django.utils.html import format_html

class RealisasiTable(tables.Table):
    aksi = tables.Column(empty_values=(), orderable=False, verbose_name='Aksi')
    verif = tables.Column(empty_values=(), orderable=False, verbose_name='Verifikasi')
    output_satuan = tables.Column(empty_values=(), verbose_name='Output dan Satuan')

    class Meta:
        model = Realisasi
        template_name = "django_tables2/bootstrap4.html"  # Menggunakan template bootstrap
        fields = ("aksi","realisasi_subopd", "realisasi_rencanaposting", "realisasi_sp2d", "realisasi_tgl", "realisasi_nilai", "output_satuan","verif")  # Kolom-kolom yang akan ditampilkan
        attrs = {
            "class": "display table-bordered",
            "id":"tabel1",
            'th': {
                    'style':"text-align: center;"
                },
            }
    
    def render_aksi(self, record):
        """Render tombol edit dan delete di kolom 'Aksi'."""
        edit_url = reverse('realisasi_pendidikan_update', args=[record.id])  # Ganti dengan nama url Anda
        delete_url = reverse('realisasi_pendidikan_delete', args=[record.id])  # Ganti dengan nama url Anda
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm"><i class="fas fa-pencil-alt"></i></a> '
            '<a href="{}" class="btn btn-danger btn-sm"><i class="fas fa-trash"></i></a>',
            edit_url,
            delete_url
        )

    def render_verif(self, record):
        if record.realisasi_verif == 0:
            verif_url = reverse('realisasi_pendidikan_modal', args=[record.id])  # URL untuk verifikasi
            return format_html(
            '<a href="#" hx-get="{}" hx-target="#verifikasiModal .modal-body" hx-trigger="click" data-toggle="modal" data-target="#verifikasiModal"><span class="badge badge-warning">Diinput Dinas</span></a>',
            verif_url
        )
        else:
            verif_url = reverse('realisasi_pendidikan_modal', args=[record.id])  # URL untuk verifikasi
            return format_html(
            '<a href="#" hx-get="{}" hx-target="#verifikasiModal .modal-body" hx-trigger="click" data-toggle="modal" data-target="#verifikasiModal"><span class="badge badge-success">Disetujui APIP</span></a>',
            verif_url
        )
    
    def render_output_satuan(self, record):
        satuan = record.realisasi_subkegiatan.dausgpendidikansub_satuan  # Ganti 'satuan' dengan nama field yang sesuai dari model Subkegiatan
        return format_html(
            '{} {}'.format(record.realisasi_output, satuan)  # Gabungkan output dan satuan
        )