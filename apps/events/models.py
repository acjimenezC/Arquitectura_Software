from django.db import models
from apps.accounts.models import Usuario


class Evento(models.Model):
    """Modelo para eventos"""
    nombre = models.CharField(max_length=200)
    lugar = models.CharField(max_length=255)
    fecha = models.DateField()
    hora = models.TimeField()
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    descripcion = models.TextField(blank=True)
    organizador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='eventos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    capacidad = models.PositiveIntegerField(default=100)  # Capacidad máxima del evento
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    
    def tickets_vendidos(self):
        return self.tickets.filter(activo=True).count()
    
    def tickets_disponibles(self):
        return self.capacidad - self.tickets_vendidos()
