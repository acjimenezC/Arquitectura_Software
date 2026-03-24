from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F, DecimalField
from django.utils import timezone
from datetime import timedelta
from apps.accounts.decorators import require_rol
from apps.events.models import Evento
from apps.tickets.models import Ticket


@require_rol('organizador')
def dashboard_view(request):
    """Vista del dashboard de estadísticas del organizador"""
    usuario = request.user
    
    # Obtener eventos del organizador
    eventos = Evento.objects.filter(organizador=usuario, activo=True).select_related('organizador')
    evento_id = request.GET.get('evento')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Filtrar por evento si se selecciona
    if evento_id:
        try:
            evento_seleccionado = Evento.objects.get(id=evento_id, organizador=usuario)
            tickets = Ticket.objects.filter(evento=evento_seleccionado)
        except Evento.DoesNotExist:
            evento_seleccionado = None
            tickets = Ticket.objects.filter(evento__organizador=usuario)
    else:
        evento_seleccionado = None
        tickets = Ticket.objects.filter(evento__organizador=usuario)
    
    # Filtrar por rango de fechas
    if fecha_inicio:
        try:
            desde = timezone.datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            tickets = tickets.filter(fecha_compra__date__gte=desde)
        except ValueError:
            pass
    
    if fecha_fin:
        try:
            hasta = timezone.datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            tickets = tickets.filter(fecha_compra__date__lte=hasta)
        except ValueError:
            pass
    
    # Calcular estadísticas principales
    tickets_totales_result = tickets.aggregate(total=Sum('cantidad'))['total']
    tickets_totales = tickets_totales_result if tickets_totales_result is not None else 0
    tickets_activos_result = tickets.filter(activo=True).aggregate(total=Sum('cantidad'))['total']
    tickets_activos = tickets_activos_result if tickets_activos_result is not None else 0
    tickets_cancelados_result = tickets.filter(activo=False).aggregate(total=Sum('cantidad'))['total']
    tickets_cancelados = tickets_cancelados_result if tickets_cancelados_result is not None else 0
    
    # Ingresos
    ingresos_totales = tickets.filter(activo=True).annotate(
        ingreso=F('evento__precio') * F('cantidad')
    ).aggregate(total=Sum('ingreso', output_field=DecimalField()))['total'] or 0
    
    # Asistentes únicos
    asistentes_unicos = tickets.filter(activo=True, validado=True).values('usuario').distinct().count()
    
    # Datos por evento (tabla)
    eventos_stats = []
    for evento in eventos:
        tickets_evento = Ticket.objects.filter(evento=evento)
        tickets_evento_activos = tickets_evento.filter(activo=True)
        tickets_evento_cancelados = tickets_evento.filter(activo=False)
        
        ingresos_evento = tickets_evento_activos.annotate(
            ingreso=F('evento__precio') * F('cantidad')
        ).aggregate(total=Sum('ingreso', output_field=DecimalField()))['total'] or 0
        
        ocupacion = evento.porcentaje_capacidad_usada()
        
        tickets_vendidos_result = tickets_evento_activos.aggregate(total=Sum('cantidad'))['total']
        tickets_vendidos_count = tickets_vendidos_result if tickets_vendidos_result is not None else 0
        tickets_cancelados_result = tickets_evento_cancelados.aggregate(total=Sum('cantidad'))['total']
        tickets_cancelados_count = tickets_cancelados_result if tickets_cancelados_result is not None else 0
        
        eventos_stats.append({
            'evento': evento,
            'tickets_vendidos': tickets_vendidos_count,
            'tickets_cancelados': tickets_cancelados_count,
            'ingresos': float(ingresos_evento),
            'ocupacion': ocupacion,
        })
    
    # Ordenar por ingresos descendente
    eventos_stats.sort(key=lambda x: x['ingresos'], reverse=True)
    
    # Evento con más ventas
    evento_top = eventos_stats[0] if eventos_stats else None
    
    # Datos para gráficas (últimos 30 días)
    hace_30_dias = timezone.now() - timedelta(days=30)
    tickets_ultimos_30 = Ticket.objects.filter(
        evento__organizador=usuario,
        fecha_compra__gte=hace_30_dias
    )
    
    # Ventas por día (últimos 30 días)
    ventas_por_dia = tickets_ultimos_30.filter(activo=True).extra(
        select={'fecha': 'DATE(fecha_compra)'}
    ).annotate(
        ingreso_ticket=F('evento__precio') * F('cantidad')
    ).values('fecha').annotate(
        cantidad=Sum('cantidad'),
        ingresos=Sum('ingreso_ticket', output_field=DecimalField())
    ).order_by('fecha')
    
    # Preparar datos para Chart.js
    import json
    from decimal import Decimal
    
    # Helper para serializar decimales
    def decimal_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError
    
    # Datos de línea (ventas por día)
    fechas_labels = [str(venta['fecha']) for venta in ventas_por_dia]
    ventas_cantidades = [venta['cantidad'] for venta in ventas_por_dia]
    
    chart_ventas_data = json.dumps({
        'labels': fechas_labels,
        'datasets': [{
            'label': 'Tickets Vendidos',
            'data': ventas_cantidades,
            'borderColor': '#D4AF37',
            'backgroundColor': 'rgba(212, 175, 55, 0.1)',
            'fill': True,
            'tension': 0.4,
        }]
    })
    
    # Datos de pastel (activos vs cancelados)
    # Recalcular para gráfica considerando cantidad
    activos_grafica_result = Ticket.objects.filter(
        evento__organizador=usuario,
        activo=True
    ).aggregate(total=Sum('cantidad'))['total']
    activos_grafica = activos_grafica_result if activos_grafica_result is not None else 0
    
    cancelados_grafica_result = Ticket.objects.filter(
        evento__organizador=usuario,
        activo=False
    ).aggregate(total=Sum('cantidad'))['total']
    cancelados_grafica = cancelados_grafica_result if cancelados_grafica_result is not None else 0
    
    chart_estados_data = json.dumps({
        'labels': ['Activos', 'Cancelados'],
        'datasets': [{
            'label': 'Tickets',
            'data': [activos_grafica, cancelados_grafica],
            'backgroundColor': ['#28a745', '#9b9b9b'],
            'borderColor': ['#1e7e34', '#6b6b6b'],
            'borderWidth': 2,
        }]
    })
    
    # Datos de barras (tickets por evento)
    eventos_labels = [e['evento'].nombre[:20] for e in eventos_stats[:10]]
    eventos_tickets = [e['tickets_vendidos'] for e in eventos_stats[:10]]
    
    chart_eventos_data = json.dumps({
        'labels': eventos_labels,
        'datasets': [{
            'label': 'Tickets Vendidos',
            'data': eventos_tickets,
            'backgroundColor': [
                '#D4AF37', '#C9A227', '#B8860B', '#9b6f37', '#6b4423',
                '#5d3a1a', '#4a2810', '#3a1f0a', '#2a1505', '#1a0a00'
            ],
            'borderColor': '#111111',
            'borderWidth': 1,
        }]
    })
    
    # Calcular crecimiento (comparar con semana anterior)
    hace_7_dias = timezone.now() - timedelta(days=7)
    hace_14_dias = timezone.now() - timedelta(days=14)
    
    tickets_esta_semana_result = tickets.filter(
        activo=True,
        fecha_compra__gte=hace_7_dias
    ).aggregate(total=Sum('cantidad'))['total']
    tickets_esta_semana = tickets_esta_semana_result if tickets_esta_semana_result is not None else 0
    
    tickets_semana_anterior_result = tickets.filter(
        activo=True,
        fecha_compra__gte=hace_14_dias,
        fecha_compra__lt=hace_7_dias
    ).aggregate(total=Sum('cantidad'))['total']
    tickets_semana_anterior = tickets_semana_anterior_result if tickets_semana_anterior_result is not None else 0
    
    if tickets_semana_anterior > 0:
        crecimiento_porcentaje = ((tickets_esta_semana - tickets_semana_anterior) / tickets_semana_anterior) * 100
    else:
        crecimiento_porcentaje = 0 if tickets_esta_semana == 0 else 100
    
    context = {
        'eventos': eventos,
        'evento_seleccionado': evento_seleccionado,
        'tickets_totales': tickets_totales,
        'tickets_activos': tickets_activos,
        'tickets_cancelados': tickets_cancelados,
        'ingresos_totales': float(ingresos_totales),
        'asistentes_unicos': asistentes_unicos,
        'ocupacion_promedio': sum([e['ocupacion'] for e in eventos_stats]) // len(eventos_stats) if eventos_stats else 0,
        'evento_top': evento_top,
        'eventos_stats': eventos_stats,
        'chart_ventas_data': chart_ventas_data,
        'chart_estados_data': chart_estados_data,
        'chart_eventos_data': chart_eventos_data,
        'crecimiento_porcentaje': round(crecimiento_porcentaje, 1),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'organizador/dashboard.html', context)


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
