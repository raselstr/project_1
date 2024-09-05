from django.apps import AppConfig


class PaguConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pagu'
    
    def ready(self):
        import signals.models_signals
