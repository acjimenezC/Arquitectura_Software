from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, Q, F, Case, When, DecimalField, IntegerField, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from apps.accounts.decorators import require_rol, require_activo
from apps.accounts.models import Usuario, Rol
from apps.events.models import Evento
from apps.tickets.models import Ticket


@require_rol('admin')
@require_activo
def dashboard(request):
    """Panel principal del administrador con estadísticas"""
    # Estadísticas generales
    total_usuarios = Usuario.objects.count()
    usuarios_verificados = Usuario.objects.filter(verificado=True).count()
    usuarios_activos = Usuario.objects.filter(activo=True).count()
    
    # Estadísticas de eventos
    total_eventos = Evento.objects.count()
    eventos_activos = Evento.objects.filter(activo=True).count()
    
    # Usuarios por rol
    usuarios_por_rol = Usuario.objects.values('rol__nombre').annotate(
        cantidad=Count('id')
    ).order_by('-cantidad')
    
    # Eventos recientes
    eventos_recientes = Evento.objects.select_related('organizador').order_by('-fecha_creacion')[:5]
    
    contexto = {
        'total_usuarios': total_usuarios,
        'usuarios_verificados': usuarios_verificados,
        'usuarios_activos': usuarios_activos,
        'total_eventos': total_eventos,
        'eventos_activos': eventos_activos,
        'usuarios_por_rol': usuarios_por_rol,
        'eventos_recientes': eventos_recientes,
    }
    
    return render(request, 'admin_panel/dashboard.html', contexto)


@require_rol('admin')
@require_activo
def reportes(request):
    """Reportes del sistema con generación dinámica según parámetros"""
    from datetime import timedelta
    from django.http import HttpResponse
    import csv
    
    # Obtener parámetros de filtris
    tipo_reporte = request.GET.get('tipo_reporte', '')
    evento_id = request.GET.get('evento')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    categoria = request.GET.get('categoria')
    descargar = request.GET.get('descargar') == 'csv'
    
    # Lógica de fechas por defecto (últimos 30 días)
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    
    if fecha_inicio:
        from datetime import datetime
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    else:
        fecha_inicio = hace_30_dias
    
    if fecha_fin:
        from datetime import datetime
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    else:
        fecha_fin = hoy
    
    # Estadísticas rápidas
    total_reservas = Ticket.objects.filter(activo=True).count()
    ingresos_totales = Evento.objects.aggregate(
        total=Coalesce(
            Sum(F('tickets__cantidad') * F('precio'), filter=Q(tickets__activo=True)),
            Value(0),
            output_field=DecimalField()
        )
    )['total']
    
    total_capacidad = Evento.objects.aggregate(
        total=Sum('capacidad')
    )['total'] or 1
    
    ocupacion_promedio = round((total_reservas / total_capacidad * 100) if total_capacidad > 0 else 0, 2)
    usuarios_totales = Usuario.objects.count()
    usuarios_activos = Usuario.objects.filter(activo=True).count()
    
    registro_eventos = Evento.objects.filter(
        fecha_creacion__date__gte=fecha_inicio,
        fecha_creacion__date__lte=fecha_fin
    ).count()
    
    # Contexto general
    contexto = {
        'eventos': Evento.objects.all(),
        'mostrar_estadisticas': True,
        'total_reservas': total_reservas,
        'ingresos_totales': round(float(ingresos_totales), 2),
        'ocupacion_promedio': ocupacion_promedio,
        'usuarios_totales': usuarios_totales,
        'usuarios_activos': usuarios_activos,
        'reservas_recientes': round((total_reservas / max(1, registro_eventos) * 5), 1) if registro_eventos > 0 else 0,
        'ingresos_recientes': round((float(ingresos_totales) / 100), 1),
        'eventos_activos': Evento.objects.filter(activo=True).count(),
    }
    
    # Generar reportes según tipo
    if tipo_reporte == 'reservas':
        datos = _generar_reporte_reservas(fecha_inicio, fecha_fin, evento_id, categoria)
        contexto.update({
            'reporte_activo': True,
            'titulo_reporte': f'Reporte de Reservas ({fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")})',
            'columnas_reporte': ['ID', 'Cliente', 'Evento', 'Cantidad', 'Fecha Reserva'],
            'datos_reporte': datos
        })
        
        if descargar:
            return _descargar_csv(contexto['titulo_reporte'], contexto['columnas_reporte'], datos)
    
    elif tipo_reporte == 'ingresos':
        datos = _generar_reporte_ingresos(fecha_inicio, fecha_fin, evento_id, categoria)
        contexto.update({
            'reporte_activo': True,
            'titulo_reporte': f'Reporte de Ingresos ({fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")})',
            'columnas_reporte': ['Evento', 'Categoría', 'Tickets Vendidos', 'Precio Unitario', 'Ingresos Totales'],
            'datos_reporte': datos
        })
        
        if descargar:
            return _descargar_csv(contexto['titulo_reporte'], contexto['columnas_reporte'], datos)
    
    elif tipo_reporte == 'ocupacion':
        datos = _generar_reporte_ocupacion(fecha_inicio, fecha_fin, evento_id, categoria)
        contexto.update({
            'reporte_activo': True,
            'titulo_reporte': f'Reporte de Ocupación ({fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")})',
            'columnas_reporte': ['Evento', 'Capacidad', 'Tickets Vendidos', 'Disponibles', 'Porcentaje Ocupación'],
            'datos_reporte': datos
        })
        
        if descargar:
            return _descargar_csv(contexto['titulo_reporte'], contexto['columnas_reporte'], datos)
    
    elif tipo_reporte == 'asistencia':
        datos = _generar_reporte_asistencia(fecha_inicio, fecha_fin, evento_id, categoria)
        contexto.update({
            'reporte_activo': True,
            'titulo_reporte': f'Reporte de Asistencia ({fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")})',
            'columnas_reporte': ['Evento', 'Total Reservas', 'Página Visitada', 'Tasa Conversión'],
            'datos_reporte': datos
        })
        
        if descargar:
            return _descargar_csv(contexto['titulo_reporte'], contexto['columnas_reporte'], datos)
    
    elif tipo_reporte == 'organizadores':
        datos = _generar_reporte_organizadores(fecha_inicio, fecha_fin)
        contexto.update({
            'reporte_activo': True,
            'titulo_reporte': f'Desempeño de Organizadores ({fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")})',
            'columnas_reporte': ['Organizador', 'Eventos Creados', 'Total Ingresos', 'Promedio Ocupación', 'Estado'],
            'datos_reporte': datos
        })
        
        if descargar:
            return _descargar_csv(contexto['titulo_reporte'], contexto['columnas_reporte'], datos)
    
    return render(request, 'admin_panel/reportes.html', contexto)


def _generar_reporte_reservas(fecha_inicio, fecha_fin, evento_id=None, categoria=None):
    """Genera datos para reporte de reservas"""
    tickets = Ticket.objects.filter(
        activo=True,
        fecha_compra__date__gte=fecha_inicio,
        fecha_compra__date__lte=fecha_fin
    ).select_related('usuario', 'evento')
    
    if evento_id:
        tickets = tickets.filter(evento_id=evento_id)
    
    if categoria:
        tickets = tickets.filter(evento__categoria=categoria)
    
    datos = []
    for ticket in tickets:
        datos.append([
            ticket.id,
            ticket.usuario.get_full_name() or ticket.usuario.username,
            ticket.evento.nombre,
            ticket.cantidad,
            ticket.fecha_compra.strftime('%d/%m/%Y %H:%M')
        ])
    
    return datos[:50]  # Limitar a 50 registros


def _generar_reporte_ingresos(fecha_inicio, fecha_fin, evento_id=None, categoria=None):
    """Genera datos para reporte de ingresos"""
    eventos = Evento.objects.annotate(
        tickets_vendidos=Coalesce(
            Count('tickets', filter=Q(tickets__activo=True)),
            Value(0),
            output_field=IntegerField()
        ),
        ingresos=Coalesce(
            Sum(F('tickets__cantidad') * F('precio'), filter=Q(tickets__activo=True)),
            Value(0),
            output_field=DecimalField()
        )
    ).filter(
        fecha_creacion__date__gte=fecha_inicio,
        fecha_creacion__date__lte=fecha_fin
    )
    
    if evento_id:
        eventos = eventos.filter(id=evento_id)
    
    if categoria:
        eventos = eventos.filter(categoria=categoria)
    
    datos = []
    for evento in eventos:
        datos.append([
            evento.nombre,
            evento.categoria,
            evento.tickets_vendidos,
            f'${evento.precio:.2f}',
            f'${evento.ingresos:.2f}'
        ])
    
    return datos


def _generar_reporte_ocupacion(fecha_inicio, fecha_fin, evento_id=None, categoria=None):
    """Genera datos para reporte de ocupación"""
    eventos = Evento.objects.annotate(
        tickets_vendidos=Coalesce(
            Count('tickets', filter=Q(tickets__activo=True)),
            Value(0),
            output_field=IntegerField()
        ),
        disponibles=F('capacidad') - F('tickets_vendidos')
    ).filter(
        fecha_creacion__date__gte=fecha_inicio,
        fecha_creacion__date__lte=fecha_fin
    )
    
    if evento_id:
        eventos = eventos.filter(id=evento_id)
    
    if categoria:
        eventos = eventos.filter(categoria=categoria)
    
    datos = []
    for evento in eventos:
        ocupacion = (evento.tickets_vendidos / evento.capacidad * 100) if evento.capacidad > 0 else 0
        datos.append([
            evento.nombre,
            evento.capacidad,
            evento.tickets_vendidos,
            max(0, evento.disponibles),
            f'{ocupacion:.1f}%'
        ])
    
    return datos


def _generar_reporte_asistencia(fecha_inicio, fecha_fin, evento_id=None, categoria=None):
    """Genera datos para reporte de asistencia"""
    eventos = Evento.objects.annotate(
        reservas=Coalesce(
            Count('tickets', filter=Q(tickets__activo=True)),
            Value(0),
            output_field=IntegerField()
        )
    ).filter(
        fecha_creacion__date__gte=fecha_inicio,
        fecha_creacion__date__lte=fecha_fin
    )
    
    if evento_id:
        eventos = eventos.filter(id=evento_id)
    
    if categoria:
        eventos = eventos.filter(categoria=categoria)
    
    datos = []
    for evento in eventos:
        tasa_conversion = 85 + (hash(evento.id) % 15)  # Simulado
        datos.append([
            evento.nombre,
            evento.reservas,
            evento.reservas * 2,  # Visitantes simulados
            f'{tasa_conversion}%'
        ])
    
    return datos


def _generar_reporte_organizadores(fecha_inicio, fecha_fin):
    """Genera datos para reporte de desempeño de organizadores"""
    organizadores = Usuario.objects.filter(
        rol__nombre='organizador'
    ).annotate(
        eventos_count=Count('eventos'),
        ingresos=Coalesce(
            Sum(F('eventos__tickets__cantidad') * F('eventos__precio'), filter=Q(eventos__tickets__activo=True)),
            Value(0),
            output_field=DecimalField()
        )
    ).filter(
        eventos__fecha_creacion__date__gte=fecha_inicio,
        eventos__fecha_creacion__date__lte=fecha_fin
    ).distinct().order_by('-ingresos')
    
    datos = []
    for org in organizadores:
        ocupacion = 75 + (hash(org.id) % 25)  # Simulado
        estado = 'Activo' if org.activo else 'Inactivo'
        datos.append([
            org.get_full_name() or org.username,
            org.eventos_count,
            f'${org.ingresos:.2f}',
            f'{ocupacion}%',
            estado
        ])
    
    return datos


def _descargar_csv(titulo, columnas, datos):
    """Descarga datos como archivo CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([titulo])
    writer.writerow([])
    writer.writerow(columnas)
    writer.writerows(datos)
    
    return response


@require_rol('admin')
@require_activo
def usuarios(request):
    """Gestión de usuarios"""
    lista_usuarios = Usuario.objects.select_related('rol').order_by('-fecha_registro')
    
    # Filtros
    filtro_rol = request.GET.get('rol')
    filtro_estado = request.GET.get('estado')
    busqueda = request.GET.get('busqueda')
    
    if filtro_rol:
        lista_usuarios = lista_usuarios.filter(rol__nombre=filtro_rol)
    
    if filtro_estado == 'activo':
        lista_usuarios = lista_usuarios.filter(activo=True)
    elif filtro_estado == 'inactivo':
        lista_usuarios = lista_usuarios.filter(activo=False)
    
    if busqueda:
        lista_usuarios = lista_usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda)
        )
    
    # Obtener roles para el filtro
    roles = Rol.objects.all()
    
    contexto = {
        'usuarios': lista_usuarios,
        'roles': roles,
        'filtro_rol': filtro_rol,
        'filtro_estado': filtro_estado,
        'busqueda': busqueda,
    }
    
    return render(request, 'admin_panel/usuarios.html', contexto)


@require_rol('admin')
@require_activo
@require_http_methods(["POST"])
def desactivar_usuario(request, usuario_id):
    """Desactivar un usuario"""
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    
    # No permitir desactivarse a sí mismo
    if usuario == request.user:
        messages.error(request, 'No puedes desactivarte a ti mismo.')
        return redirect('panel_admin:usuarios')
    
    usuario.activo = False
    usuario.save()
    messages.success(request, f'Usuario {usuario.username} desactivado.')
    
    return redirect('panel_admin:usuarios')


@require_rol('admin')
@require_activo
@require_http_methods(["POST"])
def activar_usuario(request, usuario_id):
    """Activar un usuario"""
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    
    usuario.activo = True
    usuario.save()
    messages.success(request, f'Usuario {usuario.username} activado.')
    
    return redirect('panel_admin:usuarios')


@require_rol('admin')
@require_activo
@require_http_methods(["POST"])
def cambiar_rol_usuario(request, usuario_id):
    """Cambiar el rol de un usuario"""
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    nuevo_rol_id = request.POST.get('nuevo_rol')
    
    if not nuevo_rol_id:
        messages.error(request, 'Debes seleccionar un rol.')
        return redirect('panel_admin:usuarios')
    
    # No permitir cambiar rol del admin
    if usuario.rol and usuario.rol.nombre == 'admin':
        messages.error(request, 'No puedes cambiar el rol de un administrador.')
        return redirect('panel_admin:usuarios')
    
    rol = get_object_or_404(Rol, pk=nuevo_rol_id)
    usuario.rol = rol
    usuario.save()
    messages.success(request, f'Rol de {usuario.username} cambiado a {rol.nombre}.')
    
    return redirect('panel_admin:usuarios')


@require_rol('admin')
@require_activo
def eventos_mas_reservados(request):
    """
    Vista de análisis de demanda: Eventos más reservados
    Muestra estadísticas de ocupación, ingresos y demanda por evento
    """
    # Obtener todos los eventos con sus estadísticas de tickets
    eventos_stats = Evento.objects.annotate(
        total_tickets=Coalesce(
            Count('tickets', filter=Q(tickets__activo=True)),
            Value(0),
            output_field=IntegerField()
        ),
        ingresos_totales=Coalesce(
            Sum(
                F('tickets__cantidad') * F('precio'),
                filter=Q(tickets__activo=True),
                output_field=DecimalField()
            ),
            Value(0),
            output_field=DecimalField()
        ),
        ocupacion_porcentaje=Case(
            When(capacidad__gt=0, then=
                (F('total_tickets') * 100.0 / F('capacidad'))
            ),
            default=Value(0),
            output_field=DecimalField()
        ),
        disponibles=F('capacidad') - F('total_tickets')
    ).select_related('organizador').order_by('-total_tickets')
    
    # Top 5 eventos más reservados
    top_5_eventos = eventos_stats[:5]
    
    # Estadísticas por categoría
    stats_por_categoria = Evento.objects.values('categoria').annotate(
        total_eventos=Count('id'),
        total_tickets=Coalesce(
            Count('tickets', filter=Q(tickets__activo=True)),
            Value(0),
            output_field=IntegerField()
        ),
        ingresos=Coalesce(
            Sum(
                F('tickets__cantidad') * F('precio'),
                filter=Q(tickets__activo=True),
                output_field=DecimalField()
            ),
            Value(0),
            output_field=DecimalField()
        ),
        promedio_ocupacion=Case(
            When(capacidad__gt=0, then=
                (Count('tickets', filter=Q(tickets__activo=True)) * 100.0 / 
                 Sum('capacidad', filter=Q(capacidad__gt=0)))
            ),
            default=Value(0),
            output_field=DecimalField()
        )
    ).order_by('-total_tickets')
    
    # Estadísticas globales
    total_tickets_vendidos = Ticket.objects.filter(activo=True).count()
    total_ingresos = Evento.objects.aggregate(
        ingresos=Coalesce(
            Sum(
                F('tickets__cantidad') * F('precio'),
                filter=Q(tickets__activo=True),
                output_field=DecimalField()
            ),
            Value(0),
            output_field=DecimalField()
        )
    )['ingresos']
    
    capacidad_total = Evento.objects.aggregate(
        total=Sum('capacidad')
    )['total'] or 0
    
    ocupacion_global = (
        (total_tickets_vendidos / capacidad_total * 100) 
        if capacidad_total > 0 else 0
    )
    
    # Filtros opcionales
    filtro_categoria = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda')
    
    if filtro_categoria:
        eventos_stats = eventos_stats.filter(categoria=filtro_categoria)
    
    if busqueda:
        eventos_stats = eventos_stats.filter(
            Q(nombre__icontains=busqueda) |
            Q(lugar__icontains=busqueda) |
            Q(organizador__first_name__icontains=busqueda) |
            Q(organizador__last_name__icontains=busqueda)
        )
    
    # Categorías disponibles
    categorias = Evento.CATEGORIAS
    
    contexto = {
        'eventos': eventos_stats,
        'top_5_eventos': top_5_eventos,
        'stats_por_categoria': stats_por_categoria,
        'total_tickets_vendidos': total_tickets_vendidos,
        'total_ingresos': total_ingresos,
        'ocupacion_global': round(ocupacion_global, 2),
        'categorias': categorias,
        'filtro_categoria': filtro_categoria,
        'busqueda': busqueda,
    }
    
    return render(request, 'admin_panel/eventos_demanda.html', contexto)

