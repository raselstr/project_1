# view_dashboard.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Menu, Submenu
from project.decorators import user_has_permission  # Impor decorator dari project
from project.context_processors import menu_context_processor

@login_required
# @user_has_permission
def index(request):
    context = menu_context_processor(request)
    context['judul'] = 'Dashboard'
    return render(request, "dashboard/dashboard.html", context)