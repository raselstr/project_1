from django.shortcuts import render
from django.apps import apps


def dataprogram(request, fieldget, model_name, fieldsmodel, template_name):
    Model = apps.get_model('dana', model_name)
    filter_value = request.GET.get(fieldget)
    if fieldget:
        filter_kwargs = {fieldsmodel: filter_value}
        objects = Model.objects.filter(**filter_kwargs)
    else:
        objects = Model.objects.none()
        
    return render(request, template_name, {'objects': objects})

def datasubrinc(request, **kwargs):
    nama_app = kwargs.get('nama_app')
    model_name = kwargs.get('model_name')
    fieldsmodel = kwargs.get('fieldsmodel')
    template_name = kwargs.get('template_name')
    fieldget = kwargs.get('fieldget')
    
    Model = apps.get_model(nama_app, model_name)
    filter_value = request.GET.get(fieldget)
    if fieldget:
        if isinstance(fieldsmodel, list):
            fieldsmodel = '_'.join(fieldsmodel)
        filter_kwargs = {fieldsmodel:filter_value}
        objects = Model.objects.filter(**filter_kwargs)
    else:
        objects = Model.objects.none()
    return render(request, template_name, {'objects': objects})
    

def datakegiatan(request, **kwargs):
    model_name = kwargs.get('model_name')
    fieldsmodel = kwargs.get('fieldsmodel')
    template_name = kwargs.get('template_name')
    fieldget1 = kwargs.get('fieldget1')
    fieldget2 = kwargs.get('fieldget2')

    # Mendapatkan model berdasarkan nama
    Model = apps.get_model('dana', model_name)
    # print("Model", Model)
    
    # Mendapatkan nilai filter dari parameter GET
    filter_value1 = request.GET.get(fieldget1)
    filter_value2 = request.GET.get(fieldget2)
    # print("filter value1:", filter_value1)  # Cetak nilai filter_kwargs
    # print("filter value2:", filter_value2)  # Cetak nilai filter_kwargs
    
    # Memastikan kedua nilai filter ada
    if filter_value1 and filter_value2:
        # Membuat filter_kwargs sebagai kamus
        filter_kwargs = {fieldsmodel[0]: filter_value1, fieldsmodel[1]: filter_value2}
        
        # Melakukan filter pada model
        objects = Model.objects.filter(**filter_kwargs)
    else:
        # Jika tidak ada nilai filter, kembalikan queryset kosong
        objects = Model.objects.none()
    # print(objects)
    
    # Render template dengan objek yang difilter
    return render(request, template_name, {'objects': objects})

def datasubkegiatan(request, **kwargs):
    model_name = kwargs.get('model_name')
    fieldsmodel = kwargs.get('fieldsmodel')
    template_name = kwargs.get('template_name')
    fieldget1 = kwargs.get('fieldget1')
    fieldget2 = kwargs.get('fieldget2')
    fieldget3 = kwargs.get('fieldget3')

    # Mendapatkan model berdasarkan nama
    Model = apps.get_model('dana', model_name)
    
    # Mendapatkan nilai filter dari parameter GET
    filter_value1 = request.GET.get(fieldget1)
    filter_value2 = request.GET.get(fieldget2)
    filter_value3 = request.GET.get(fieldget3)
    
    # Memastikan kedua nilai filter ada
    if filter_value1 and filter_value2 and filter_value3:
        # Membuat filter_kwargs sebagai kamus
        filter_kwargs = {fieldsmodel[0]: filter_value1, fieldsmodel[1]: filter_value2, fieldsmodel[2]: filter_value3}
        
        # Melakukan filter pada model
        objects = Model.objects.filter(**filter_kwargs)
    else:
        # Jika tidak ada nilai filter, kembalikan queryset kosong
        objects = Model.objects.none()
        
    # print(objects)
    
    # Render template dengan objek yang difilter
    return render(request, template_name, {'objects': objects})
