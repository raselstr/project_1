from django.apps import AppConfig


class PenerimaanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'penerimaan'
    
    def ready(self):
        import signals.models_signals
