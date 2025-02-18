import django_tables2 as tables
from .models import Jadwal
from django.urls import reverse
from django.utils.html import format_html

class JadwalTable(tables.Table):
    aksi = tables.Column(empty_values=(), orderable=False, verbose_name='Aksi')
    jadwal_aktif = tables.Column(verbose_name='Status')

    class Meta:
        model = Jadwal
        template_name = "django_tables2/bootstrap4.html"
        attrs = {
            "class": "display table-bordered",
            "id": "tabel1",
            'th': {'style': "text-align: center;"},
            'tf': {'style': "text-align: right;"},
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def render_aksi(self, record):
        edit_url = reverse('jadwal_edit', args=[record.id])
        delete_url = reverse('jadwal_delete', args=[record.id])
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm"><i class="fas fa-pencil-alt"></i></a> '
            '<a href="{}" class="btn btn-danger btn-sm"><i class="fas fa-trash"></i></a>',
            edit_url, delete_url
        )
    
    def render_jadwal_aktif(self, value):
        return format_html(
            '<span class="badge {}">{}</span>',
            "badge-success" if value else "badge-danger",
            "Aktif" if value else "Nonaktif"
        )
