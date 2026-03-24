from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from apps.accounts.decorators import require_rols
from .models import Evento
from .forms import EventoForm


def eventos_list_view(request):
    """Vista pública para listar todos los eventos activos"""
    eventos = Evento.objects.filter(activo=True).select_related('organizador')

    # Filtros desde GET
    query = request.GET.get('q', '').strip()
    lugar = request.GET.get('lugar', '').strip()
    fecha = request.GET.get('fecha', '').strip()
    categoria = request.GET.get('categoria', '').strip()

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
    
    if categoria:
        eventos = eventos.filter(categoria=categoria)

    # Lugares únicos para el filtro desplegable
    lugares = Evento.objects.filter(activo=True).values_list('lugar', flat=True).distinct().exclude(lugar='')

    context = {
        'eventos': eventos,
        'lugares': lugares,
        'query': query,
        'lugar_seleccionado': lugar,
        'fecha_seleccionada': fecha,
        'categoria_seleccionada': categoria,
        'total_eventos': eventos.count(),
    }
    return render(request, 'eventos_list.html', context)


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
    return render(request, 'eventos/evento_detail.html', context)


@login_required(login_url='accounts:login')
@require_rols('organizador', 'admin')
def crear_evento_view(request):
    """Vista para crear eventos - solo organizadores y admin"""
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
            evento.save()
            messages.success(request, f'Evento "{evento.nombre}" creado exitosamente.')
            return redirect('events:mis_eventos')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = EventoForm()
    
    return render(request, 'eventos/crear_evento.html', {'form': form})


@login_required(login_url='accounts:login')
@require_rols('organizador', 'admin')
def mis_eventos_view(request):
    """Vista para ver los eventos creados por el usuario"""
    eventos = Evento.objects.filter(organizador=request.user)
    return render(request, 'eventos/mis_eventos.html', {'eventos': eventos})
