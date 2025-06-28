
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls

from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
] + debug_toolbar_urls()

app_name = 'service'
