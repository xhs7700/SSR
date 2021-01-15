from django.contrib import admin

from users.models import User, ConfirmString, Place, Device

admin.site.register(User)
admin.site.register(ConfirmString)
admin.site.register(Place)
admin.site.register(Device)