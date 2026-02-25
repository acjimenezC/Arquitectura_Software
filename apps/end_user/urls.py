from django.urls import path
from . import views

app_name = 'end_user'

urlpatterns = [
    path('eventos/', views.eventos_view, name='eventos'),
]
