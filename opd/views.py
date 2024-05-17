from django.shortcuts import render
from .models import Opd

def index(request):
    # if request.method == "GET":
        return render(request, "opd/opd.html")

# Create your views here.
def opd_list(request):
    opd = Opd.objects.all()
    return render(request, "opd/opd_list.html", {"opd": opd})

