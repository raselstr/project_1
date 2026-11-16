from django.apps import AppConfig


class GajiasnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gajiasn'

    def ready(self):
        import signals.models_signals
