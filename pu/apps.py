from django.apps import AppConfig


class PuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pu'
    
    def ready(self):
        import signals.models_signals
