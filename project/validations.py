from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator
from django.apps import apps

    
def unik(value, app_name: str, model_name:str, field:str, instance=None):
    apps_model = apps.get_model(app_name, model_name)
    filter_kwargs = {field: value}
    queryset = apps_model.objects.filter(**filter_kwargs)
    if instance is not None:
        queryset = queryset.exclude(pk=instance.pk)

    if queryset.exists():
        raise ValidationError(f'Data {value} ini sudah ada. Silakan masukkan data yang berbeda.')
    
number_validator = RegexValidator(
    regex='^[0-9]+$',
    message='Data yang diinput harus berupa angka'
)
# text_validator = RegexValidator(
#     regex='^[a-zA-Z0-9\s.,!?@<>\]+$',
#     message='Data yang diinput harus teks'
# )

minimal2_validator = MinLengthValidator(
    limit_value=2,
    message="Data yang diinput minimal 2 karakter"
)