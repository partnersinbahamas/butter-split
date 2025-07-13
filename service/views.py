from django.contrib.auth import get_user_model, login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserCreateForm, EventForm
from .models import Event


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'pages/index.html')


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
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.owner = self.request.user
        else:
            form.instance.owner = None

            if not self.request.session.session_key:
                self.request.session.save()
            form.instance.session_id = self.request.session.session_key

        self.object = form.save()
        return super().form_valid(form)
