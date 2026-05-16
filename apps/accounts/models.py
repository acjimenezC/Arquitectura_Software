from django.db import models
from django.contrib.auth.models import AbstractUser


class Rol(models.Model):
    """Modelo para definir roles del sistema"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    permisos = models.JSONField(default=dict, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    ######### feedback
    def tiene_permiso(self, permiso):
        """Verifica si el rol tiene un permiso específico"""
        return self.permisos.get(permiso, False)
    
    def agregar_permiso(self, permiso):
        """Agrega un permiso al rol"""
        self.permisos[permiso] = True
        self.save(update_fields=['permisos'])
    ######### feedbacks
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    """Modelo personalizado de usuario"""
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    telefono = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    cedula = models.CharField(max_length=20, unique=True, blank=True, null=True)
    genero = models.CharField(
        max_length=10,
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        blank=True
    )
    activo = models.BooleanField(default=True)
    verificado = models.BooleanField(default=False)
    foto_perfil = models.ImageField(upload_to='perfil/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def es_admin(self):
        return self.is_superuser or (self.rol and self.rol.nombre == 'admin')
    
    def es_organizador(self):
        return self.is_superuser or (self.rol and self.rol.nombre == 'organizador')
    
    def es_usuario(self):
        return self.rol and self.rol.nombre == 'usuario'
