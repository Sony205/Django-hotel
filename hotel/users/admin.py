from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


admin.site.register(CustomUser, UserAdmin)

admin.site.unregister(Group)
