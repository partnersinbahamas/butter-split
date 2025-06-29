from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls

from .views import index, UserCreateView


urlpatterns = [
    path('', index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/registrate', UserCreateView.as_view(), name='registrate'),
] + debug_toolbar_urls()

app_name = 'service'
