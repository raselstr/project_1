import django_tables2 as tables
from .models import Realisasi, Realisasisisa, Rencanaposting, Rencanapostingsisa
from django.urls import reverse
from django.utils.html import format_html

model = Realisasi
model_sisa = Realisasisisa
model_rencana = Rencanaposting
model_rencana_sisa = Rencanapostingsisa

class totalrealisasi(tables.Column):
    def __init__(self, *args, getter=None, **kwargs):
        self.getter = getter
        super().__init__(*args, **kwargs)

    def render_footer(self, bound_column, table):
        total = 0
        for row in table.data:
            try:
                if self.getter:
                    total += self.getter(row)
                else:
                    total += bound_column.accessor.resolve(row)
            except Exception:
                pass
        return f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

class BaseRealisasiTable(tables.Table):
    aksi = tables.Column(empty_values=(), orderable=False, verbose_name='Aksi')
    verif = tables.Column(empty_values=(), orderable=False, verbose_name='Verifikasi')
    output_satuan = tables.Column(empty_values=(), verbose_name='Output dan Satuan')
    realisasi_tgl = tables.Column(footer="Total Realisasi:")
    realisasi_nilai = totalrealisasi()

    class Meta:
        template_name = "django_tables2/bootstrap4.html"  # Menggunakan template bootstrap
        attrs = {
            "class": "display table-bordered tabel-dinamis",
            "id":"tabel1",
            'th': {
                'style':"text-align: center;"
                },
            'tf': {
                'style':"text-align: right;"
                },
            }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Ambil request dari kwargs, jika ada
        super().__init__(*args, **kwargs)
    
    def render_aksi(self, record):
        opd = self.request.session.get('idsubopd', None)
        
        # Jika akun == 'Pengguna' dan status verif != 1, maka tampilkan tombol edit dan delete
        if opd not in [70,67,None] and record.realisasi_verif != 1:
            edit_url = reverse(f'{self.model_name}_update', args=[record.id])
            delete_url = reverse(f'{self.model_name}_delete', args=[record.id])
            return format_html(
                '<a href="{}" class="btn btn-info btn-sm"><i class="fas fa-pencil-alt"></i></a> '
                '<a href="{}" class="btn btn-danger btn-sm"><i class="fas fa-trash"></i></a>',
                edit_url,
                delete_url
            )
        
        # Jika status verif sudah 1 (disetujui), maka tombol tidak ditampilkan
        return 'Tindakan tidak tersedia'

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
        try:
            satuan = getattr(record.realisasi_subkegiatan, 'dausgpendidikansub_satuan', '')
            return f"{record.realisasi_output or 0} {satuan}"
        except Exception:
            return ""

class RealisasiTable(BaseRealisasiTable):
    class Meta(BaseRealisasiTable.Meta):
        model = model
        fields = ("aksi", "realisasi_subopd", "realisasi_rencanaposting", "realisasi_sp2d", 
                  "realisasi_tgl", "realisasi_nilai", "output_satuan", "verif")

    model_name = 'realisasi_pendidikan'


class RealisasiTablesisa(BaseRealisasiTable):
    class Meta(BaseRealisasiTable.Meta):
        model = model_sisa
        fields = ("aksi", "realisasi_subopd", "realisasi_rencanaposting", "realisasi_sp2d", 
                  "realisasi_tgl", "realisasi_nilai", "output_satuan", "verif")

    model_name = 'realisasi_pendidikansisa'

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
    total_sisa = totalrealisasi(verbose_name="Sisa Dana", attrs={"td": {"class": "text-right"}})

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


class BaseSp2dTable (tables.Table):
    realisasi_tgl = tables.Column(footer="Total")
    realisasi_nilai = totalrealisasi(attrs={"td": {"class": "text-right"}})
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


class BaseRencanaTable(tables.Table):
    rencana_pagu = totalrealisasi(attrs={"td": {"class": "text-right"}})
    nomor = tables.Column(verbose_name="No", empty_values=())
    satuan_kegiatan = tables.Column(verbose_name="Satuan Kegiatan", accessor="get_satuan_kegiatan")
    kegiatan = tables.Column(verbose_name="Kegiatan", accessor="get_kegiatan")
    subkegiatan = tables.Column(verbose_name="Sub Kegiatan", accessor="get_subkegiatan", footer="Total Keseluruhan")
    rencana_ket = tables.Column(verbose_name="Kode Sub Kegiatan DPA")
    rencana_pagudpa = tables.Column(
        verbose_name="Nilai Pagu Sub Kegiatan sesuai DPA",
        attrs={"td": {"class": "text-right"}},  # ✅ Tambahkan class Bootstrap
    )
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
        order_by = ("rencana_subopd", "rencana_kegiatan")
        fields = (
            "nomor",
            "rencana_subopd",
            "kegiatan",
            "subkegiatan",
            "rencana_pagu",
            "rencana_output",
            "satuan_kegiatan",
            "rencana_ket",
            "rencana_pagudpa",
        )
        exclude = ("rencana_kegiatan",)

class RencanasisaTable(BaseRencanaTable):
    

    class Meta(BaseRencanaTable.Meta):
        model = model_sisa
        order_by = ("rencana_subopd", "rencana_kegiatan")
        fields = (
            "nomor",
            "rencana_subopd",
            "kegiatan",
            "subkegiatan",
            "rencana_pagu",
            "rencana_output",
            "satuan_kegiatan",
            "rencana_ket",
            "rencana_pagudpa",
        )
        exclude = ("rencana_kegiatan",)

class BaseMetaTable:
    template_name = "django_tables2/bootstrap4.html"
    fields = (
        'nomor',
        'subkegiatan',
        'posting_pagu',
        'output_satuan',
        'total_realisasi_pk',
    )
    attrs = {
        'class': 'table table-bordered table-sm',
        'id':'tabel1',
        'th': {'style': "text-align: center;"},
        'tf': {'style': "text-align: right;"},
    }

class BaseRencanapendidikanpostingTable(tables.Table):
    nomor = tables.Column(empty_values=(), verbose_name="No")
    posting_subopd = tables.Column(verbose_name="Sub OPD", accessor="get_subopd",order_by="posting_subopd__sub_nama")
    subkegiatan = tables.Column(verbose_name="Sub Kegiatan", accessor="get_subkegiatan", footer="Total Keseluruhan")
    posting_pagu = totalrealisasi(verbose_name="Pagu", attrs={"td": {"class": "text-right"}})
    total_realisasi_pk = totalrealisasi(
        verbose_name="Realisasi",
        getter=lambda row: row.get_total_realisasi_pk(),
        empty_values=(),
        attrs={"td": {"class": "text-right"}},
    )
    output_satuan = tables.Column(empty_values=(), verbose_name='Rencana Output', attrs={"td": {"class": "text-center"}})
    realisasi_output = tables.Column(empty_values=(), verbose_name='Realisasi Output', attrs={"td": {"class": "text-center"}})

    class Meta(BaseMetaTable):
        sequence = (
            'nomor',
            'posting_subopd',
            'subkegiatan',
            'posting_pagu',
            'output_satuan',
            'total_realisasi_pk',
            'realisasi_output',
        )
        
    
    def __init__(self, *args, show_aksi=False, **kwargs):
        extra = []
        if show_aksi:
            extra.append((
                'aksi',
                tables.Column(
                    empty_values=(),
                    verbose_name='SP2D',
                    attrs={"td": {"class": "text-center"}}
                )
            ))
        super().__init__(*args, extra_columns=extra, **kwargs)


    def render_nomor(self, record, table):
        return list(table.data).index(record) + 1
    
    def get_sp2d_url_name(self):
        return 'realisasi_pendidikan_sp2dsisa' if self._meta.model == model_rencana_sisa else 'realisasi_pendidikan_sp2d'


    def render_aksi(self, record):
        url_name = self.get_sp2d_url_name()
        sp2dinput = reverse(url_name, args=[record.id])
        return format_html(
            '<a href="{}" class="btn btn-info btn-sm"><i class="fas fa-pencil-alt"></i></a>',
            sp2dinput,
        )
    
    def render_total_realisasi_pk(self, record):
        value = record.get_total_realisasi_pk()
        return value

    def render_output_satuan(self, record):
        return f'{record.posting_output} {record.get_satuan_kegiatan()}'
    
    def render_realisasi_output(self, record):
        value = record.get_total_realisasi_output_pk()
        return f'{value} {record.get_satuan_kegiatan()}' if value else '0'

class RencanapendidikanpostingTable(BaseRencanapendidikanpostingTable):
    class Meta(BaseRencanapendidikanpostingTable.Meta):
        model = model_rencana

class RencanapendidikanpostingsisaTable(BaseRencanapendidikanpostingTable):
    class Meta(BaseRencanapendidikanpostingTable.Meta):
        model = model_rencana_sisa