from celery import shared_task
from .utils.importer import import_register_sp2d_excel


@shared_task(bind=True)
def import_register_sp2d_task(self, file_path: str, tahun: int):
    cache_key = f"register_sp2d_{self.request.id}"
    return import_register_sp2d_excel(file_path, tahun, cache_key)
