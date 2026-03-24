"""
Tests para el modelo Ticket y servicios.

Incluye tests de:
- Validación de disponibilidad
- Creación de reservas
- Cancelación de tickets
- Validación de entrada
- Generación de códigos QR
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, datetime

from apps.tickets.models import Ticket
from apps.tickets.services import TicketService, EstadisticasTicketService
from apps.accounts.models import Usuario, Rol
from apps.events.models import Evento


class TicketModelTestCase(TestCase):
    """Tests del modelo Ticket."""
    
    @classmethod
    def setUpTestData(cls):
        """Configuración inicial para todos los tests."""
        # Crear rol
        cls.rol = Rol.objects.create(nombre='usuario')
        
        # Crear usuario
        cls.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            verified=True,
            active=True,
            rol=cls.rol
        )
        
        # Crear evento
        cls.evento = Evento.objects.create(
            nombre='Test Event',
            lugar='Test Venue',
            fecha=timezone.now().date() + timedelta(days=30),
            hora=timezone.now().time(),
            precio=100.00,
            capacidad=100,
            organizador=cls.usuario
        )
    
    def test_crear_ticket_exitosamente(self):
        """Test: Crear un ticket válido."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        self.assertEqual(ticket.usuario, self.usuario)
        self.assertEqual(ticket.evento, self.evento)
        self.assertEqual(ticket.cantidad, 5)
        self.assertTrue(ticket.activo)
        self.assertFalse(ticket.validado)
    
    def test_codigo_unico_generado(self):
        """Test: Se genera UUID único automáticamente."""
        ticket1 = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=1
        )
        
        ticket2 = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=1
        )
        
        self.assertIsNotNone(ticket1.codigo_unico)
        self.assertIsNotNone(ticket2.codigo_unico)
        self.assertNotEqual(ticket1.codigo_unico, ticket2.codigo_unico)
    
    def test_evitar_sobreventa(self):
        """Test: No permitir sobreventa de tickets."""
        # Crear tickets hasta el límite
        for i in range(100):
            Ticket.objects.create(
                usuario=self.usuario,
                evento=self.evento,
                cantidad=1
            )
        
        # Intentar crear uno más debería fallar
        with self.assertRaises(ValidationError):
            ticket = Ticket(
                usuario=self.usuario,
                evento=self.evento,
                cantidad=1
            )
            ticket.full_clean()
    
    def test_cantidad_positiva_requerida(self):
        """Test: La cantidad debe ser positiva."""
        with self.assertRaises(ValidationError):
            ticket = Ticket(
                usuario=self.usuario,
                evento=self.evento,
                cantidad=0
            )
            ticket.full_clean()
    
    def test_obtener_disponibilidad(self):
        """Test: Calcular tickets disponibles correctamente."""
        # Evento tiene capacidad de 100
        disponibles_inicial = Ticket.get_disponibles_evento(self.evento)
        self.assertEqual(disponibles_inicial, 100)
        
        # Vender 30 tickets
        Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=30
        )
        
        disponibles = Ticket.get_disponibles_evento(self.evento)
        self.assertEqual(disponibles, 70)
    
    def test_cancelar_ticket(self):
        """Test: Cancelar un ticket exitosamente."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        ticket.cancelar()
        
        self.assertFalse(ticket.activo)
        self.assertTrue('[CANCELADO' in ticket.notas)
    
    def test_no_cancelar_ticket_ya_cancelado(self):
        """Test: No permitir cancelar un ticket ya cancelado."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        ticket.cancelar()
        
        with self.assertRaises(ValidationError):
            ticket.cancelar()
    
    def test_no_cancelar_ticket_validado(self):
        """Test: No permitir cancelar un ticket ya validado."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        ticket.validado = True
        ticket.save()
        
        with self.assertRaises(ValidationError):
            ticket.cancelar()
    
    def test_validar_entrada(self):
        """Test: Validar entrada de un ticket."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        resultado = ticket.validar_entrada()
        
        self.assertTrue(resultado['valido'])
        self.assertEqual(resultado['codigo'], 'TICKET_VALIDO')
        self.assertTrue(ticket.validado)
        self.assertIsNotNone(ticket.fecha_validacion)
    
    def test_no_validar_ticket_cancelado(self):
        """Test: No permitir validar un ticket cancelado."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        ticket.cancelar()
        resultado = ticket.validar_entrada()
        
        self.assertFalse(resultado['valido'])
        self.assertEqual(resultado['codigo'], 'TICKET_CANCELADO')
    
    def test_no_validar_ticket_dos_veces(self):
        """Test: No permitir validar un ticket ya validado."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        ticket.validar_entrada()
        resultado2 = ticket.validar_entrada()
        
        self.assertFalse(resultado2['valido'])
        self.assertEqual(resultado2['codigo'], 'TICKET_YA_VALIDADO')
    
    def test_codigo_qr_generado(self):
        """Test: Generar código QR correctamente."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        codigo_qr = ticket.obtener_codigo_qr()
        
        # Formato: UUID|usuario_id|evento_id|cantidad
        partes = codigo_qr.split('|')
        self.assertEqual(len(partes), 4)
        self.assertEqual(partes[1], str(self.usuario.id))
        self.assertEqual(partes[2], str(self.evento.id))
        self.assertEqual(partes[3], '5')
    
    def test_validar_por_codigo_qr(self):
        """Test: Validar ticket usando código QR."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        codigo = str(ticket.codigo_unico)
        resultado = Ticket.validar_por_codigo(codigo)
        
        self.assertTrue(resultado['valido'])
        self.assertEqual(resultado['codigo'], 'TICKET_VALIDO')
    
    def test_calcular_precio_total(self):
        """Test: Calcular precio total de una reserva."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        total = ticket.get_total_precio()
        self.assertEqual(total, 500.0)  # 5 * 100
    
    def test_dias_desde_compra(self):
        """Test: Calcular días desde la compra."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=1
        )
        
        dias = ticket.get_dias_desde_compra()
        self.assertEqual(dias, 0)  # Comprado hoy
    
    def test_es_proxima_a_vencer(self):
        """Test: Verificar si evento es próximo."""
        # Evento en 5 días
        evento_pronto = Evento.objects.create(
            nombre='Evento Próximo',
            lugar='Test Venue',
            fecha=timezone.now().date() + timedelta(days=5),
            hora=timezone.now().time(),
            precio=100.00,
            capacidad=100,
            organizador=self.usuario
        )
        
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=evento_pronto,
            cantidad=1
        )
        
        self.assertTrue(ticket.es_proxima_a_vencer(dias=7))
        self.assertFalse(ticket.es_proxima_a_vencer(dias=3))


class TicketServiceTestCase(TestCase):
    """Tests del servicio TicketService."""
    
    @classmethod
    def setUpTestData(cls):
        """Configuración inicial para todos los tests."""
        cls.rol = Rol.objects.create(nombre='usuario')
        cls.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            verified=True,
            active=True,
            rol=cls.rol
        )
        
        cls.evento = Evento.objects.create(
            nombre='Test Event',
            lugar='Test Venue',
            fecha=timezone.now().date() + timedelta(days=30),
            hora=timezone.now().time(),
            precio=100.00,
            capacidad=50,
            organizador=self.usuario
        )
    
    def test_crear_reserva_exitosa(self):
        """Test: Crear reserva mediante servicio."""
        resultado = TicketService.crear_reserva(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        self.assertTrue(resultado['exito'])
        self.assertIsNotNone(resultado['ticket'])
        self.assertEqual(resultado['codigo'], 'RESERVA_EXITOSA')
    
    def test_crear_reserva_sin_disponibilidad(self):
        """Test: No permitir crear reserva sin disponibilidad."""
        resultado = TicketService.crear_reserva(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=100  # Más que la capacidad
        )
        
        self.assertFalse(resultado['exito'])
        self.assertEqual(resultado['codigo'], 'STOCK_INSUFICIENTE')
    
    def test_cancelar_reserva(self):
        """Test: Cancelar reserva mediante servicio."""
        ticket = Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=10
        )
        
        resultado = TicketService.cancelar_reserva(ticket)
        
        self.assertTrue(resultado['exito'])
    
    def test_obtener_disponibilidad_evento(self):
        """Test: Obtener información de disponibilidad."""
        info = TicketService.obtener_disponibilidad_evento(self.evento)
        
        self.assertEqual(info['capacidad_total'], 50)
        self.assertEqual(info['tickets_disponibles'], 50)
        self.assertEqual(info['porcentaje_ocupacion'], 0)
    
    def test_obtener_estadisticas_usuario(self):
        """Test: Obtener estadísticas de usuario."""
        Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=5
        )
        
        stats = TicketService.obtener_estadisticas_usuario(self.usuario)
        
        self.assertEqual(stats['total_tickets_comprados'], 1)
        self.assertEqual(stats['total_gastado'], 500.0)
    
    def test_obtener_estadisticas_evento(self):
        """Test: Obtener estadísticas de evento."""
        Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento,
            cantidad=25
        )
        
        stats = TicketService.obtener_estadisticas_evento(self.evento)
        
        self.assertEqual(stats['tickets_vendidos'], 25)
        self.assertEqual(stats['compradores_unicos'], 1)
        self.assertAlmostEqual(stats['ocupacion_porcentaje'], 50.0, places=1)


class EstadisticasTicketServiceTestCase(TestCase):
    """Tests del servicio EstadisticasTicketService."""
    
    @classmethod
    def setUpTestData(cls):
        """Configuración inicial."""
        cls.rol = Rol.objects.create(nombre='usuario')
        cls.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            verified=True,
            active=True,
            rol=cls.rol
        )
        
        cls.evento_pronto = Evento.objects.create(
            nombre='Event Próximo',
            lugar='Venue',
            fecha=timezone.now().date() + timedelta(days=3),
            hora=timezone.now().time(),
            precio=100.00,
            capacidad=50,
            organizador=cls.usuario
        )
        
        cls.evento_sin_reservas = Evento.objects.create(
            nombre='Event Sin Reservas',
            lugar='Venue',
            fecha=timezone.now().date() + timedelta(days=30),
            hora=timezone.now().time(),
            precio=100.00,
            capacidad=50,
            organizador=cls.usuario
        )
    
    def test_tickets_proximos_a_vencer(self):
        """Test: Obtener tickets próximos a vencer."""
        Ticket.objects.create(
            usuario=self.usuario,
            evento=self.evento_pronto,
            cantidad=5
        )
        
        proximos = EstadisticasTicketService.tickets_proximos_a_vencer(dias=7)
        
        self.assertEqual(proximos.count(), 1)
    
    def test_eventos_sin_reservas(self):
        """Test: Obtener eventos sin reservas."""
        sin_reservas = EstadisticasTicketService.eventos_sin_reservas()
        
        self.assertIn(self.evento_sin_reservas, sin_reservas)
