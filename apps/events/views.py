from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import require_rols
from .models import Evento
from .forms import EventoForm


def eventos_list_view(request):
    """Vista pública para listar y buscar eventos"""
    query = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    lugar = request.GET.get('lugar', '').strip()
    fecha = request.GET.get('fecha', '').strip()

    eventos = Evento.objects.filter(activo=True)

    if categoria:
        eventos = eventos.filter(categoria=categoria)
    elif query:
        eventos = eventos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(lugar__icontains=query)
        )

    if lugar:
        eventos = eventos.filter(lugar__icontains=lugar)

    if fecha:
        eventos = eventos.filter(fecha=fecha)

    lugares = Evento.objects.filter(activo=True).values_list('lugar', flat=True).distinct().exclude(lugar='')

    total_eventos = eventos.count()
    context = {
        'eventos': eventos,
        'lugares': lugares,
        'categoria': categoria,
        'query': query,
        'lugar_seleccionado': lugar,
        'fecha_seleccionada': fecha,
        'total_eventos': total_eventos,
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
    return render(request, 'events/evento_detail.html', context)


@login_required(login_url='accounts:login')
@require_rols('organizador', 'admin')
def crear_evento_view(request):
    """Vista para crear eventos - solo organizadores y admin"""
    
    ######### feedback
    if not request.user.is_superuser and not (request.user.rol and request.user.rol.tiene_permiso('crear_eventos')):
        return HttpResponseForbidden('No tienes permiso para crear eventos')
    ######### feedback
    
    if request.method == 'POST':
        form = EventoForm(request.POST)
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
