from django.contrib import admin
from .models import FieldSightLog
from .models import CeleryTaskProgress

admin.site.register(FieldSightLog)
admin.site.register(CeleryTaskProgress)