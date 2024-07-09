# your_project/middleware.py
from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URL names that do not require login
        exempt_urls = [
            'login',  # Name of your login URL
            'logout',  # Name of your logout URL
            'admin:index',  # Admin index URL
            # Add other exempt URLs here
        ]
        
        # Allow access to exempt URLs without login
        if not request.user.is_authenticated:
            current_url_name = resolve(request.path_info).url_name
            if current_url_name not in exempt_urls:
                return redirect(settings.LOGIN_URL)
        
        response = self.get_response(request)
        return response
