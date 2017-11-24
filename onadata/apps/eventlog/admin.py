from django.contrib import admin
from .models import FieldSightLog, CeleryTaskProgress

admin.site.register(FieldSightLog)
admin.site.register(CeleryTaskProgress)