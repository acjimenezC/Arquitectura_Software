"""
Servicios de Tickets - Lógica de negocio compleja.

Separación de responsabilidades:
- models.py: Definición de estructura y métodos de entidad
- views.py: Lógica de presentación y HTTP
- services.py: Lógica de negocio y casos de uso
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum, Count, F, Case, When
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Ticket
from apps.events.models import Evento
from apps.accounts.models import Usuario

logger = logging.getLogger(__name__)


class TicketService:
    """
    Servicio para gestionar la lógica de negocio de tickets.
    Maneja compras, validaciones, cancelaciones y reportes.
    """
    
    @staticmethod
    def crear_reserva(usuario, evento, cantidad):
        """
        Crea una reserva de tickets con validaciones transaccionales.
        
        Args:
            usuario: Instancia de Usuario
            evento: Instancia de Evento
            cantidad: Cantidad de tickets
        
        Returns:
            dict: {'exito': bool, 'ticket': Ticket, 'mensaje': str, 'codigo': str}
        
        Raises:
            ValidationError: Si hay problemas en la validación
        """
        try:
            with transaction.atomic():
                # Verificar disponibilidad
                disponibles = Ticket.get_disponibles_evento(evento)
                
                if cantidad <= 0:
                    return {
                        'exito': False,
                        'ticket': None,
                        'mensaje': 'La cantidad debe ser mayor a cero.',
                        'codigo': 'CANTIDAD_INVALIDA'
                    }
                
                if cantidad > disponibles:
                    return {
                        'exito': False,
                        'ticket': None,
                        'mensaje': f'Tickets insuficientes. Disponibles: {disponibles}',
                        'codigo': 'STOCK_INSUFICIENTE'
                    }
                
                # Crear ticket
                ticket = Ticket.objects.create(
                    usuario=usuario,
                    evento=evento,
                    cantidad=cantidad
                )
                
                logger.info(f"Reserva creada: {ticket}")
                
                return {
                    'exito': True,
                    'ticket': ticket,
                    'mensaje': f'Reserva confirmada. Código: {ticket.codigo_unico}',
                    'codigo': 'RESERVA_EXITOSA'
                }
        
        except Exception as e:
            logger.error(f"Error al crear reserva: {str(e)}")
            return {
                'exito': False,
                'ticket': None,
                'mensaje': f'Error al procesar la reserva: {str(e)}',
                'codigo': 'ERROR_RESERVA'
            }
    
    @staticmethod
    def cancelar_reserva(ticket, razon=""):
        """
        Cancela una reserva y libera los tickets.
        
        Args:
            ticket: Instancia de Ticket
            razon: Razón de cancelación
        
        Returns:
            dict: {'exito': bool, 'mensaje': str}
        """
        try:
            with transaction.atomic():
                if not ticket.activo:
                    return {
                        'exito': False,
                        'mensaje': 'El ticket ya está cancelado.'
                    }
                
                if ticket.validado:
                    return {
                        'exito': False,
                        'mensaje': 'No se puede cancelar un ticket ya validado.'
                    }
                
                ticket.cancelar()
                if razon:
                    ticket.notas = f"{ticket.notas}\nRazón: {razon}"
                    ticket.save()
                
                logger.info(f"Ticket cancelado: {ticket} | Razón: {razon}")
                
                return {
                    'exito': True,
                    'mensaje': 'Reserva cancelada exitosamente.'
                }
        
        except Exception as e:
            logger.error(f"Error al cancelar: {str(e)}")
            return {
                'exito': False,
                'mensaje': f'Error: {str(e)}'
            }
    
    @staticmethod
    def obtener_disponibilidad_evento(evento):
        """
        Obtiene información completa de disponibilidad de un evento.
        
        Args:
            evento: Instancia de Evento
        
        Returns:
            dict: Información de capacidad y disponibilidad
        """
        tickets_vendidos = Ticket.objects.filter(
            evento=evento,
            activo=True
        ).aggregate(
            total=Sum('cantidad', default=0)
        )['total']
        
        disponibles = max(0, evento.capacidad - tickets_vendidos)
        porcentaje_ocupacion = (tickets_vendidos / evento.capacidad * 100) if evento.capacidad > 0 else 0
        
        return {
            'evento': evento.nombre,
            'capacidad_total': evento.capacidad,
            'tickets_vendidos': tickets_vendidos,
            'tickets_disponibles': disponibles,
            'porcentaje_ocupacion': round(porcentaje_ocupacion, 2),
            'evento_completo': disponibles == 0,
            'casi_completo': disponibles > 0 and porcentaje_ocupacion >= 80,
        }
    
    @staticmethod
    def obtener_estadisticas_usuario(usuario):
        """
        Obtiene estadísticas de tickets del usuario.
        
        Args:
            usuario: Instancia de Usuario
        
        Returns:
            dict: Estadísticas de compras, asistencia, etc.
        """
        tickets = Ticket.objects.filter(usuario=usuario)
        
        # TICKETS COMPRADOS (suma cantidad)
        total_comprados_result = tickets.filter(activo=True).aggregate(
            total=Sum('cantidad', default=0)
        )['total']
        total_comprados = total_comprados_result if total_comprados_result is not None else 0
        
        # TICKETS VALIDADOS (suma cantidad)
        total_validados_result = tickets.filter(validado=True).aggregate(
            total=Sum('cantidad', default=0)
        )['total']
        total_validados = total_validados_result if total_validados_result is not None else 0
        
        # TICKETS CANCELADOS (suma cantidad)
        total_cancelados_result = tickets.filter(activo=False).aggregate(
            total=Sum('cantidad', default=0)
        )['total']
        total_cancelados = total_cancelados_result if total_cancelados_result is not None else 0
        
        # GASTO TOTAL
        total_gastado = tickets.filter(
            activo=True
        ).annotate(
            total=F('cantidad') * F('evento__precio')
        ).aggregate(
            suma=Sum('total', default=0)
        )['suma'] or 0
        
        # EVENTOS PRÓXIMOS (suma cantidad)
        eventos_proximos_result = Ticket.objects.filter(
            usuario=usuario,
            activo=True,
            validado=False,
            evento__fecha__gte=timezone.now().date()
        ).aggregate(total=Sum('cantidad', default=0))['total']
        eventos_proximos = eventos_proximos_result if eventos_proximos_result is not None else 0
        
        return {
            'usuario': usuario.username,
            'total_tickets_comprados': total_comprados,
            'total_tickets_validados': total_validados,
            'total_tickets_cancelados': total_cancelados,
            'total_gastado': float(total_gastado),
            'eventos_proximos': eventos_proximos,
            'tasa_validacion': round((total_validados / total_comprados * 100), 2) if total_comprados > 0 else 0,
        }
    
    @staticmethod
    def obtener_estadisticas_evento(evento):
        """
        Obtiene estadísticas completas de un evento.
        
        Args:
            evento: Instancia de Evento
        
        Returns:
            dict: Estadísticas de ventas, validación, etc.
        """
        tickets = Ticket.objects.filter(evento=evento, activo=True)
        
        total_tickets = tickets.aggregate(
            suma=Sum('cantidad', default=0)
        )['suma'] or 0
        
        total_ingresos = tickets.annotate(
            total=F('cantidad') * F('evento__precio')
        ).aggregate(
            suma=Sum('total', default=0)
        )['suma'] or 0
        
        total_validados = tickets.filter(validado=True).aggregate(
            suma=Sum('cantidad', default=0)
        )['suma'] or 0
        
        num_compradores = tickets.values('usuario').distinct().count()
        
        # Ingresos esperados vs reales
        ingresos_esperados = evento.capacidad * evento.precio
        
        return {
            'evento': evento.nombre,
            'capacidad': evento.capacidad,
            'tickets_vendidos': total_tickets,
            'entradas_validadas': total_validados,
            'tasa_validacion': round((total_validados / total_tickets * 100), 2) if total_tickets > 0 else 0,
            'compradores_unicos': num_compradores,
            'ingresos_reales': float(total_ingresos),
            'ingresos_esperados': float(ingresos_esperados),
            'ocupacion_porcentaje': round((total_tickets / evento.capacidad * 100), 2) if evento.capacidad > 0 else 0,
        }
    
    @staticmethod
    def liberar_tickets_no_validados(dias=30):
        """
        Libera tickets que no fueron validados en un período.
        Útil para cancelar automáticamente tickets de eventos pasados.
        
        Args:
            dias: Días desde la compra para considerar como vencido
        
        Returns:
            dict: Información sobre tickets liberados
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        
        # Buscar eventos pasados
        tickets_vencidos = Ticket.objects.filter(
            evento__fecha__lt=timezone.now().date(),
            validado=False,
            activo=True,
            fecha_compra__lt=fecha_limite
        )
        
        cantidad_liberados = 0
        try:
            with transaction.atomic():
                for ticket in tickets_vencidos:
                    ticket.cancelar()
                    cantidad_liberados += 1
                
                logger.info(f"Liberados {cantidad_liberados} tickets no validados")
        
        except Exception as e:
            logger.error(f"Error al liberar tickets: {str(e)}")
        
        return {
            'tickets_liberados': cantidad_liberados,
            'fecha_limite': fecha_limite,
            'mensaje': f'{cantidad_liberados} tickets liberados automáticamente'
        }
    
    @staticmethod
    def generar_reporte_diario():
        """
        Genera reporte diario de tickets vendidos y validados.
        
        Returns:
            dict: Información del reporte
        """
        hoy = timezone.now().date()
        
        tickets_hoy = Ticket.objects.filter(
            fecha_compra__date=hoy,
            activo=True
        )
        
        total_tickets = tickets_hoy.aggregate(
            suma=Sum('cantidad', default=0)
        )['suma'] or 0
        
        total_ingresos = tickets_hoy.annotate(
            total=F('cantidad') * F('evento__precio')
        ).aggregate(
            suma=Sum('total', default=0)
        )['suma'] or 0
        
        total_validados = tickets_hoy.filter(validado=True).aggregate(
            suma=Sum('cantidad', default=0)
        )['suma'] or 0
        
        eventos_concurridos = tickets_hoy.values('evento').count()
        
        return {
            'fecha': hoy.isoformat(),
            'total_tickets_vendidos': total_tickets,
            'total_ingresos': float(total_ingresos),
            'tickets_validados': total_validados,
            'eventos_concurridos': eventos_concurridos,
            'promedio_por_evento': round(total_tickets / eventos_concurridos, 2) if eventos_concurridos > 0 else 0,
        }
    
    @staticmethod
    def validar_lote_qr(codigos_qr):
        """
        Valida múltiples códigos QR (batch validation).
        Útil para procesamiento en torniquetes.
        
        Args:
            codigos_qr: Lista de códigos UUID o QR
        
        Returns:
            dict: Resultados de validación
        """
        resultados = {
            'exitosos': [],
            'fallos': [],
            'duplicados': [],
            'total_procesados': len(codigos_qr)
        }
        
        codigos_procesados = set()
        
        for codigo in codigos_qr:
            # Detectar duplicados en el lote
            if codigo in codigos_procesados:
                resultados['duplicados'].append(codigo)
                continue
            
            codigos_procesados.add(codigo)
            resultado = Ticket.validar_por_codigo(codigo)
            
            if resultado['valido']:
                resultados['exitosos'].append(resultado)
            else:
                resultados['fallos'].append(resultado)
        
        resultados['resumen'] = {
            'exitosos': len(resultados['exitosos']),
            'fallos': len(resultados['fallos']),
            'duplicados': len(resultados['duplicados']),
        }
        
        return resultados


class EstadisticasTicketService:
    """
    Servicio especializado en análisis y reportería de tickets.
    """
    
    @staticmethod
    def tickets_proximos_a_vencer(dias=7):
        """
        Obtiene tickets de eventos próximos a vencer.
        """
        hoy = timezone.now().date()
        fecha_limite = hoy + timedelta(days=dias)
        
        return Ticket.objects.filter(
            evento__fecha__gte=hoy,
            evento__fecha__lte=fecha_limite,
            activo=True,
            validado=False
        ).select_related('usuario', 'evento').order_by('evento__fecha')
    
    @staticmethod
    def eventos_sin_reservas():
        """
        Obtiene eventos que no tienen reservas activas.
        """
        eventos_con_reservas = Ticket.objects.filter(
            activo=True
        ).values('evento').distinct()
        
        return Evento.objects.filter(
            activo=True
        ).exclude(
            id__in=eventos_con_reservas
        ).order_by('fecha')
