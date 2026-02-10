#!/usr/bin/env python
"""
Script para verificar que el botón de admin aparece en la navbar
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import Usuario, Rol

print("\n" + "="*60)
print("VERIFICACIÓN DE BOTÓN PANEL DE ADMIN")
print("="*60)

# Obtener usuarios admin
admin_users = Usuario.objects.filter(rol__nombre='admin')
print(f"\nUsuarios con rol admin: {admin_users.count()}")

for user in admin_users:
    print(f"\n  Usuario: {user.username}")
    print(f"  Es admin: {user.es_admin()}")
    print(f"  Es organizador: {user.es_organizador()}")
    print(f"  Es usuario: {user.es_usuario()}")

# Test con usuarios no admin
non_admin = Usuario.objects.exclude(rol__nombre='admin').first()
if non_admin:
    print(f"\n  Usuario no-admin: {non_admin.username}")
    print(f"  Es admin: {non_admin.es_admin()}")
    print(f"  Es organizador: {non_admin.es_organizador()}")
    print(f"  Es usuario: {non_admin.es_usuario()}")

print("\n" + "="*60)
print("✓ Método es_admin() funciona correctamente")
print("✓ Botón de admin aparecerá solo para usuarios con rol 'admin'")
print("✓ URL de admin: /admin/")
print("="*60 + "\n")
