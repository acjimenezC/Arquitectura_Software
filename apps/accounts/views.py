from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from .forms import LoginForm, RegistroForm


def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            user.ultimo_acceso = timezone.now()
            user.save()
            messages.success(request, f'¡Bienvenido {user.get_full_name()}!')
            
            # Redirigir según el rol del usuario
            if user.rol and user.rol.nombre == 'admin':
                return redirect('panel_admin:dashboard')
            elif user.rol and user.rol.nombre == 'organizador':
                return redirect('organizer:events')
            elif user.rol and user.rol.nombre == 'usuario':
                return redirect('end_user:eventos')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('home')


def registro_view(request):
    """Vista de registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Si el rol es admin, marcar como staff y superuser
            if user.rol and user.rol.nombre == 'admin':
                user.is_staff = True
                user.is_superuser = True
                user.save()
                # Auto login al admin
                login(request, user)
                user.ultimo_acceso = timezone.now()
                user.save()
                messages.success(request, '¡Bienvenido administrador!')
                return redirect('panel_admin:dashboard')
            else:
                messages.success(request, 'Cuenta creada exitosamente. Por favor inicia sesión.')
                return redirect('accounts:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistroForm()
    
    return render(request, 'accounts/registro.html', {'form': form})


@login_required(login_url='accounts:login')
def perfil_view(request):
    """Vista del perfil del usuario"""
    usuario = request.user
    
    if request.method == 'POST':
        # Validar que haya un archivo
        if 'foto_perfil' in request.FILES:
            archivo = request.FILES['foto_perfil']
            
            # Validar tamaño (5MB máximo)
            if archivo.size > 5 * 1024 * 1024:  # 5MB
                messages.error(request, 'La imagen debe ser menor a 5MB.')
            # Validar que sea imagen
            elif not archivo.content_type.startswith('image/'):
                messages.error(request, 'Por favor sube una imagen válida.')
            else:
                # Guardar la foto
                usuario.foto_perfil = archivo
                usuario.save()
                messages.success(request, '¡Foto de perfil actualizada correctamente!')
        else:
            messages.warning(request, 'Por favor selecciona una imagen.')
        
        return redirect('accounts:perfil')
    
    return render(request, 'accounts/perfil.html', {'usuario': usuario})


@login_required(login_url='accounts:login')
def configuraciones_view(request):
    """Vista de configuración del usuario"""
    usuario = request.user
    
    if request.method == 'POST':
        usuario.email = request.POST.get('email', usuario.email)
        usuario.first_name = request.POST.get('first_name', usuario.first_name)
        usuario.last_name = request.POST.get('last_name', usuario.last_name)
        usuario.save()
        messages.success(request, 'Configuraciones actualizadas correctamente.')
        return redirect('accounts:configuraciones')
    
    return render(request, 'accounts/configuraciones.html', {'usuario': usuario})
