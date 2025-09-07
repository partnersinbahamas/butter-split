from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, DetailView

from .forms import UserCreateForm, EventForm, EventListSearchForm, EventDetailForm, ExpenseForm, UserLoginForm
from .models import Event, Expense

MAX_EVENT_CHIPS = 3

def index(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        event_chips = Event.objects.filter(owner=request.user)
    else:
        event_chips = Event.objects.filter(owner=None, session_id=request.session.session_key)

    event_chips = event_chips.order_by('-created_at')

    context = {
        'event_chips': event_chips[:MAX_EVENT_CHIPS],
        'max_event_chips': MAX_EVENT_CHIPS,
        'is_max_events_reached': event_chips.count() > MAX_EVENT_CHIPS,
    }

    return render(request, 'pages/index.html', context=context)

class UserLoginView(LoginView):
    model = get_user_model()
    template_name = 'registration/login.html'
    form_class = UserLoginForm

    def get_success_url(self):
        return reverse_lazy('service:index')


class UserCreateView(CreateView):
    model = get_user_model()
    form_class = UserCreateForm
    template_name = 'registration/login.html'

    def get_success_url(self):
        return reverse_lazy('service:login')


class EventCreateView(CreateView):
    model = Event
    template_name = 'pages/event_action_page.html'
    form_class = EventForm

    def get_success_url(self):
        return reverse_lazy('service:event-detail', kwargs={'pk': self.object.id})

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
    form_class = EventListSearchForm
    template_name = 'pages/event_list.html'
    context_object_name = 'event_list'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context['search_form'] = EventListSearchForm(initial=self.request.GET)

        return context

    def get_queryset(self):
        form = EventListSearchForm(self.request.GET)
        queryset = Event.objects.filter(
            owner=None,
            session_id=self.request.session.session_key
        )

        if self.request.user and self.request.user.is_authenticated:
            queryset = Event.objects.filter(owner=self.request.user)


        if form.is_valid() and form.cleaned_data.get('name'):
            queryset = queryset.filter(name__icontains=form.cleaned_data['name'])

        return (
            queryset
                .order_by('-created_at')
                .select_related('owner', 'currency')
                .prefetch_related('participants', 'expenses')
        )


class EventDeleteView(DeleteView):
    model = Event
    template_name = 'pages/event-delete-confirmation.html'
    context_object_name = 'event'
    success_url = reverse_lazy('service:event-list')

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)

        return context

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.is_user_can_manage(request):
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied()


class EventUpdateView(UpdateView):
    model = Event
    template_name = 'pages/event_action_page.html'
    form_class = EventForm

    def get_success_url(self):
        return reverse_lazy('service:event-detail', kwargs={'pk': self.object.id})

    def get_form_kwargs(self):
        kwargs = super(EventUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['session_key'] = self.request.session.session_key

        return kwargs


class EventDetailView(DetailView):
    model = Event
    template_name = 'pages/event_detail.html'
    context_object_name = 'event'
    form_class = EventDetailForm

    def get_queryset(self):
        return (Event.objects
        .select_related('owner', 'currency')
        .prefetch_related(
            'participants',
            Prefetch(
                'expenses',
                queryset=Expense.objects.select_related('payer')
            ),
        ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EventDetailForm(instance=self.object)
        context['can_manage'] = self.object.is_user_can_manage(self.request)

        if 'expense_form' in kwargs:
            context['expense_form'] = kwargs['expense_form']
        else:
            context['expense_form'] = ExpenseForm(event=self.object)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        expense_delete_id = request.POST.get('Delete')

        if not self.object.is_user_can_manage(request):
            raise PermissionDenied()

        if expense_delete_id:
            expense_to_delete = Expense.objects.get(id=expense_delete_id, event=self.object)
            expense_to_delete.delete()

            return HttpResponseRedirect(reverse_lazy('service:event-detail', kwargs={'pk': self.object.id}))

        form = ExpenseForm(data=request.POST, instance=Expense(event=self.object), event=self.object)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse_lazy('service:event-detail', kwargs={'pk': self.object.pk}))

        context = self.get_context_data(expense_form=form)
        return self.render_to_response(context)


def event_calculate_view(request: HttpRequest, pk: int) -> HttpResponse:
    event = (
        Event.objects
            .select_related('owner', 'currency')
            .prefetch_related('participants', 'expenses'
        ).get(pk=pk))

    settlements = event.calculate_participants_debt()

    context = {
        'event': event,
        'settlements': settlements
    }

    return render(request, 'pages/event-calculate-page.html', context)
