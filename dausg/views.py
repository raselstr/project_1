from django.shortcuts import render

# # Create your views here.

def dausg(request):
    context = {
        "judul": "Dana Alokasi Umum Spesific Grand (DAU SG)", 
    }
        
    return render(request, 'dausg/dausg.html', context)
