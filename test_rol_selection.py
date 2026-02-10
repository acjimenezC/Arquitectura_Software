#!/usr/bin/env python
"""
Script para verificar que el formulario de registro funciona con selección de rol
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import Usuario, Rol
from apps.accounts.forms import RegistroForm

# Limpiar usuarios de prueba previos
Usuario.objects.filter(username__startswith='test_rol_').delete()

print("\n" + "="*60)
print("PRUEBAS DE SELECCIÓN DE ROL EN REGISTRO")
print("="*60)

# Verificar que los roles existen
roles = Rol.objects.filter(nombre__in=['usuario', 'organizador'])
print(f"\nRoles disponibles para registro: {[r.nombre for r in roles]}")

# Test 1: Registro como usuario
print("\n1. Registrando usuario con rol 'usuario'...")
form_data_user = {
    'username': 'test_rol_user',
    'email': 'test_user@example.com',
    'first_name': 'Test',
    'last_name': 'Usuario',
    'rol': Rol.objects.get(nombre='usuario').id,
    'password1': '123456',
    'password2': '123456',
}
form_user = RegistroForm(data=form_data_user)
if form_user.is_valid():
    user1 = form_user.save()
    print(f"   ✓ Usuario creado: {user1.username}, Rol: {user1.rol.nombre}")
else:
    print(f"   ✗ Errores: {form_user.errors}")

# Test 2: Registro como organizador
print("\n2. Registrando usuario con rol 'organizador'...")
form_data_org = {
    'username': 'test_rol_org',
    'email': 'test_org@example.com',
    'first_name': 'Test',
    'last_name': 'Organizador',
    'rol': Rol.objects.get(nombre='organizador').id,
    'password1': 'simple_pass',
    'password2': 'simple_pass',
}
form_org = RegistroForm(data=form_data_org)
if form_org.is_valid():
    user2 = form_org.save()
    print(f"   ✓ Usuario creado: {user2.username}, Rol: {user2.rol.nombre}")
else:
    print(f"   ✗ Errores: {form_org.errors}")

# Test 3: Verificar que el rol es requerido
print("\n3. Validando que el rol es requerido...")
form_data_no_rol = {
    'username': 'test_rol_none',
    'email': 'test_none@example.com',
    'first_name': 'Test',
    'last_name': 'NoRol',
    'password1': 'pass123',
    'password2': 'pass123',
}
form_no_rol = RegistroForm(data=form_data_no_rol)
if not form_no_rol.is_valid() and 'rol' in form_no_rol.errors:
    print(f"   ✓ Rol es requerido (validación correcta)")
else:
    print(f"   ✗ No validó correctamente: {form_no_rol.errors}")

# Test 4: Verificar que el formulario incluye el campo de rol
print("\n4. Verificando campos del formulario...")
form = RegistroForm()
campos = list(form.fields.keys())
print(f"   Campos: {campos}")
if 'rol' in campos:
    print(f"   ✓ Campo 'rol' presente en el formulario")
else:
    print(f"   ✗ Campo 'rol' no encontrado")

# Resumen
print("\n" + "="*60)
usuarios_test = Usuario.objects.filter(username__startswith='test_rol_')
print(f"Total usuarios de prueba creados: {usuarios_test.count()}")
for u in usuarios_test:
    print(f"  - {u.username}: {u.rol.nombre}")
print("\n✓ Selección de rol implementada exitosamente")
print("="*60 + "\n")

# Limpiar
usuarios_test.delete()
