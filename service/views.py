from django.contrib.auth import get_user_model, login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import UserCreateForm, EventForm
from .models import Event

MAX_EVENT_CHIPS = 3

def index(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        event_chips = Event.objects.filter(owner=request.user)
    else:
        event_chips = Event.objects.filter(owner=None, session_id=request.session.session_key)

    context = {
        'event_chips': event_chips[:MAX_EVENT_CHIPS],
        'max_event_chips': MAX_EVENT_CHIPS,
        'is_max_events_reached': event_chips.count() > MAX_EVENT_CHIPS,
    }

    return render(request, 'pages/index.html', context=context)


class UserCreateView(CreateView):
    model = get_user_model()
    form_class = UserCreateForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('service:index')

    def get_success_url(self):
        return reverse_lazy('service:index')

    def form_valid(self, form):
        self.object = form.save()

        if not self.request.user.is_authenticated:
            user = self.object
            login(self.request, user)

        return redirect(self.get_success_url())


class EventCreateView(CreateView):
    model = Event
    template_name = 'pages/event_create.html'
    form_class = EventForm
    success_url = reverse_lazy('service:index')

    def get_form_kwargs(self):
        kwargs = super(EventCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['session_key'] = self.request.session.session_key
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.owner = self.request.user
            form.instance.session_id = None
        else:
            form.instance.owner = None

            if not self.request.session.session_key:
                self.request.session.save()
            form.instance.session_id = self.request.session.session_key

        self.object = form.save()
        return super().form_valid(form)


class EventListView(ListView):
    model = Event
    template_name = 'pages/event_list.html'
    context_object_name = 'event_list'
    paginate_by = 4

    def get_queryset(self):
        queryset = Event.objects.filter(
            owner=None,
            session_id=self.request.session.session_key
        )

        if self.request.user and self.request.user.is_authenticated:
            queryset = Event.objects.filter(owner=self.request.user)

        return queryset.order_by('-created_at')

