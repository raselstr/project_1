# signals/models_signals.py
from django.db.models.signals import pre_delete
from django.core.exceptions import ValidationError
from django.apps import apps
from django.db.models import ForeignKey

def prevent_deletion(sender, instance, **kwargs):
    model_name = sender.__name__
    all_models = apps.get_models()
    
    for model in all_models:
        for field in model._meta.fields:
            if isinstance(field, ForeignKey) and field.related_model == sender:
                if model.objects.filter(**{field.name: instance}).exists():
                    raise ValidationError('Data tidak bisa dihapus karena terhubung dengan data lain.')
    
# Daftar aplikasi yang ingin dihubungkan dengan sinyal
apps_to_connect = [
    'dana', 
    'dashboard',
    'dausg',
    'opd',
    'penerimaan',
    'dankel',
    ]

for app_label in apps_to_connect:
    app_config = apps.get_app_config(app_label)
    for model in app_config.get_models():
        pre_delete.connect(prevent_deletion, sender=model)