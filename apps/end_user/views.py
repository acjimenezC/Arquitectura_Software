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
    tickets = Ticket.objects.filter(usuario=request.user, activo=True).select_related('evento')
    return render(request, 'usuario/mis_tickets.html', {'tickets': tickets})


@login_required(login_url='accounts:login')
def reservar_view(request, evento_id):
    """Vista de reserva de tickets del usuario final"""
    from apps.events.models import Evento
    from apps.tickets.models import Ticket
    from django.shortcuts import redirect
    from django.contrib import messages
    
    evento = get_object_or_404(Evento, pk=evento_id, activo=True)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        if cantidad < 1:
            cantidad = 1
        
        if evento.tickets_disponibles() >= cantidad:
            Ticket.objects.create(
                usuario=request.user,
                evento=evento,
                cantidad=cantidad
            )
            messages.success(request, f'Reserva exitosa para {cantidad} ticket(s) de {evento.nombre}')
            return redirect('end_user:mis_tickets')
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
