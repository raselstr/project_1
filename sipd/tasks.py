from celery import shared_task
from .utils.importer import import_sipd_excel
from .utils.importer_tbp import import_tbp_excel


@shared_task(bind=True)
def import_sipd_task(self, file_path, tahun):
    cache_key = f"sipd_{self.request.id}"
    return import_sipd_excel(file_path, tahun, cache_key)

@shared_task(bind=True)
def import_tbp_task(self, file_path, tahun):
    cache_key = f"tbp_{self.request.id}"
    return import_tbp_excel(file_path, tahun, cache_key)