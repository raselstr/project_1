from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator
from django.apps import apps

    
def unik(value, app_name: str, model_name:str, field:str):
    apps_model = apps.get_model(app_name, model_name)
    filter_kwargs = {field: value}
    filter = apps_model.objects.filter(**filter_kwargs).exists()
    if filter:
        raise ValidationError(f'Data {value} ini sudah ada. Silakan masukkan data yang berbeda.')
    
number_validator = RegexValidator(
    regex='^[0-9]+$',
    message='Kode OPD harus berupa angka'
)

minimal2_validator = MinLengthValidator(
    limit_value=2,
    message="Nama OPD minimal 2 huruf"
)