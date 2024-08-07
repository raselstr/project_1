from django.urls import path

from ..views import view_postingsisa

urlpatterns = [
    path('dankelsisalist/', view_postingsisa.list, name="postingsisa_list"),
    path('dankelsisaposting/', view_postingsisa.posting, name="postingsisa_simpan"),
]