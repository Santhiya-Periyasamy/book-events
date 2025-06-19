from django.contrib import admin
from .models import *

admin.site.register(Event)

admin.site.register(Booking)

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('event', 'show_time', 'total_seats', 'price')
    fields = ('event', 'show_time', 'total_seats', 'price', 'booked_seats')

    def formfield_for_dbfield(self, db_field, **kwargs):
        from django import forms
        if db_field.name == 'booked_seats':
            return forms.JSONField(required=False, initial=list)
        return super().formfield_for_dbfield(db_field, **kwargs)
    
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'image')