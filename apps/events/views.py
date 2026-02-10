from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import require_rols
from .models import Evento
from .forms import EventoForm


@login_required(login_url='accounts:login')
@require_rols('organizador', 'admin')
def crear_evento_view(request):
    """Vista para crear eventos - solo organizadores y admin"""
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
