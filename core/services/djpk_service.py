from decimal import Decimal

from core.services.pagu_service import PaguService
from core.services.realisasi_service import RealisasiService


class DjpkService:

    @classmethod
    def get_rekap(cls):

        # PAGU
        pagu_data = PaguService.aggregate_by_fields(["tahun", "dana"])

        dana_map = dict(RealisasiService.get_available_dana())

        result = []

        for p in pagu_data:

            tahun = p["tahun"]
            dana_id = p["dana"]
            pagu = p["total"]

            # ambil realisasi khusus tahun + dana ini
            realisasi_data = RealisasiService.get_rekap_per_tahap(
                tahun=tahun,
                dana=dana_id
            )

            for r in realisasi_data:

                realisasi = r["realisasi"]

                result.append({
                    "tahun": tahun,
                    "dana_id": dana_id,
                    "dana_nama": dana_map.get(dana_id, "-"),
                    "tahap_id": r["realisasi_tahap_id"],
                    "tahap_nama": r["realisasi_tahap__tahap_dana"],
                    "pagu": pagu,
                    "realisasi": realisasi,
                    "sisa": pagu - realisasi
                })

        return sorted(
            result,
            key=lambda x: (
                x["tahun"],
                x["dana_nama"],
                x["tahap_id"]
            )
        )