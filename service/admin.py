from django.contrib import admin

from .models import Currency, Event, Participant


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')
    search_fields = ('code', 'name')
    list_filter = ('name', 'code')

    class Meta:
        model = Currency


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    list_filter = ('name', )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'currency', 'participants_count', 'created_at')
    ordering = ('participants', 'created_at')
    search_fields = ('name', )
    list_filter = ('owner', 'currency')

    def participants_count(self, obj):
        return obj.participants.count()

    participants_count.admin_order_field = 'participants'
    participants_count.short_description = 'Number of participants'
