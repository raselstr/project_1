from django.shortcuts import render

def index(request):
    context = {
        'judul' : 'Dashboard',
    }
    # if request.method == "GET":
    return render(request, "dashboard/dashboard.html", context)
