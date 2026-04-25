from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import require_rol


@require_rol('organizador')
def events_view(request):
    """Vista de eventos del organizador"""
    # Contexto necesario para la plantilla
    context = {
        'eventos': [],  # Aquí puedes agregar la lógica para obtener eventos del BD
        'total_reservas': 0,
        'ingresos_totales': 0.00,
    }
    return render(request, 'organizador/events.html', context)


@require_rol('organizador')
def reservations_view(request):
    """Vista de reservaciones del organizador"""
    context = {
        'reservaciones': [],  # Aquí puedes agregar la lógica para obtener reservaciones
    }
    return render(request, 'organizador/reservations.html', context)
