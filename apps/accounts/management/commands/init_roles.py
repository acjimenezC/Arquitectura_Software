from django.core.management.base import BaseCommand
from apps.accounts.models import Rol


class Command(BaseCommand):
    help = 'Inicializa los roles del sistema'

    def handle(self, *args, **options):
        roles_data = [
            {
                'nombre': 'admin',
                'descripcion': 'Administrador del sistema con acceso total',
                'permisos': {'todos': True}
            },
            {
                'nombre': 'organizador',
                'descripcion': 'Organizador de eventos',
                'permisos': {'crear_eventos': True, 'gestionar_eventos': True}
            },
            {
                'nombre': 'usuario',
                'descripcion': 'Usuario final - asistente a eventos',
                'permisos': {'ver_eventos': True, 'comprar_tickets': True}
            },
        ]

        for rol_data in roles_data:
            rol, created = Rol.objects.get_or_create(
                nombre=rol_data['nombre'],
                defaults={
                    'descripcion': rol_data['descripcion'],
                    'permisos': rol_data['permisos'],
                    'activo': True
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Rol "{rol.nombre}" creado correctamente')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Rol "{rol.nombre}" ya existe')
                )

        self.stdout.write(self.style.SUCCESS('\n✓ Inicialización de roles completada'))
