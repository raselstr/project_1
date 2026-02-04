from pendidikan.models import (
    Rencanaposting,
    Rencana,
    Realisasi,
    Rencanapostingsisa,
    Rencanasisa,
    Realisasisisa,
)
from dausg.models import Subkegiatan
from penerimaan.models import Penerimaan
from pendidikan.tables import RealisasiTable, RencanapendidikanpostingTable
from pendidikan.forms.form_pendidikan import RealisasiFilterForm, RealisasiForm

SIPD_REGISTRY = {
    'realisasi': {
        'tabel_realisasi': RealisasiTable,
        'tabel_rencana': RencanapendidikanpostingTable,
        'form_filter': RealisasiFilterForm,
        'form_data': RealisasiForm,

        'model_rencana': Rencanaposting,
        'model_pagu': Rencana,
        'model_realisasi': Realisasi,

        'model_dana': Subkegiatan,
        'model_penerimaan': Penerimaan,

        'session_dana': 'dau-dukungan-bidang-pendidikan',
        'url_sp2d' : "realisasi_pendidikan_sp2d",
        
    },
    'realisasisisa': {
        'tabel_realisasi': RealisasiTable,
        'tabel_rencana': RencanapendidikanpostingTable,
        'form_filter': RealisasiFilterForm,
        'form_data': RealisasiForm,

        'model_rencana': Rencanapostingsisa,
        'model_pagu': Rencanasisa,
        'model_realisasi': Realisasisisa,

        'model_dana': Subkegiatan,
        'model_penerimaan': Penerimaan,

        'session_dana': 'sisa-dana-alokasi-umum-dukungan-bidang-pendidikan',
        'url_sp2d' : "realisasi_pendidikan_sp2dsisa",
    }
}
