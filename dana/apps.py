from django.apps import AppConfig


class DanaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dana'
    
    def ready(self):
        import signals.models_signals
