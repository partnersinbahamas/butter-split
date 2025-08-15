from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls

from .views import index, UserCreateView, EventCreateView, EventListView, EventDeleteView, EventUpdateView, EventDetailView

urlpatterns = [
    path('', index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/registrate', UserCreateView.as_view(), name='registrate'),
    path('event/create', EventCreateView.as_view(), name='event-create'),
    path('event/list', EventListView.as_view(), name='event-list'),
    path('event/delete/<int:pk>', EventDeleteView.as_view(), name='event-delete'),
    path('event/update/<int:pk>', EventUpdateView.as_view(), name='event-update'),
    path('event/<int:pk>', EventDetailView.as_view(), name='event-detail'),
] + debug_toolbar_urls()

app_name = 'service'
