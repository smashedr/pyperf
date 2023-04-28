from django.contrib import admin
from .models import SpeedTest, Webhooks

admin.site.register(SpeedTest)
admin.site.register(Webhooks)
