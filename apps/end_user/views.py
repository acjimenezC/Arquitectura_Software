from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required


@login_required(login_url='accounts:login')
def eventos_view(request):
    """Vista de eventos del usuario final"""
    from apps.events.models import Evento
    eventos = Evento.objects.filter(activo=True)
    return render(request, 'usuario/eventos.html', {'eventos': eventos})


@login_required(login_url='accounts:login')
def mis_tickets_view(request):
    """Vista de tickets del usuario final"""
    from apps.tickets.models import Ticket
    from django.shortcuts import redirect
    from django.contrib import messages
    
    # Procesar cancelación de tickets
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'cancelar_ticket':
            ticket_id = request.POST.get('ticket_id')
            ticket = get_object_or_404(Ticket, pk=ticket_id, usuario=request.user)
            
            # Validar que el ticket pueda ser cancelado
            if not ticket.activo:
                messages.error(request, 'Este ticket ya ha sido cancelado.')
                return redirect('end_user:mis_tickets')
            
            if ticket.validado:
                messages.error(request, 'No puedes cancelar un ticket que ya ha sido validado.')
                return redirect('end_user:mis_tickets')
            
            # Verificar límite de 2 cancelaciones del mismo evento
            cancelaciones_previas = ticket.contar_cancelaciones_evento()
            if cancelaciones_previas >= 2:
                messages.error(
                    request, 
                    f'Ya has cancelado 2 veces tickets para {ticket.evento.nombre}. '
                    'No puedes cancelar más tickets de este evento.'
                )
                return redirect('end_user:mis_tickets')
            
            # Procesar la cancelación
            razon = request.POST.get('razon', '')
            try:
                ticket.cancelar(razon=razon)
                messages.success(
                    request, 
                    f'Tu ticket para {ticket.evento.nombre} ha sido cancelado exitosamente. '
                    f'El espacio ha sido liberado.'
                )
            except Exception as e:
                messages.error(request, f'Error al cancelar el ticket: {str(e)}')
            
            return redirect('end_user:mis_tickets')
    
    # Mostrar todos los tickets del usuario (activos e inactivos)
    tickets = Ticket.objects.filter(usuario=request.user).select_related('evento').order_by('-fecha_compra')
    
    return render(request, 'usuario/mis_tickets.html', {'tickets': tickets})


@login_required(login_url='accounts:login')
def reservar_view(request, evento_id):
    """Vista de reserva de tickets del usuario final"""
    from apps.events.models import Evento
    from apps.tickets.models import Ticket
    from django.shortcuts import redirect
    from django.contrib import messages
    from django.core.exceptions import ValidationError
    from django.db import IntegrityError
    
    evento = get_object_or_404(Evento, pk=evento_id, activo=True)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        if cantidad < 1:
            cantidad = 1
        
        if evento.tickets_disponibles() >= cantidad:
            try:
                Ticket.objects.create(
                    usuario=request.user,
                    evento=evento,
                    cantidad=cantidad
                )
                messages.success(request, f'Reserva exitosa para {cantidad} ticket(s) de {evento.nombre}')
                return redirect('end_user:mis_tickets')
            except (ValidationError, IntegrityError) as e:
                # Manejar error de ticket duplicado
                if 'un_ticket_por_usuario_evento' in str(e) or 'already exists' in str(e):
                    messages.error(
                        request, 
                        f'Ya compraste una entrada para {evento.nombre}. No puedes comprar más tickets del mismo evento.'
                    )
                else:
                    messages.error(request, f'Error al procesar la reserva: {str(e)}')
        else:
            messages.error(request, 'No hay suficientes tickets disponibles')
    
    context = {
        'evento': evento,
        'disponibles': evento.tickets_disponibles(),
    }
    return render(request, 'usuario/reservar.html', context)

@login_required(login_url='accounts:login')
def crear_evento_view(request):
    """Vista para crear eventos desde el usuario final (si se le da permiso)"""
    from apps.events.views import crear_evento_view
    return crear_evento_view(request)
