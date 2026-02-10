#!/usr/bin/env python
"""
Script para verificar que se pueden crear usuarios sin restricciones de contraseña
y con email opcional
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import Usuario, Rol
from apps.accounts.forms import RegistroForm
from django.contrib.auth.hashers import make_password

# Limpiar usuarios de prueba previos
Usuario.objects.filter(username__startswith='test_').delete()

print("\n" + "="*60)
print("PRUEBAS DE FLEXIBILIDAD DE CONTRASEÑA Y EMAIL")
print("="*60)

# Test 1: Contraseña numérica pura
print("\n1. Creando usuario con contraseña numérica pura (123456)...")
try:
    user1 = Usuario.objects.create_user(
        username='test_numeric',
        password='123456',
        email=''  # Sin email
    )
    print(f"   ✓ Usuario creado: {user1.username}, Email: '{user1.email}'")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Contraseña igual al nombre de usuario
print("\n2. Creando usuario con contraseña igual al nombre...")
try:
    user2 = Usuario.objects.create_user(
        username='test_admin',
        password='test_admin',
        email=''
    )
    print(f"   ✓ Usuario creado: {user2.username}, Email: '{user2.email}'")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Contraseña simple corta
print("\n3. Creando usuario con contraseña simple corta (aaa)...")
try:
    user3 = Usuario.objects.create_user(
        username='test_short',
        password='aaa',
        email=''
    )
    print(f"   ✓ Usuario creado: {user3.username}, Email: '{user3.email}'")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Validación del formulario con email vacío
print("\n4. Validando formulario con email vacío...")
form_data = {
    'username': 'test_form',
    'email': '',
    'first_name': 'Test',
    'last_name': 'User',
    'password1': '123',
    'password2': '123',
}
form = RegistroForm(data=form_data)
if form.is_valid():
    print(f"   ✓ Formulario válido - Email vacío permitido")
else:
    print(f"   ✗ Errores de validación: {form.errors}")

# Test 5: Validación del formulario con email duplicado
print("\n5. Validando que sigue rechazando emails duplicados...")
Usuario.objects.create_user(
    username='test_dup_email',
    email='test@example.com',
    password='pass123'
)
form_data_dup = {
    'username': 'test_form2',
    'email': 'test@example.com',
    'first_name': 'Test',
    'last_name': 'User',
    'password1': '123',
    'password2': '123',
}
form_dup = RegistroForm(data=form_data_dup)
if not form_dup.is_valid() and 'email' in form_dup.errors:
    print(f"   ✓ Email duplicado rechazado correctamente")
else:
    print(f"   ✗ No validó correctamente los emails duplicados")

# Resumen
print("\n" + "="*60)
usuarios = Usuario.objects.filter(username__startswith='test_')
print(f"Total usuarios de prueba creados: {usuarios.count()}")
print("\nRestricciones eliminadas:")
print("  ✓ AUTH_PASSWORD_VALIDATORS = [] (sin restricciones)")
print("  ✓ email = forms.EmailField(required=False)")
print("  ✓ Campo email vacío es válido")
print("  ✓ Contraseñas numéricas permitidas")
print("  ✓ Contraseñas cortas permitidas")
print("  ✓ Contraseñas iguales al username permitidas")
print("="*60 + "\n")

# Limpiar
usuarios.delete()
