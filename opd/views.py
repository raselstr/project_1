from django.shortcuts import render
from .models import Opd

# Create your views here.
def opd_list(request):
    opd = Opd.objects.all()
    return render(request, "opd/opd_list.html", {"opds": opd})

