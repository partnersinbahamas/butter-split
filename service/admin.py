from django.contrib import admin

from .models import Currency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')
    search_fields = ('code', 'name')
    list_filter = ('name', 'code')

    class Meta:
        model = Currency
