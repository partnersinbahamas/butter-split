import ast

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Event, Participant, Currency
from django.core.exceptions import ValidationError


class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('email',)


class EventForm(forms.ModelForm):
    participants = forms.CharField(
        widget=forms.SelectMultiple(attrs={'id': 'id_participants'}),
    )
    name = forms.CharField(
        widget=forms.TextInput(),
    )
    currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(),
        widget=forms.Select(),
    )

    class Meta:
        model = Event
        fields = ('name', 'currency', 'participants',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.session_key = kwargs.pop('session_key', None)
        super(EventForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        event = super().save(commit=False)

        if commit:
            event.save()

        raw_participants = ast.literal_eval(self.cleaned_data.get('participants'))

        creator = self.user if (self.user and self.user.is_authenticated) else None

        for raw_participant_name in raw_participants:
            new_participant, _ = Participant.objects.get_or_create(
                name=raw_participant_name,
                creator=creator
            )
            event.participants.add(new_participant)

        return event

    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        name = cleaned_data.get('name')

        if self.user and self.user.is_authenticated:
            queryset = Event.objects.filter(name=name, owner=self.user)
        else:
            queryset = Event.objects.filter(name=name, session_id=self.session_key, owner=None)

        if queryset.exists():
            raise ValidationError({'name': 'Event with this name already exists'})

        return cleaned_data
