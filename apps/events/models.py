from django.db import models
from apps.accounts.models import Usuario


class Evento(models.Model):
    """Modelo para eventos"""
    CATEGORIAS = [
        ('Empresariales', 'Empresariales'),
        ('Conciertos', 'Conciertos'),
        ('Deportes', 'Deportes'),
        ('Festivales', 'Festivales'),
    ]
    
    nombre = models.CharField(max_length=200)
    lugar = models.CharField(max_length=255)
    fecha = models.DateField()
    hora = models.TimeField()
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='eventos/', null=True, blank=True)
    organizador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='eventos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    capacidad = models.PositiveIntegerField(default=100)  # Capacidad máxima del evento
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='Empresariales')
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    
    def tickets_vendidos(self):
        from django.db.models import Sum
        total = self.tickets.filter(activo=True).aggregate(total=Sum('cantidad'))['total']
        return total if total is not None else 0
    
    def tickets_disponibles(self):
        return self.capacidad - self.tickets_vendidos()
    
    def porcentaje_capacidad_usada(self):
        """Retorna el porcentaje de capacidad utilizada (0-100)"""
        if self.capacidad == 0:
            return 0
        return int((self.tickets_vendidos() / self.capacidad) * 100)
    
    def porcentaje_capacidad_disponible(self):
        """Retorna el porcentaje de capacidad disponible (0-100)"""
        return 100 - self.porcentaje_capacidad_usada()
