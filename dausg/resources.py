from import_export import resources
from .models import DankelProg,DausgpendidikanProg, DausgpendidikanKeg, DausgpendidikanSub, DausgkesehatanProg, DausgkesehatanKeg, DausgkesehatanSub, DausgpuProg, DausgpuKeg, DausgpuSub

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

class DausgkesehatanProgResource(resources.ModelResource):
    class Meta:
        model = DausgkesehatanProg

class DausgkesehatanKegResource(resources.ModelResource):
    class Meta:
        model = DausgkesehatanKeg

class DausgkesehatanSubResource(resources.ModelResource):
    class Meta:
        model = DausgkesehatanSub

class DausgpuProgResource(resources.ModelResource):
    class Meta:
        model = DausgpuProg

class DausgpuKegResource(resources.ModelResource):
    class Meta:
        model = DausgpuKeg

class DausgpuSubResource(resources.ModelResource):
    class Meta:
        model = DausgpuSub



