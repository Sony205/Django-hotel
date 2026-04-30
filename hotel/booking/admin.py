from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'client',
        'room',
        'booking_date',
        'expiration_date',
        'status',
        'created_at',
    )
    list_filter = ('status', 'booking_date')
    search_fields = ('client__username', 'client__email', 'room__room_number')
    list_editable = ('status',)
    ordering = ('-created_at',)
