from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from apps.events.models import Evento
from apps.accounts.models import Usuario
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Crea múltiples eventos de ejemplo en la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=20,
            help='Cantidad de eventos a crear (default: 20)'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        
        # Obtener un organizador (usuario con rol organizador)
        organizador = Usuario.objects.filter(rol__nombre='organizador').first()
        
        if not organizador:
            # Si no hay organizador, intentar crear uno
            rol_organizador = Usuario.objects.filter(rol__nombre='organizador').first()
            if not rol_organizador:
                self.stdout.write(self.style.ERROR('❌ No hay usuarios con rol "organizador" en la base de datos'))
                return
        
        # Datos para generar eventos variados
        nombres = [
            'Conferencia de Tecnología 2026',
            'Festival de Música Electrónica',
            'Seminario de Marketing Digital',
            'Concierto de Jazz en Vivo',
            'Taller de Programación Python',
            'Gala Empresarial Anual',
            'Summit de Emprendimiento',
            'Exposición de Arte Contemporáneo',
            'Torneo de Ajedrez Internacional',
            'Foro de Sostenibilidad Empresarial',
            'Workshop de Diseño UX/UI',
            'Competencia de Startups',
            'Charla de Liderazgo Empresarial',
            'Festival de Cine Independiente',
            'Jornada de Transformación Digital',
            'Congreso de Inteligencia Artificial',
            'Evento de Networking Profesional',
            'Masterclass de Oratoria',
            'Conferencia de Ciberseguridad',
            'Festival Gastronómico Internacional',
            'Simposio de Investigación Científica',
            'Evento de Lanzamiento de Producto',
            'Taller de Emprendimiento Social',
            'Conferencia de Fintech',
            'Festival de Danza Contemporánea',
        ]

        lugares = [
            'Madrid, España',
            'Barcelona, España',
            'Valencia, España',
            'Bogotá, Colombia',
            'Santiago, Chile',
            'México City, México',
            'Buenos Aires, Argentina',
            'São Paulo, Brasil',
            'Lima, Perú',
            'Cartagena, Colombia',
        ]

        descripciones = [
            'Un evento excepcional que reúne a los mejores profesionales del sector.',
            'Experencia única de networking y aprendizaje con expertos internacionales.',
            'Oportunidad imperdible para conectar con líderes de la industria.',
            'Jornada dedicada a explorar las tendencias más innovadoras del momento.',
            'Espacio de intercambio de conocimientos y experiencias profesionales.',
            'Evento enfocado en el desarrollo personal y profesional de los asistentes.',
            'Plataforma para descubrir nuevas oportunidades de negocio y colaboración.',
            'Encuentro de mentes brillantes para compartir visiones y proyectos.',
        ]

        eventos_creados = 0
        
        for i in range(cantidad):
            try:
                # Generar datos aleatorios
                nombre = f"{random.choice(nombres)} #{i + 1}"
                lugar = random.choice(lugares)
                
                # Fecha aleatoria entre 7 días y 6 meses en el futuro
                dias_adelante = random.randint(7, 180)
                fecha = timezone.now().date() + timedelta(days=dias_adelante)
                
                # Hora aleatoria entre 8:00 AM y 8:00 PM
                hora = timezone.datetime.strptime(
                    f"{random.randint(8, 20)}:{random.choice(['00', '30'])}", 
                    "%H:%M"
                ).time()
                
                # Precio aleatorio entre $50 y $500
                precio = Decimal(random.randint(50, 500))
                
                # Descripción aleatoria
                descripcion = random.choice(descripciones)
                
                # Capacidad aleatoria entre 50 y 500 personas
                capacidad = random.randint(50, 500)
                
                # Crear el evento
                evento = Evento.objects.create(
                    nombre=nombre,
                    lugar=lugar,
                    fecha=fecha,
                    hora=hora,
                    precio=precio,
                    descripcion=descripcion,
                    organizador=organizador,
                    activo=True,
                    capacidad=capacidad
                )
                
                eventos_creados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Evento {eventos_creados}/{cantidad}: "{evento.nombre}" - {evento.fecha} - ${evento.precio}'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creando evento {i + 1}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Se crearon exitosamente {eventos_creados} eventos de {cantidad}'
            )
        )
