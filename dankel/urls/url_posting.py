from django.urls import path

from ..views import view_posting

urlpatterns = [
    path('dankellist/', view_posting.list, name="posting_list"),
    path('dankelposting/', view_posting.posting, name="posting_simpan"),
    path('dankelhome/', view_posting.home, name="posting_home"),
]