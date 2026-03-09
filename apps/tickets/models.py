from django.db import models
from apps.accounts.models import Usuario
from apps.events.models import Evento


class Ticket(models.Model):
    """Modelo para tickets/reservas"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tickets')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='tickets')
    cantidad = models.PositiveIntegerField(default=1)
    fecha_compra = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-fecha_compra']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.evento.nombre} - {self.cantidad} ticket(s)"