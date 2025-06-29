from django.contrib.auth import get_user_model, login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserCreateForm


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
