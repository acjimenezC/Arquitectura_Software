from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('crear/', views.crear_evento_view, name='crear'),
    path('mis-eventos/', views.mis_eventos_view, name='mis_eventos'),
]
