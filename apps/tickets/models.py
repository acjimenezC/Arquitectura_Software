from django.db import models
from apps.accounts.models import Usuario
from apps.events.models import Evento

######### feedback
class Reserva(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='reservas')
    cantidad = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_reserva']
 
    def __str__(self):
        return f"{self.usuario.username} - {self.evento.nombre} ({self.estado})"
######### feedback

class Ticket(models.Model):
    """Modelo para tickets/reservas"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tickets')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='tickets')
    cantidad = models.PositiveIntegerField(default=1)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='tickets')######### feedback

    
    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-fecha_compra']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.evento.nombre} - {self.cantidad} ticket(s)"