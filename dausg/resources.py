from import_export import resources
from .models import DankelProg,DausgpendidikanProg, DausgpendidikanKeg, DausgpendidikanSub

class DankelProgResource(resources.ModelResource):
    class Meta:
        model = DankelProg

class DausgpendidikanProgResource(resources.ModelResource):
    class Meta:
        model = DausgpendidikanProg

class DausgpendidikanKegResource(resources.ModelResource):
    class Meta:
        model = DausgpendidikanKeg

class DausgpendidikanSubResource(resources.ModelResource):
    class Meta:
        model = DausgpendidikanSub



