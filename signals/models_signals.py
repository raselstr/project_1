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
                    raise ValidationError(f"{model_name} cannot be deleted because it is related to {model.__name__}.")

# Daftar model yang ingin dihubungkan dengan sinyal
# models_to_connect = [
#     'dana.Dana',
#     'dana.Program',
#     'dana.Kegiatan',
#     'dana.Subkegiatan',
#     'dana.TahapDana',
#     'dashboard.SomeModel',  # Contoh model dari aplikasi lain
#     # Tambahkan model lain sesuai kebutuhan
# ]

# Daftar aplikasi yang ingin dihubungkan dengan sinyal
apps_to_connect = [
    'dana', 
    'dashboard',
    'dausg',
    'opd',
    'penerimaan',
    'rencana',
    ]

for app_label in apps_to_connect:
    app_config = apps.get_app_config(app_label)
    for model in app_config.get_models():
        pre_delete.connect(prevent_deletion, sender=model)