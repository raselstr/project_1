from celery import shared_task
from .utils.importer import import_sipd_excel


@shared_task(bind=True)
def import_sipd_task(self, file_path, tahun):
    cache_key = f"sipd_{self.request.id}"
    return import_sipd_excel(file_path, tahun, cache_key)
