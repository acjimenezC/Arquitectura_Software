# Generated migration: Add ticket fields with unique handling

from django.db import migrations, models
import uuid


def generate_unique_ticket_codes(apps, schema_editor):
    """
    Generar un UUID único para cada ticket existente.
    Esto es necesario antes de congelar el campo como UNIQUE.
    """
    Ticket = apps.get_model('tickets', 'Ticket')
    for ticket in Ticket.objects.all():
        ticket.codigo_unico = uuid.uuid4()
        ticket.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_alter_ticket_id'),
    ]

    operations = [
        # Paso 1: Agregar el campo codigo_unico SIN restricción UNIQUE
        migrations.AddField(
            model_name='ticket',
            name='codigo_unico',
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                help_text='Código único del ticket (para validación QR o acceso)',
                # NO agregamos unique=True aquí
            ),
        ),
        
        # Paso 2: Agregar otros campos necesarios
        migrations.AddField(
            model_name='ticket',
            name='fecha_validacion',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text='Fecha y hora de validación de entrada'
            ),
        ),
        
        migrations.AddField(
            model_name='ticket',
            name='cantidad',
            field=models.PositiveIntegerField(
                default=1,
                help_text='Cantidad de tickets en esta reserva'
            ),
        ),
        
        migrations.AddField(
            model_name='ticket',
            name='notas',
            field=models.TextField(
                blank=True,
                help_text='Notas adicionales sobre el ticket'
            ),
        ),
        
        migrations.AddField(
            model_name='ticket',
            name='validado',
            field=models.BooleanField(
                default=False,
                help_text='Indica si el ticket ha sido validado/utilizado'
            ),
        ),
        
        migrations.AddField(
            model_name='ticket',
            name='activo',
            field=models.BooleanField(
                default=True,
                help_text='Indica si el ticket está vigente'
            ),
        ),
        
        # Paso 3: Ejecutar función para generar UUIDs únicos ANTES de agregar restricción
        migrations.RunPython(generate_unique_ticket_codes),
        
        # Paso 4: Ahora sí agregar la restricción UNIQUE
        migrations.AlterField(
            model_name='ticket',
            name='codigo_unico',
            field=models.UUIDField(
                default=uuid.uuid4,
                editable=False,
                help_text='Código único del ticket (para validación QR o acceso)',
                unique=True  # Ahora SÍ con UNIQUE
            ),
        ),
        
        # Paso 5: Agregar restricción compuesta usuario+evento
        migrations.AddConstraint(
            model_name='ticket',
            constraint=models.UniqueConstraint(
                fields=['usuario', 'evento'],
                name='un_ticket_por_usuario_evento'
            ),
        ),
        
        # Paso 6: Agregar índices para mejorar performance
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(
                fields=['codigo_unico'],
                name='tickets_codigo_unico_idx'
            ),
        ),
        
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(
                fields=['evento', 'activo'],
                name='tickets_evento_activo_idx'
            ),
        ),
        
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(
                fields=['usuario', 'activo'],
                name='tickets_usuario_activo_idx'
            ),
        ),
        
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(
                fields=['validado', 'activo'],
                name='tickets_validado_activo_idx'
            ),
        ),
    ]
