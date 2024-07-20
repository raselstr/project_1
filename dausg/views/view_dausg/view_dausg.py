from django.shortcuts import render
from project.decorators import menu_access_required

# # Create your views here.
def dausg(request):
    context = {
        "judul": "Dana Alokasi Umum Spesific Grand (DAU SG)", 
    }
        
    return render(request, 'dausg/dausg.html', context)
