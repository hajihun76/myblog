from django.contrib import admin
from .models import BusQueryLog

@admin.register(BusQueryLog)
class BusQueryLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'bus_number', 'queried_at']
    list_filter = ['date', 'bus_number']
    search_fields = ['user__email', 'bus_number']
    ordering = ['-queried_at']
