from django.urls import path
from . import views
from . import tickets_views

app_name = 'panel_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reportes/', views.reportes, name='reportes'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/<int:usuario_id>/desactivar/', views.desactivar_usuario, name='desactivar_usuario'),
    path('usuarios/<int:usuario_id>/activar/', views.activar_usuario, name='activar_usuario'),
    path('usuarios/<int:usuario_id>/cambiar-rol/', views.cambiar_rol_usuario, name='cambiar_rol_usuario'),
    path('eventos/demanda/', views.eventos_mas_reservados, name='eventos_demanda'),
    
    # ========== TICKETS ==========
    path('tickets/', tickets_views.tickets_list, name='tickets_list'),
    path('tickets/<int:ticket_id>/', tickets_views.ticket_detail, name='ticket_detail'),
    path('tickets/<int:ticket_id>/validar/', tickets_views.validar_ticket, name='validar_ticket'),
    path('tickets/<int:ticket_id>/cancelar/', tickets_views.cancelar_ticket, name='cancelar_ticket'),
    path('tickets/acciones/masivas/', tickets_views.acciones_masivas, name='acciones_masivas'),
    path('tickets/estadisticas/', tickets_views.tickets_estadisticas, name='tickets_estadisticas'),
    
    # ========== APIs JSON ==========
    path('api/tickets/<int:ticket_id>/', tickets_views.api_ticket_detail, name='api_ticket_detail'),
    path('api/tickets/validar-codigo/', tickets_views.api_validar_por_codigo, name='api_validar_codigo'),
    path('api/eventos/<int:evento_id>/disponibilidad/', tickets_views.api_disponibilidad_evento, name='api_disponibilidad'),
]