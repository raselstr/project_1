from import_export import resources
from .models import DankelProg,DankelKeg,Dankelsub,DausgpendidikanProg, DausgpendidikanKeg, DausgpendidikanSub, DausgkesehatanProg, DausgkesehatanKeg, DausgkesehatanSub, DausgpuProg, DausgpuKeg, DausgpuSub
from opd.models import Opd, Subopd
from pagu.models import Pagudausg

class DankelProgResource(resources.ModelResource):
    class Meta:
        model = DankelProg

class DankelKegResource(resources.ModelResource):
    class Meta:
        model = DankelKeg

class DankelsubResource(resources.ModelResource):
    class Meta:
        model = Dankelsub

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

class OpdResource(resources.ModelResource):
    class Meta:
        model = Opd

class SubopdResource(resources.ModelResource):
    class Meta:
        model = Subopd

class PaguResource(resources.ModelResource):
    class Meta:
        model = Pagudausg



