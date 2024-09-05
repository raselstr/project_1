from django.apps import AppConfig


class PendidikanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pendidikan'
    
    def ready(self):
        import signals.models_signals
