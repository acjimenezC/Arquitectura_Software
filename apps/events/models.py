from django.db import models
from apps.accounts.models import Usuario
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum



class Evento(models.Model):
    """Modelo para eventos"""
    nombre = models.CharField(max_length=200)
    lugar = models.CharField(max_length=255)
    fecha = models.DateField()
    hora = models.TimeField()
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('Empresariales', 'Empresariales'),
            ('Conciertos', 'Conciertos'),
            ('Deportes', 'Deportes'),
            ('Festivales', 'Festivales'),
        ],
        default='Empresariales'
    )
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    descripcion = models.TextField(blank=True)
    organizador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='eventos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    capacidad = models.PositiveIntegerField(default=100)  # Capacidad máxima del evento
    
    
    ######### feedback
    def clean(self):
        if self.fecha < timezone.now().date():
            raise ValidationError('La fecha del evento debe ser futura')
  
    @property
    def tickets_vendidos(self):
        return self.reservas.filter(
            estado='confirmada'
        ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    @property
    def tickets_disponibles(self):
        return self.capacidad - self.tickets_vendidos
    ######### feedback

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre