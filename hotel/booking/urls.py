from django.urls import path
from . import views

urlpatterns = [
    path('room/<int:room_id>/create/', views.create_booking, name='create_booking'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),

    path('manager/', views.booking_list, name='booking_list'),
    path('<int:booking_id>/confirm/', views.confirm_booking, name='confirm_booking'),
    path('<int:booking_id>/complete/', views.complete_booking, name='complete_booking'),

    path('update-completed/', views.update_completed_bookings, name='update_completed_bookings'),
]
