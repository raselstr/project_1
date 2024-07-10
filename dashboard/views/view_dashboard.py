# view_dashboard.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Menu, Submenu
from project.context_processors import menu_context_processor
from project.decorators import menu_access_required  # Impor decorator dari project

@login_required
@menu_access_required
def index(request):
    context = menu_context_processor(request)
    context['judul'] = 'Dashboard'
    return render(request, "dashboard/dashboard.html", context)