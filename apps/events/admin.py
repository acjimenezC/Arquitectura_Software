from django.contrib import admin
from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'lugar', 'fecha', 'hora', 'organizador', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion', 'fecha']
    search_fields = ['nombre', 'lugar', 'organizador__username']
    readonly_fields = ['fecha_creacion']
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'lugar', 'descripcion')
        }),
        ('Fecha y Hora', {
            'fields': ('fecha', 'hora')
        }),
        ('Organizador', {
            'fields': ('organizador',)
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion')
        }),
    )
