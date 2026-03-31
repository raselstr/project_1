# core/helpers/filter_helper.py
from core.services.pagu_service import PaguService
from core.services.realisasi_service import RealisasiService


class FilterHelper:

    @staticmethod
    def tahun_choices():
        tahun = PaguService.get_available_tahun()
        return [("", "Semua Tahun")] + [(t, t) for t in tahun]

    @staticmethod
    def dana_choices():
        dana = RealisasiService.get_available_dana()
        return [("", "Semua Dana")] + list(dana)

    @staticmethod
    def tahap_choices():
        tahap = RealisasiService.get_available_tahap()
        return [("", "Semua Tahap")] + list(tahap)