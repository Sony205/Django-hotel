from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from rooms.models import Room
from .forms import BookingForm
from .models import Booking


@login_required
def create_booking(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_available=True)

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            booking_date = form.cleaned_data['booking_date']
            expiration_date = form.cleaned_data['expiration_date']

            has_conflict = Booking.objects.filter(
                room=room,
                booking_date__lt=expiration_date,
                expiration_date__gt=booking_date,
            ).exclude(status='dead').exists()

            if has_conflict:
                form.add_error(None, 'Номер уже забронирован на выбранные даты.')
            else:
                booking = form.save(commit=False)
                booking.client = request.user
                booking.room = room
                booking.status = 'sleeping'
                booking.save()

                messages.success(request, 'Бронирование успешно создано.')
                return redirect('my_bookings')
    else:
        form = BookingForm()

    return render(request, 'booking/create_booking.html', {
        'form': form,
        'room': room,
    })


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(
        client=request.user
    ).select_related('room').order_by('-created_at')

    return render(request, 'booking/my_bookings.html', {
        'bookings': bookings,
    })


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        client=request.user
    )

    if request.method == 'POST':
        booking.status = 'dead'
        booking.save()

        messages.success(request, 'Бронирование отменено.')
        return redirect('my_bookings')

    return render(request, 'booking/cancel_booking.html', {
        'booking': booking,
    })


def is_manager(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_manager)
def booking_list(request):
    bookings = Booking.objects.select_related(
        'client',
        'room'
    ).order_by('-created_at')

    return render(request, 'booking/booking_list.html', {
        'bookings': bookings,
    })


@user_passes_test(is_manager)
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        booking.status = 'active'
        booking.save()

        messages.success(request, 'Бронирование подтверждено.')

    return redirect('booking_list')


@user_passes_test(is_manager)
def complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        booking.status = 'dead'
        booking.save()

        messages.success(request, 'Бронирование завершено.')

    return redirect('booking_list')


@login_required
def update_completed_bookings(request):
    Booking.objects.filter(
        expiration_date__lt=timezone.now().date()
    ).exclude(status='dead').update(status='dead')

    return redirect('my_bookings')