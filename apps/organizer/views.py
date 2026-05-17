from django.shortcuts import render
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from apps.accounts.decorators import require_rol
from apps.events.models import Evento
from apps.tickets.models import Reserva


@require_rol('organizador')
def events_view(request):
    """Vista de eventos del organizador"""
    eventos = Evento.objects.filter(organizador=request.user)
    reservas_confirmadas = Reserva.objects.filter(evento__organizador=request.user, estado='confirmada')
    total_eventos = eventos.count()
    total_reservas = reservas_confirmadas.aggregate(total=Sum('cantidad'))['total'] or 0
    ingresos_totales = reservas_confirmadas.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('cantidad') * F('evento__precio'),
                output_field=DecimalField(max_digits=14, decimal_places=2)
            )
        )
    )['total'] or 0.00

    context = {
        'eventos': eventos,
        'total_eventos': total_eventos,
        'total_reservas': total_reservas,
        'ingresos_totales': ingresos_totales,
    }
    return render(request, 'organizador/events.html', context)


@require_rol('organizador')
def reservations_view(request):
    """Vista de reservaciones del organizador"""
    context = {
        'reservaciones': [],
    }
    return render(request, 'organizador/reservations.html', context)
