from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def require_rol(rol_requerido):
    """Decorador para verificar que el usuario tiene un rol específico"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='accounts:login')
        def wrapper(request, *args, **kwargs):
            if not request.user.rol or request.user.rol.nombre != rol_requerido:
                messages.error(request, 'No tienes permisos para acceder a esta página.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_rols(*roles_requeridos):
    """Decorador para verificar que el usuario tiene uno de varios roles"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='accounts:login')
        def wrapper(request, *args, **kwargs):
            if not request.user.rol or request.user.rol.nombre not in roles_requeridos:
                messages.error(request, 'No tienes permisos para acceder a esta página.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_activo(view_func):
    """Decorador para verificar que el usuario está activo"""
    @wraps(view_func)
    @login_required(login_url='accounts:login')
    def wrapper(request, *args, **kwargs):
        if not request.user.activo:
            messages.error(request, 'Tu cuenta ha sido desactivada.')
            return redirect('accounts:logout')
        return view_func(request, *args, **kwargs)
    return wrapper
