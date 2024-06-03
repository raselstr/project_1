from django.shortcuts import render
from django.apps import apps

def dataprogram(request, fieldget, model_name, fieldsmodel, template_name):
    Model = apps.get_model('dana', model_name)
    # print("Mode:", Model)  # Cetak nilai filter_kwargs
    filter_value = request.GET.get(fieldget)
    # print("Filter Value:", filter_value)  # Cetak nilai filter_kwargs
    filter_kwargs = {fieldsmodel: filter_value}
    # print("Filter kwargs:", filter_kwargs)  # Cetak nilai filter_kwargs
    objects = Model.objects.filter(**filter_kwargs)
    # print("Filtered objects:", objects)  # Cetak objek yang difilter
    return render(request, template_name, {'objects': objects})

