from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum, F
from django.utils import timezone
import uuid
from apps.accounts.models import Usuario
from apps.events.models import Evento


class Ticket(models.Model):
    """
    Modelo para gestión de tickets/reservas.
    
    Incluye validación de disponibilidad, control de sobreventa,
    UUID para validación QR y métodos para gestión del ciclo de vida.
    """
    
    # Identificadores únicos
    id = models.AutoField(primary_key=True)
    codigo_unico = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Código único del ticket (para validación QR o acceso)"
    )
    
    # Relaciones
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='tickets',
        help_text="Usuario propietario del ticket"
    )
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='tickets',
        help_text="Evento para el cual se reservó el ticket"
    )
    
    # Información del ticket
    cantidad = models.PositiveIntegerField(
        default=1,
        help_text="Cantidad de tickets en esta reserva"
    )
    
    # Fechas
    fecha_compra = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de compra del ticket"
    )
    fecha_validacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora de validación de entrada"
    )
    
    # Estado
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el ticket está vigente"
    )
    validado = models.BooleanField(
        default=False,
        help_text="Indica si el ticket ha sido validado/utilizado"
    )
    
    # Metadata
    notas = models.TextField(
        blank=True,
        help_text="Notas adicionales sobre el ticket"
    )
    razon_cancelacion = models.TextField(
        blank=True,
        help_text="Razón proporcionada al cancelar el ticket"
    )
    fecha_cancelacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora de cancelación del ticket"
    )
    
    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-fecha_compra']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'evento'],
                name='un_ticket_por_usuario_evento'
            )
        ]
        indexes = [
            models.Index(fields=['codigo_unico']),
            models.Index(fields=['evento', 'activo']),
            models.Index(fields=['usuario', 'activo']),
            models.Index(fields=['validado', 'activo']),
        ]
    
    def __str__(self):
        estado = "Validado" if self.validado else "Activo" if self.activo else "Cancelado"
        return f"{self.usuario.username} - {self.evento.nombre} ({self.cantidad} ticket) - {estado}"
    
    def clean(self):
        """
        Validación de negocio antes de guardar.
        Verifica disponibilidad, evento válido y consistencia de datos.
        """
        # Verificar que el evento existe y está activo
        if not self.evento.activo:
            raise ValidationError("El evento no está disponible para reservas.")
        
        # Verificar que la cantidad sea positiva
        if self.cantidad <= 0:
            raise ValidationError("La cantidad de tickets debe ser mayor a cero.")
        
        # Verificar disponibilidad de tickets
        tickets_disponibles = self.get_tickets_disponibles_evento()
        if self.cantidad > tickets_disponibles:
            raise ValidationError(
                f"No hay suficientes tickets disponibles. "
                f"Disponibles: {tickets_disponibles}, Solicitados: {self.cantidad}"
            )
        
        # Si el ticket ya existe (edición), restar la cantidad anterior
        if self.pk:
            ticket_anterior = Ticket.objects.get(pk=self.pk)
            diferencia = self.cantidad - ticket_anterior.cantidad
            
            if diferencia > 0 and diferencia > tickets_disponibles:
                raise ValidationError(
                    f"No hay suficientes tickets para aumentar la cantidad. "
                    f"Disponibles: {tickets_disponibles}, Diferencia: {diferencia}"
                )
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe save() para ejecutar validaciones antes de guardar.
        """
        self.full_clean()  # Ejecuta clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_disponibles_evento(cls, evento=None, excluir_ticket_id=None):
        """
        Calcula la cantidad de tickets disponibles para un evento.
        
        Args:
            evento: Instancia de Evento. Si no se proporciona, se usa self.evento
            excluir_ticket_id: ID del ticket a excluir del cálculo (para ediciones)
        
        Returns:
            int: Cantidad de tickets disponibles
        """
        if evento is None:
            return 0
        
        # Contar tickets activos vendidos
        tickets_vendidos = cls.objects.filter(
            evento=evento,
            activo=True
        ).exclude(pk=excluir_ticket_id).aggregate(
            total=Sum('cantidad', default=0)
        )['total']
        
        # Calcular disponibles
        disponibles = max(0, evento.capacidad - tickets_vendidos)
        return disponibles
    
    def get_tickets_disponibles_evento(self):
        """
        Instancia del método de clase para obtener disponibilidad.
        """
        return self.__class__.get_disponibles_evento(
            evento=self.evento,
            excluir_ticket_id=self.pk
        )
    
    def cancelar(self, razon=""):
        """
        Cancela el ticket desactivándolo sin eliminarlo.
        Permite auditoría y reversos.
        
        Args:
            razon: Razón por la cual se cancela el ticket
            
        Returns:
            bool: True si se cancela exitosamente
            
        Raises:
            ValidationError: Si el ticket no puede ser cancelado
        """
        if not self.activo:
            raise ValidationError("El ticket ya está cancelado.")
        
        if self.validado:
            raise ValidationError("No puedes cancelar un ticket que ya ha sido validado.")
        
        self.activo = False
        self.razon_cancelacion = razon
        self.fecha_cancelacion = timezone.now()
        self.notas = f"{self.notas}\n[CANCELADO {self.fecha_cancelacion.strftime('%Y-%m-%d %H:%M')}]" if self.notas else f"[CANCELADO {self.fecha_cancelacion.strftime('%Y-%m-%d %H:%M')}]"
        self.save()
        
        return True
    
    def contar_cancelaciones_evento(self):
        """
        Cuenta cuántas veces el usuario ha cancelado tickets del mismo evento.
        
        Returns:
            int: Número total de tickets cancelados
        """
        from django.db.models import Sum
        total_cancelado = Ticket.objects.filter(
            usuario=self.usuario,
            evento=self.evento,
            activo=False,
            fecha_cancelacion__isnull=False
        ).aggregate(total=Sum('cantidad', default=0))['total']
        return total_cancelado if total_cancelado is not None else 0
    
    def validar_entrada(self):
        """
        Valida la entrada del ticket (marca como utilizado).
        Se usa en torniquetes, QR scanners, etc.
        
        Returns:
            dict: Resultado de la validación
        """
        if not self.activo:
            return {
                'valido': False,
                'mensaje': 'El ticket ha sido cancelado.',
                'codigo': 'TICKET_CANCELADO'
            }
        
        if self.validado:
            return {
                'valido': False,
                'mensaje': 'El ticket ya ha sido validado.',
                'codigo': 'TICKET_YA_VALIDADO',
                'fecha_validacion': self.fecha_validacion.isoformat() if self.fecha_validacion else None
            }
        
        # Marcar como validado
        self.validado = True
        self.fecha_validacion = timezone.now()
        self.save()
        
        return {
            'valido': True,
            'mensaje': f'Ticket validado correctamente para {self.evento.nombre}',
            'codigo': 'TICKET_VALIDO',
            'usuario': self.usuario.get_full_name() or self.usuario.username,
            'evento': self.evento.nombre,
            'cantidad': self.cantidad,
            'codigo_ticket': str(self.codigo_unico),
            'fecha_validacion': self.fecha_validacion.isoformat()
        }
    
    def obtener_codigo_qr(self):
        """
        Retorna información formateada para código QR.
        Formato: UUID|Usuario|Evento|Cantidad
        """
        return f"{self.codigo_unico}|{self.usuario.id}|{self.evento.id}|{self.cantidad}"
    
    @classmethod
    def validar_por_codigo(cls, codigo_qr):
        """
        Valida un ticket usando su código QR.
        
        Args:
            codigo_qr: UUID del ticket o string del formato QR
        
        Returns:
            dict: Resultado de la validación
        """
        try:
            # Intentar buscar por UUID directo
            try:
                uuid_obj = uuid.UUID(codigo_qr)
            except ValueError:
                # Si no es UUID válido, intentar extraer del formato QR
                uuid_obj = uuid.UUID(codigo_qr.split('|')[0])
            
            ticket = cls.objects.get(codigo_unico=uuid_obj)
            return ticket.validar_entrada()
        
        except cls.DoesNotExist:
            return {
                'valido': False,
                'mensaje': 'El código de ticket no existe.',
                'codigo': 'TICKET_NO_EXISTE'
            }
        
        except (ValueError, IndexError):
            return {
                'valido': False,
                'mensaje': 'Formato de código inválido.',
                'codigo': 'FORMATO_INVALIDO'
            }
    
    def puede_canjearse(self):
        """
        Verifica si el ticket puede canjearse (validarse).
        
        Returns:
            bool: True si puede validarse
        """
        return self.activo and not self.validado
    
    def get_estado_display_custom(self):
        """
        Retorna el estado del ticket en formato legible.
        """
        if self.validado:
            return "Validado/Utilizado"
        elif self.activo:
            return "Activo/Disponible"
        else:
            return "Cancelado"
    
    def get_dias_desde_compra(self):
        """
        Calcula cantidad de días desde la compra.
        """
        return (timezone.now() - self.fecha_compra).days
    
    def get_total_precio(self):
        """
        Calcula el precio total de esta reserva.
        """
        return self.cantidad * self.evento.precio
    
    def es_proxima_a_vencer(self, dias=7):
        """
        Verifica si el evento está próximo a ocurrir.
        """
        dias_para_evento = (self.evento.fecha - timezone.now().date()).days
        return 0 < dias_para_evento <= dias