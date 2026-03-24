from django.urls import path
from . import views

app_name = 'organizer'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('events/', views.events_view, name='events'),
    path('reservations/', views.reservations_view, name='reservations'),
]
