"""
Vista para gestión de Tickets en Panel Admin.

Replica la funcionalidad de Django Admin pero con diseño personalizado
y mejor escalabilidad.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator

from apps.accounts.decorators import require_rol, require_activo
from apps.tickets.models import Ticket
from apps.tickets.services import TicketService
from apps.events.models import Evento


@require_rol('admin')
@require_activo
def tickets_list(request):
    """
    Listado profesional de tickets con filtros, búsqueda y acciones masivas.
    Reemplaza Django Admin con mejor UX.
    """
    
    # Base de datos
    tickets = Ticket.objects.select_related('usuario', 'evento').all()
    
    # FILTROS
    filtro_estado = request.GET.get('estado')
    filtro_validado = request.GET.get('validado')
    filtro_evento = request.GET.get('evento')
    busqueda = request.GET.get('q')
    
    # Aplicar filtros
    if filtro_estado == 'activo':
        tickets = tickets.filter(activo=True)
    elif filtro_estado == 'cancelado':
        tickets = tickets.filter(activo=False)
    
    if filtro_validado == 'validado':
        tickets = tickets.filter(validado=True)
    elif filtro_validado == 'no_validado':
        tickets = tickets.filter(validado=False)
    
    if filtro_evento:
        tickets = tickets.filter(evento_id=filtro_evento)
    
    # BÚSQUEDA
    if busqueda:
        tickets = tickets.filter(
            Q(usuario__username__icontains=busqueda) |
            Q(usuario__email__icontains=busqueda) |
            Q(evento__nombre__icontains=busqueda) |
            Q(codigo_unico__icontains=busqueda)
        )
    
    # ORDENAMIENTO
    tickets = tickets.order_by('-fecha_compra')
    
    # PAGINACIÓN
    paginator = Paginator(tickets, 25)  # 25 tickets por página
    page_num = request.GET.get('page', 1)
    page = paginator.get_page(page_num)
    
    # ESTADÍSTICAS
    total_tickets = Ticket.objects.filter(activo=True).aggregate(
        total=Sum('cantidad', default=0)
    )['total'] or 0
    
    total_validados = Ticket.objects.filter(validado=True).aggregate(
        total=Sum('cantidad', default=0)
    )['total'] or 0
    
    # Eventos para filtro
    eventos = Evento.objects.all().order_by('nombre')
    
    contexto = {
        'page': page,
        'total_tickets': total_tickets,
        'total_validados': total_validados,
        'tickets_pendientes': total_tickets - total_validados,
        'eventos': eventos,
        'filtro_estado': filtro_estado,
        'filtro_validado': filtro_validado,
        'filtro_evento': filtro_evento,
        'busqueda': busqueda,
    }
    
    return render(request, 'admin_panel/tickets_list.html', contexto)


@require_rol('admin')
@require_activo
def ticket_detail(request, ticket_id):
    """
    Vista detallada de un ticket con opciones de edición.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'cambiar_estado':
            nuevo_estado = request.POST.get('estado')
            if nuevo_estado == 'activo':
                ticket.activo = True
            elif nuevo_estado == 'cancelado':
                ticket.activo = False
            ticket.save()
            messages.success(request, 'Estado actualizado')
        
        elif accion == 'cambiar_validacion':
            nuevo_validado = request.POST.get('validado') == 'true'
            ticket.validado = nuevo_validado
            if nuevo_validado:
                ticket.fecha_validacion = timezone.now()
            else:
                ticket.fecha_validacion = None
            ticket.save()
            messages.success(request, 'Validación actualizada')
        
        elif accion == 'actualizar_notas':
            ticket.notas = request.POST.get('notas', '')
            ticket.save()
            messages.success(request, 'Notas actualizadas')
        
        return redirect('panel_admin:ticket_detail', ticket_id=ticket_id)
    
    contexto = {
        'ticket': ticket,
        'precio_total': ticket.get_total_precio(),
        'estado_display': ticket.get_estado_display_custom(),
        'dias_desde_compra': ticket.get_dias_desde_compra(),
    }
    
    return render(request, 'admin_panel/ticket_detail.html', contexto)


@require_rol('admin')
@require_activo
@require_http_methods(["POST"])
def validar_ticket(request, ticket_id):
    """
    Valida un ticket (marca como utilizado).
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    resultado = ticket.validar_entrada()
    
    if resultado['valido']:
        messages.success(request, f"Ticket validado correctamente")
    else:
        messages.error(request, f"No se puede validar: {resultado['mensaje']}")
    
    return redirect('panel_admin:ticket_detail', ticket_id=ticket_id)


@require_rol('admin')
@require_activo
@require_http_methods(["POST"])
def cancelar_ticket(request, ticket_id):
    """
    Cancela un ticket.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    razon = request.POST.get('razon', '')
    
    resultado = TicketService.cancelar_reserva(ticket, razon)
    
    if resultado['exito']:
        messages.success(request, resultado['mensaje'])
    else:
        messages.error(request, resultado['mensaje'])
    
    return redirect('panel_admin:ticket_detail', ticket_id=ticket_id)


@require_rol('admin')
@require_activo
@require_http_methods(["POST"])
def acciones_masivas(request):
    """
    Ejecuta acciones sobre múltiples tickets.
    """
    accion = request.POST.get('accion')
    ticket_ids = request.POST.getlist('ticket_ids')
    tickets = Ticket.objects.filter(id__in=ticket_ids)
    
    if accion == 'validar':
        count = 0
        for ticket in tickets:
            if ticket.puede_canjearse():
                resultado = ticket.validar_entrada()
                if resultado['valido']:
                    count += 1
        messages.success(request, f'{count} ticket(s) validados')
    
    elif accion == 'revertir_validacion':
        count = tickets.filter(validado=True).update(
            validado=False,
            fecha_validacion=None
        )
        messages.success(request, f'{count} ticket(s) revertidos')
    
    elif accion == 'cancelar':
        count = 0
        for ticket in tickets.filter(activo=True, validado=False):
            try:
                ticket.cancelar()
                count += 1
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        messages.success(request, f'{count} ticket(s) cancelados')
    
    elif accion == 'reactivar':
        count = tickets.filter(activo=False).update(activo=True)
        messages.success(request, f'{count} ticket(s) reactivados')
    
    return redirect('panel_admin:tickets_list')


@require_rol('admin')
@require_activo
def tickets_estadisticas(request):
    """
    Dashboard con estadísticas avanzadas de tickets.
    """
    
    # Estadísticas globales
    total_tickets = Ticket.objects.filter(activo=True).aggregate(
        total=Sum('cantidad', default=0)
    )['total'] or 0
    
    total_validados = Ticket.objects.filter(validado=True).aggregate(
        total=Sum('cantidad', default=0)
    )['total'] or 0
    
    total_cancelados = Ticket.objects.filter(activo=False).aggregate(
        total=Sum('cantidad', default=0)
    )['total'] or 0
    
    # Ingresos
    total_ingresos = Ticket.objects.filter(
        activo=True
    ).annotate(
        total=F('cantidad') * F('evento__precio')
    ).aggregate(
        suma=Sum('total', default=0)
    )['suma'] or 0
    
    # Tickets por evento
    tickets_por_evento = Ticket.objects.filter(
        activo=True
    ).values('evento__nombre').annotate(
        total=Sum('cantidad', default=0)
    ).order_by('-total')[:10]
    
    # Usuarios con más compras
    usuarios_top = Ticket.objects.filter(
        activo=True
    ).values('usuario__username').annotate(
        total=Count('id'),
        gasto=Sum(F('cantidad') * F('evento__precio'), output_field=models.DecimalField())
    ).order_by('-total')[:10]
    
    # Tasa de validación
    tasa_validacion = (total_validados / total_tickets * 100) if total_tickets > 0 else 0
    
    contexto = {
        'total_tickets': total_tickets,
        'total_validados': total_validados,
        'total_cancelados': total_cancelados,
        'ingresos': total_ingresos,
        'tickets_pendientes': total_tickets - total_validados,
        'tasa_validacion': round(tasa_validacion, 2),
        'tickets_por_evento': tickets_por_evento,
        'usuarios_top': usuarios_top,
    }
    
    return render(request, 'admin_panel/tickets_estadisticas.html', contexto)


# ============================================================================
# API JSON para AJAX / Integraciones
# ============================================================================

@require_rol('admin')
@require_activo
def api_ticket_detail(request, ticket_id):
    """
    API JSON para obtener detalles de un ticket.
    Escalable para móvil o llamadas AJAX.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    return JsonResponse({
        'id': ticket.id,
        'codigo_unico': str(ticket.codigo_unico),
        'usuario': ticket.usuario.username,
        'evento': ticket.evento.nombre,
        'cantidad': ticket.cantidad,
        'fecha_compra': ticket.fecha_compra.isoformat(),
        'fecha_validacion': ticket.fecha_validacion.isoformat() if ticket.fecha_validacion else None,
        'activo': ticket.activo,
        'validado': ticket.validado,
        'precio_total': float(ticket.get_total_precio()),
        'estado': ticket.get_estado_display_custom(),
    })


@require_rol('admin')
@require_activo
def api_validar_por_codigo(request):
    """
    API para validar ticket por código QR.
    Escalable para torniquetes, aplicaciones móviles, etc.
    """
    codigo = request.GET.get('codigo', '')
    
    resultado = Ticket.validar_por_codigo(codigo)
    
    return JsonResponse({
        'valido': resultado['valido'],
        'codigo': resultado['codigo'],
        'mensaje': resultado['mensaje'],
        'detalles': {k: v for k, v in resultado.items() 
                     if k not in ['valido', 'codigo', 'mensaje']}
    })


@require_rol('admin')
@require_activo
def api_disponibilidad_evento(request, evento_id):
    """
    API para obtener disponibilidad de un evento.
    """
    evento = get_object_or_404(Evento, id=evento_id)
    info = TicketService.obtener_disponibilidad_evento(evento)
    
    return JsonResponse(info)
