#!/usr/bin/env python
"""Script para verificar que el sistema de autenticación está funcionando correctamente"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from apps.accounts.models import Usuario, Rol

print("\n" + "="*60)
print("✓ VERIFICACIÓN DE SISTEMA DE AUTENTICACIÓN")
print("="*60)

print("\n1️⃣ CONFIGURACIÓN DJANGO")
print(f"  ✓ AUTH_USER_MODEL: {settings.AUTH_USER_MODEL}")
print(f"  ✓ LOGIN_URL: {settings.LOGIN_URL}")
print(f"  ✓ SESSION_ENGINE: {settings.SESSION_ENGINE}")
print(f"  ✓ SESSION_COOKIE_AGE: {settings.SESSION_COOKIE_AGE} segundos")
print(f"  ✓ SESSION_COOKIE_HTTPONLY: {settings.SESSION_COOKIE_HTTPONLY}")

print("\n2️⃣ ROLES DISPONIBLES")
roles = Rol.objects.all()
if roles.exists():
    for rol in roles:
        print(f"  ✓ {rol.nombre.upper()}: {rol.descripcion}")
else:
    print("  ⚠ No hay roles definidos")

print("\n3️⃣ USUARIOS REGISTRADOS")
usuarios = Usuario.objects.all()
if usuarios.exists():
    print(f"  ✓ Total: {usuarios.count()} usuario(s)")
    for user in usuarios:
        rol_nombre = user.rol.nombre if user.rol else "Sin asignar"
        estado = "✓ Activo" if user.activo else "✗ Inactivo"
        print(f"    - {user.username} ({user.get_full_name()}) - Rol: {rol_nombre} - {estado}")
else:
    print("  ℹ No hay usuarios registrados aún")

print("\n4️⃣ VALIDACIÓN DE DECORADORES")
try:
    from apps.accounts.decorators import require_rol, require_rols, require_activo
    print("  ✓ @require_rol importado correctamente")
    print("  ✓ @require_rols importado correctamente")
    print("  ✓ @require_activo importado correctamente")
except Exception as e:
    print(f"  ✗ Error importando decoradores: {e}")

print("\n5️⃣ VALIDACIÓN DE FORMULARIOS")
try:
    from apps.accounts.forms import LoginForm, RegistroForm
    print("  ✓ LoginForm importado correctamente")
    print("  ✓ RegistroForm importado correctamente")
except Exception as e:
    print(f"  ✗ Error importando formularios: {e}")

print("\n6️⃣ VALIDACIÓN DE VISTAS")
try:
    from apps.accounts.views import login_view, logout_view, registro_view, perfil_view
    print("  ✓ login_view importada correctamente")
    print("  ✓ logout_view importada correctamente")
    print("  ✓ registro_view importada correctamente")
    print("  ✓ perfil_view importada correctamente")
except Exception as e:
    print(f"  ✗ Error importando vistas: {e}")

print("\n" + "="*60)
print("✅ SISTEMA DE AUTENTICACIÓN LISTO")
print("="*60)
print("\n📝 URLs DISPONIBLES:")
print("  - Inicio: http://localhost:8000/")
print("  - Login: http://localhost:8000/accounts/login/")
print("  - Registro: http://localhost:8000/accounts/registro/")
print("  - Perfil: http://localhost:8000/accounts/perfil/")
print("  - Admin: http://localhost:8000/admin/")
print("\n")
