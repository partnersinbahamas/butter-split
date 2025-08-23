from decimal import Decimal

from django.contrib.auth import get_user_model, login
from django.db.models import Prefetch
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, DetailView

from .forms import UserCreateForm, EventForm, EventListSearchForm, EventDetailForm, ExpenseForm
from .models import Event, Expense

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
    template_name = 'pages/event_action_page.html'
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
                .prefetch_related('participants')
        )


class EventDeleteView(DeleteView):
    model = Event
    template_name = 'pages/event-delete-confirmation.html'
    context_object_name = 'event'
    success_url = reverse_lazy('service:event-list')


class EventUpdateView(UpdateView):
    model = Event
    template_name = 'pages/event_action_page.html'
    form_class = EventForm
    success_url = reverse_lazy('service:event-list')

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

        if 'expense_form' in kwargs:
            context['expense_form'] = kwargs['expense_form']
        else:
            context['expense_form'] = ExpenseForm(event=self.object)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = ExpenseForm(data=request.POST, instance=Expense(event=self.object), event=self.object)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse_lazy('service:event-detail', kwargs={'pk': self.object.pk}))

        context = self.get_context_data(expense_form=form)
        return self.render_to_response(context)
