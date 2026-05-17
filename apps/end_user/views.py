from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from apps.tickets.models import Reserva, Ticket


def home_view(request):
    """Vista de inicio con eventos destacados"""
    from apps.events.models import Evento
    eventos = Evento.objects.filter(activo=True).order_by('-fecha_creacion')[:3]
    return render(request, 'landing.html', {'eventos': eventos})


@login_required(login_url='accounts:login')
def eventos_view(request):
    """Vista de eventos del usuario final"""
    from apps.events.models import Evento
    eventos = Evento.objects.filter(activo=True).order_by('-fecha_creacion')
    return render(request, 'usuario/eventos.html', {'eventos': eventos})


@login_required(login_url='accounts:login')
def mis_tickets_view(request):
    """Vista de tickets del usuario final"""
    tickets = Ticket.objects.filter(usuario=request.user, activo=True).select_related('evento')
    return render(request, 'usuario/mis_tickets.html', {'tickets': tickets})


@login_required(login_url='accounts:login')
def ticket_detalle_view(request, ticket_id):
    """Detalle de un ticket comprado"""
    ticket = get_object_or_404(Ticket.objects.select_related('evento', 'reserva'), pk=ticket_id, usuario=request.user, activo=True)
    precio_unitario = ticket.evento.precio
    total_pagado = precio_unitario * ticket.cantidad
    return render(request, 'usuario/ticket_detalle.html', {
        'ticket': ticket,
        'precio_unitario': precio_unitario,
        'total_pagado': total_pagado,
    })


@login_required(login_url='accounts:login')
def reservar_view(request, evento_id):
    """Vista de reserva de tickets del usuario final"""
    from apps.events.models import Evento
    from apps.tickets.models import Ticket
    from django.contrib import messages
    
    evento = get_object_or_404(Evento, pk=evento_id, activo=True)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        if cantidad < 1:
            cantidad = 1
        
        if evento.tickets_disponibles >= cantidad:
            if evento.precio > 0:
                pago_url = reverse('end_user:pago', args=[evento.id])
                return redirect(f"{pago_url}?cantidad={cantidad}")

            reserva = Reserva.objects.create(
                usuario=request.user,
                evento=evento,
                cantidad=cantidad,
                estado='confirmada'
            )
            Ticket.objects.create(
                usuario=request.user,
                evento=evento,
                cantidad=cantidad,
                reserva=reserva
            )
            messages.success(request, f'Reserva exitosa para {cantidad} ticket(s) de {evento.nombre}')
            return redirect('end_user:mis_tickets')
        else:
            messages.error(request, 'No hay suficientes tickets disponibles')
 
    back_url = request.GET.get('next') or request.POST.get('next') or ''
    context = {
        'evento': evento,
        'disponibles': evento.tickets_disponibles,
        'back_url': back_url,
    }
    return render(request, 'usuario/reservar.html', context)

@login_required(login_url='accounts:login')
def pago_view(request, evento_id):
    """Vista de pago para confirmar la compra de tickets"""
    from apps.events.models import Evento
    from apps.tickets.models import Ticket
    from django.contrib import messages

    evento = get_object_or_404(Evento, pk=evento_id, activo=True)
    cantidad = int(request.GET.get('cantidad', request.POST.get('cantidad', 1)))
    if cantidad < 1:
        cantidad = 1

    if evento.tickets_disponibles < cantidad:
        messages.error(request, 'No hay suficientes tickets disponibles para completar la compra.')
        return redirect('end_user:reservar', evento_id=evento.id)

    precio_total = evento.precio * cantidad
    errors = []

    if request.method == 'POST':
        tarjeta = request.POST.get('tarjeta', '').replace(' ', '')
        csv = request.POST.get('csv', '').strip()
        expiracion = request.POST.get('expiracion', '').strip()

        if len(tarjeta) != 16 or not tarjeta.isdigit():
            errors.append('Ingrese los 16 números de la tarjeta correctamente.')
        if len(csv) not in (3, 4) or not csv.isdigit():
            errors.append('Ingrese un CSV válido de 3 o 4 dígitos.')
        if not expiracion or len(expiracion) < 5:
            errors.append('Ingrese la fecha de expiración en formato MM/AA.')

        if not errors:
            reserva = Reserva.objects.create(
                usuario=request.user,
                evento=evento,
                cantidad=cantidad,
                estado='confirmada'
            )
            Ticket.objects.create(
                usuario=request.user,
                evento=evento,
                cantidad=cantidad,
                reserva=reserva
            )
            messages.success(request, f'Pago confirmado y ticket(s) reservado(s) para {evento.nombre}')
            return redirect('end_user:mis_tickets')

    context = {
        'evento': evento,
        'cantidad': cantidad,
        'precio_total': precio_total,
        'errors': errors,
    }
    return render(request, 'usuario/pago.html', context)

@login_required(login_url='accounts:login')
def crear_evento_view(request):
    """Vista para crear eventos desde el usuario final (si se le da permiso)"""
    from apps.events.views import crear_evento_view
    return crear_evento_view(request)
