from django.urls import path
from apps.events import views
from . import views

app_name = 'events'

urlpatterns = [
    # Public listing
    path('', views.eventos_list_view, name='list'),
    path('<int:pk>/', views.evento_detail_view, name='detail'),
    # Existing organizer routes
    path('crear_evento/', views.crear_evento_view, name='crear_evento'),
    path('mis-eventos/', views.mis_eventos_view, name='mis_eventos'),
]
