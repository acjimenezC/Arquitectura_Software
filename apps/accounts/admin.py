from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre']


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'rol', 'activo', 'ultimo_acceso']
    list_filter = ['rol', 'activo', 'fecha_registro']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['fecha_registro', 'ultimo_acceso']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'telefono', 'cedula', 'genero', 'fecha_nacimiento', 'foto_perfil')
        }),
        ('Estado', {
            'fields': ('activo', 'verificado', 'fecha_registro', 'ultimo_acceso')
        }),
    )
