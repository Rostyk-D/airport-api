from django.contrib import admin

from .models import Airplane, AirplaneType, Crew, Flight


admin.site.register(Airplane)
admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(Flight)
