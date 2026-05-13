from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from rooms.models import Room
from .forms import BookingForm
from .models import Booking, Services


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
                booking.status = 'active'
                booking.save()
                form.save_m2m()

                messages.success(request, 'Бронирование успешно создано.')
                return redirect('my_bookings')
    else:
        form = BookingForm()

    services = Services.objects.all()
    return render(request, 'booking/create_booking.html', {
        'form': form,
        'room': room,
        'services': services,
    })


@login_required
def my_bookings(request):
    Booking.objects.filter(
        expiration_date__lt=timezone.now().date()
    ).exclude(status='dead').update(status='dead')

    bookings = Booking.objects.filter(
        client=request.user
    ).select_related('room').prefetch_related('servises').order_by('-created_at')
    
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