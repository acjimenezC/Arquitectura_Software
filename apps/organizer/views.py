from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='accounts:login')
def events_view(request):
    """Vista de eventos del organizador"""
    return render(request, 'organizador/events.html')
