from django.contrib import admin
from .models import Conference

@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'location')
    search_fields = ('title', 'description')
    list_filter = ('start_date', 'location')