from django.apps import AppConfig


class RencanaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rencana'
    
    def ready(self):
        import signals.models_signals
