from django.urls import path
from . import views

urlpatterns = [
    path('room/<int:room_id>/create/', views.create_booking, name='create_booking'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
]