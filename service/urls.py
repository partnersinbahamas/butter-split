
from django.urls import path
from debug_toolbar.toolbar import debug_toolbar_urls

from .views import index

urlpatterns = [
    path('', index, name='index'),
] + debug_toolbar_urls()

app_name = 'service'
