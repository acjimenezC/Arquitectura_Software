from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Evento


def eventos_list_view(request):
    """Vista pública para listar todos los eventos activos"""
    eventos = Evento.objects.filter(activo=True).select_related('organizador')

    # Filtros desde GET
    query = request.GET.get('q', '').strip()
    lugar = request.GET.get('lugar', '').strip()
    fecha = request.GET.get('fecha', '').strip()

    if query:
        eventos = eventos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(lugar__icontains=query)
        )

    if lugar:
        eventos = eventos.filter(lugar__icontains=lugar)

    if fecha:
        eventos = eventos.filter(fecha=fecha)

    # Lugares únicos para el filtro desplegable
    lugares = Evento.objects.filter(activo=True).values_list('lugar', flat=True).distinct().exclude(lugar='')

    context = {
        'eventos': eventos,
        'lugares': lugares,
        'query': query,
        'lugar_seleccionado': lugar,
        'fecha_seleccionada': fecha,
        'total_eventos': eventos.count(),
    }
    return render(request, 'events/eventos_list.html', context)


def evento_detail_view(request, pk):
    """Vista de detalle de un evento"""
    evento = get_object_or_404(Evento, pk=pk, activo=True)
    eventos_relacionados = Evento.objects.filter(
        lugar=evento.lugar, activo=True
    ).exclude(pk=pk)[:3]

    context = {
        'evento': evento,
        'eventos_relacionados': eventos_relacionados,
    }
    return render(request, 'events/evento_detail.html', context)
