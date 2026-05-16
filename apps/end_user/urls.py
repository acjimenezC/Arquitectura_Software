from django.urls import path
from . import views

app_name = 'end_user'

urlpatterns = [
    path('eventos/', views.eventos_view, name='eventos'),
    path('mis-tickets/', views.mis_tickets_view, name='mis_tickets'),
    path('mis-tickets/<int:ticket_id>/', views.ticket_detalle_view, name='ticket_detalle'),
    path('reservar/<int:evento_id>/', views.reservar_view, name='reservar'),
    path('pago/<int:evento_id>/', views.pago_view, name='pago'),
    path('crear_evento/', views.crear_evento_view, name='crear_evento'),
]
