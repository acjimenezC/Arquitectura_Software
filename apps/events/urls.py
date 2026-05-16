from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.eventos_list_view, name='list'),
    path('<int:pk>/', views.evento_detail_view, name='detail'),
    path('crear_evento/', views.crear_evento_view, name='crear_evento'),
    path('mis-eventos/', views.mis_eventos_view, name='mis_eventos'),
]
