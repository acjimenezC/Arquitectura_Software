from django.urls import path
from . import views

app_name = 'organizer'

urlpatterns = [
    path('events/', views.events_view, name='events'),
]
