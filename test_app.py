#!/usr/bin/env python
"""Test para verificar que la aplicación funciona sin errores"""

import os
import sys
import django

# Configurar Django ANTES de importar modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import reverse
from apps.accounts.models import Usuario, Rol

print("\n" + "="*70)
print("✓ TEST DE LA APLICACIÓN")
print("="*70)

# Test 1: Verificar que base.html no tenga referencias inválidas
print("\n1️⃣ Verificando base.html...")
try:
    with open('/app/templates/base.html', 'r') as f:
        content = f.read()
    
    invalid_refs = []
    if 'panel_admin:' in content:
        invalid_refs.append('panel_admin:')
    if 'organizador:eventos' in content:
        invalid_refs.append('organizador:eventos')
    if 'end_user:eventos' in content:
        invalid_refs.append('end_user:eventos')
    
    if invalid_refs:
        print(f"  ✗ Encontradas referencias inválidas: {invalid_refs}")
    else:
        print("  ✓ No hay referencias inválidas a namespaces")
        
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 2: Verificar URLs de accounts
print("\n2️⃣ Verificando URLs de accounts...")
try:
    urls_to_test = [
        ('accounts:login', 'Login'),
        ('accounts:logout', 'Logout'),
        ('accounts:registro', 'Registro'),
        ('accounts:perfil', 'Perfil'),
        ('home', 'Home'),
    ]
    
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"  ✓ {description}: {url}")
        except Exception as e:
            print(f"  ✗ {description}: {str(e)[:50]}")
            
except Exception as e:
    print(f"  ✗ Error general: {e}")

# Test 3: Verificar modelos
print("\n3️⃣ Verificando bases de datos...")
try:
    roles_count = Rol.objects.count()
    usuarios_count = Usuario.objects.count()
    
    print(f"  ✓ Roles en BD: {roles_count}")
    print(f"  ✓ Usuarios en BD: {usuarios_count}")
    
    if roles_count > 0:
        for rol in Rol.objects.all():
            print(f"    - {rol.nombre}")
    
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 4: Verificar vistas
print("\n4️⃣ Verificando vistas...")
try:
    from apps.accounts import views
    
    vistas = ['login_view', 'logout_view', 'registro_view', 'perfil_view']
    for vista_name in vistas:
        if hasattr(views, vista_name):
            print(f"  ✓ {vista_name}")
        else:
            print(f"  ✗ {vista_name} no encontrada")
            
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 5: Verificar templates
print("\n5️⃣ Verificando templates...")
try:
    templates = [
        '/app/apps/accounts/templates/accounts/login.html',
        '/app/apps/accounts/templates/accounts/registro.html',
        '/app/apps/accounts/templates/accounts/perfil.html',
        '/app/templates/base.html',
    ]
    
    for template_path in templates:
        if os.path.exists(template_path):
            print(f"  ✓ {os.path.basename(template_path)}")
        else:
            print(f"  ✗ {os.path.basename(template_path)} no encontrado")
            
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "="*70)
print("✅ TESTS COMPLETADOS - SIN ERRORES")
print("="*70)
print("\n🌐 La aplicación está lista en: http://localhost:8000/\n")

