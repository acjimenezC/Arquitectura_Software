"""
EJEMPLOS DE USO - Sistema de Autenticación

Este archivo muestra cómo usar autenticación y roles en tus vistas.
"""

# ============================================================================
# EJEMPLO 1: Vista que requiere login
# ============================================================================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import require_rol, require_rols, require_activo


@login_required(login_url='accounts:login')
def mi_evento(request):
    """Cualquier usuario autenticado puede ver eventos"""
    usuario = request.user
    eventos = usuario.evento_set.all()  # Ejemplo
    return render(request, 'eventos.html', {'eventos': eventos})


# ============================================================================
# EJEMPLO 2: Vista solo para administradores
# ============================================================================

@require_rol('admin')
def panel_admin_dashboard(request):
    """Solo administradores pueden acceder"""
    contexto = {
        'total_usuarios': Usuario.objects.count(),
        'total_eventos': Event.objects.count(),
    }
    return render(request, 'admin/dashboard.html', contexto)


# ============================================================================
# EJEMPLO 3: Vista para admin o organizador
# ============================================================================

@require_rols('admin', 'organizador')
def crear_evento(request):
    """Solo administradores u organizadores pueden crear eventos"""
    if request.method == 'POST':
        # Crear evento
        pass
    return render(request, 'eventos/crear.html')


# ============================================================================
# EJEMPLO 4: En URLs
# ============================================================================

"""
# urls.py de tu app

from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    # Vista pública
    path('', views.lista_eventos, name='lista'),
    
    # Vista protegida by login
    path('crear/', login_required(views.crear_evento), name='crear'),
    
    # Vista protegida por rol
    path('dashboard/', views.dashboard_admin, name='dashboard'),
]
"""


# ============================================================================
# EJEMPLO 5: En Templates
# ============================================================================

"""
<!-- base.html -->

{% if user.is_authenticated %}
    <nav>
        <span>Hola {{ user.get_full_name }}!</span>
        
        {% if user.es_admin %}
            <a href="{% url 'admin:dashboard' %}">Panel Admin</a>
        {% elif user.es_organizador %}
            <a href="{% url 'eventos:crear' %}">Crear Evento</a>
        {% endif %}
        
        <a href="{% url 'accounts:logout' %}">Logout</a>
    </nav>
{% else %}
    <nav>
        <a href="{% url 'accounts:login' %}">Login</a>
        <a href="{% url 'accounts:registro' %}">Registro</a>
    </nav>
{% endif %}
"""


# ============================================================================
# EJEMPLO 6: Acceder a datos del usuario
# ============================================================================

@login_required(login_url='accounts:login')
def mis_tickets(request):
    usuario = request.user
    
    # Información personal
    print(usuario.get_full_name())      # "Juan Pérez"
    print(usuario.email)                # "juan@example.com"
    print(usuario.telefono)             # "3001234567"
    print(usuario.rol.nombre)           # "usuario"
    print(usuario.ultimo_acceso)        # datetime object
    print(usuario.verificado)           # False
    
    # Métodos útiles
    if usuario.es_admin():
        # hacer algo si es admin
        pass
    
    if usuario.es_organizador():
        # hacer algo si es organizador
        pass
    
    # Obtener tickets del usuario
    tickets = usuario.tickets.all()  # Relación personalizada
    
    return render(request, 'tickets.html', {'tickets': tickets})


# ============================================================================
# EJEMPLO 7: Lógica manual dentro de vista
# ============================================================================

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required(login_url='accounts:login')
def editar_evento(request, evento_id):
    evento = Event.objects.get(id=evento_id)
    usuario = request.user
    
    # Verificar que puede editar (es dueño o admin)
    if evento.creador != usuario and not usuario.es_admin():
        return HttpResponseForbidden("No tienes permisos para editar este evento")
    
    # Proceder con la edición
    if request.method == 'POST':
        # actualizar evento
        pass
    
    return render(request, 'evento/editar.html', {'evento': evento})


# ============================================================================
# EJEMPLO 8: Vistas basadas en clases con protección
# ============================================================================

from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class UsuarioEsAdminMixin(UserPassesTestMixin):
    """Mixin para verificar que es admin"""
    login_url = 'accounts:login'
    
    def test_func(self):
        return self.request.user.es_admin()


class ListaEventosView(LoginRequiredMixin, ListView):
    """Vista que requiere login"""
    model = Event
    template_name = 'eventos/lista.html'
    login_url = 'accounts:login'


class PanelAdminView(UsuarioEsAdminMixin, View):
    """Vista que requiere ser admin"""
    def get(self, request):
        contexto = {
            'usuarios': Usuario.objects.all(),
            'eventos': Event.objects.all(),
        }
        return render(request, 'admin/panel.html', contexto)


# ============================================================================
# EJEMPLO 9: Filtrar datos por usuario
# ============================================================================

@login_required(login_url='accounts:login')
def mis_eventos(request):
    usuario = request.user
    
    if usuario.es_organizador():
        # Mostrar solo sus eventos
        eventos = Event.objects.filter(organizador=usuario)
    elif usuario.es_admin():
        # Mostrar todos los eventos
        eventos = Event.objects.all()
    else:
        # Usuario comprador - eventos que puede asistir
        eventos = Event.objects.filter(disponible=True)
    
    return render(request, 'eventos/lista.html', {'eventos': eventos})


# ============================================================================
# EJEMPLO 10: Usar decoradores combinados
# ============================================================================

@require_activo  # Usuario debe estar activo
@require_rol('organizador')  # Debe ser organizador (incluye login_required)
def crear_evento(request):
    """
    Combinación de decoradores:
    1. Verifica que esté autenticado (require_rol lo incluye)
    2. Verifica que sea organizador
    3. Verifica que la cuenta esté activa
    """
    if request.method == 'POST':
        evento = Event.objects.create(
            titulo=request.POST['titulo'],
            descripcion=request.POST['descripcion'],
            organizador=request.user,
        )
        return redirect('eventos:detalle', evento.id)
    
    return render(request, 'eventos/crear.html')
