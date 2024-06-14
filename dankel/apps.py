from django.apps import AppConfig


class DankelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dankel'
    
    def ready(self):
        import signals.models_signals
