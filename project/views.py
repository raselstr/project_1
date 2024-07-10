from django.shortcuts import render

def notfound(request):
    return render(request, '403.html')