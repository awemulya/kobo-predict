from django.contrib import admin
from .models import GeoLayer, GeoArea


class GeoAreaInline(admin.StackedInline):
    model = GeoArea
    extra = 0


@admin.register(GeoLayer)
class GeoLayerAdmin(admin.ModelAdmin):
    inlines = [GeoAreaInline]
