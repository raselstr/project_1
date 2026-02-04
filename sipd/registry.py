from pendidikan.models import (
    Rencanaposting,
    Realisasi,
    Rencanapostingsisa,
    Realisasisisa,
)
from kesehatan.models import (
    Rencanakesehatanposting,
    Rencanakesehatanpostingsisa,
    Realisasikesehatan,
    Realisasikesehatansisa,
)
from pu.models import (
    Rencanapuposting,
    Rencanapupostingsisa,
    Realisasipu,
    Realisasipusisa,
)

SIPD_REGISTRY = {
    'realisasi': {
        'model_rencana': Rencanaposting,
        'model_rencana_sisa': Rencanapostingsisa,
        'model_realisasi': Realisasi,
        'model_realisasi_sisa': Realisasisisa,
        'url_sp2d' : "realisasi_pendidikan_sp2d",
        
    },
    'realisasisisa': {
        'model_rencana': Rencanapostingsisa,
        'model_rencana_sisa': Rencanaposting,
        'model_realisasi': Realisasisisa,
        'model_realisasi_sisa': Realisasi,
        'url_sp2d' : "realisasi_pendidikan_sp2dsisa",
    },
    'realisasi_kesehatan': {
        'model_rencana': Rencanakesehatanposting,
        'model_rencana_sisa': Rencanakesehatanpostingsisa,
        'model_realisasi': Realisasikesehatan,
        'model_realisasi_sisa': Realisasikesehatansisa,
        'url_sp2d' : "realisasi_kesehatan_sp2d",
    },
    'realisasi_kesehatan_sisa': {
        'model_rencana': Rencanakesehatanpostingsisa,
        'model_rencana_sisa': Rencanakesehatanposting,
        'model_realisasi': Realisasikesehatansisa,
        'model_realisasi_sisa': Realisasikesehatan,
        'url_sp2d' : "realisasi_kesehatan_sp2dsisa",
    },
    'realisasi_pu': {
        'model_rencana': Rencanapuposting,
        'model_rencana_sisa': Rencanapupostingsisa,
        'model_realisasi': Realisasipu,
        'model_realisasi_sisa': Realisasipusisa,
        'url_sp2d' : "realisasi_pu_sp2d",
    },
    'realisasi_pu_sisa': {
        'model_rencana': Rencanapupostingsisa,
        'model_rencana_sisa': Rencanapuposting,
        'model_realisasi': Realisasipusisa,
        'model_realisasi_sisa': Realisasipu,
        'url_sp2d' : "realisasi_pu_sp2dsisa",
    },
}

def get_sp2d_sudah_realisasi_global(
    rencana,
    model_rencana,
    model_realisasi,
    model_rencana_sisa,
    model_realisasi_sisa,
):
    """
    Ambil SEMUA SP2D yang sudah direalisasikan,
    baik di realisasi utama maupun sisa.
    """
    sp2d = set()

    # 1. realisasi yang FK-nya cocok
    if isinstance(rencana, model_rencana):
        sp2d |= set(
            model_realisasi.objects.values_list(
                'realisasi_sp2d', flat=True
            )
        )

    if isinstance(rencana, model_rencana_sisa):
        sp2d |= set(
            model_realisasi_sisa.objects.values_list(
                'realisasi_sp2d', flat=True
            )
        )

    # 2. realisasi lawan (tanpa peduli FK rencana)
    sp2d |= set(
        model_realisasi.objects.values_list(
            'realisasi_sp2d', flat=True
        )
    )

    sp2d |= set(
        model_realisasi_sisa.objects.values_list(
            'realisasi_sp2d', flat=True
        )
    )

    return sp2d


def get_rencana_by_pk(pk, *models):
    for model in models:
        obj = (
            model.objects
            .select_related(
                'posting_subopd',
                'posting_subkegiatan',
                'posting_dana'
            )
            .filter(pk=pk)
            .first()
        )
        if obj:
            return obj
    return None