from django.shortcuts import render
from django.db.models import Q
from apps.events.models import Evento
from datetime import datetime


def home_view(request):
    """Vista de home que muestra los eventos destacados con búsqueda"""
    # Obtener parámetros de búsqueda
    q = request.GET.get('q', '').strip()
    lugar = request.GET.get('lugar', '').strip()
    fecha = request.GET.get('fecha', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    
    # Query base: solo eventos activos
    eventos = Evento.objects.filter(activo=True)
    
    # Filtrar por nombre (búsqueda)
    if q:
        eventos = eventos.filter(
            Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )
    
    # Filtrar por ubicación
    if lugar and lugar != 'Cualquier ciudad':
        eventos = eventos.filter(lugar__icontains=lugar)
    
    # Filtrar por fecha
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            eventos = eventos.filter(fecha__gte=fecha_obj)
        except ValueError:
            pass
    
    # Filtrar por categoría
    if categoria:
        eventos = eventos.filter(categoria=categoria)
    
    # Ordenar por fecha
    eventos = eventos.order_by('fecha')[:12]
    
    # Obtener lista de ciudades únicas para el dropdown
    ciudades = Evento.objects.filter(activo=True).values_list('lugar', flat=True).distinct().order_by('lugar')
    
    return render(request, 'landing.html', {
        'eventos': eventos,
        'ciudades': ciudades,
        'search_params': {
            'q': q,
            'lugar': lugar,
            'fecha': fecha,
            'categoria': categoria
        }
    })

