from django.shortcuts import get_object_or_404, render
from .models import Room


def room_list(request):
    rooms = Room.objects.filter(is_available=True)

    return render(request, 'rooms/room_list.html', {
        'rooms': rooms,
    })


def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    return render(request, 'rooms/room_detail.html', {
        'room': room,
    })