from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='accounts:login')
def eventos_view(request):
    """Vista de eventos del usuario final"""
    return render(request, 'usuario/eventos.html')
