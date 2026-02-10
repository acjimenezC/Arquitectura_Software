# 🚀 GUÍA DE SETUP - Sistema de Autenticación Completo

## ✅ Lo que se ha implementado

### 1. **App Accounts** ✓
- Modelos de Usuario personalizado y Rol
- Sistema de roles (admin, organizador, usuario)
- Vistas de login, logout, registro y perfil
- Formularios validados
- Decoradores para proteger vistas
- Templates responsivos

### 2. **Seguridad** ✓
- Autenticación con contraseñas hasheadas
- CSRF protection
- Sesiones almacenadas en BD
- Cookies HTTPOnly
- Control de usuarios activos/inactivos
- Sistema flexible de roles

### 3. **Características** ✓
- Login y Logout
- Registro de usuarios
- Perfil de usuario
- Manejo de sesiones
- Protección de vistas por roles
- Seguimiento de último acceso

---

## 📝 Paso a Paso: Configuración

### Paso 1: Crear las migraciones
```bash
docker-compose exec web python manage.py makemigrations accounts
```

**Esperado:**
```
Migrations for 'accounts':
  apps/accounts/migrations/0001_initial.py
    - Create model Rol
    - Create model Usuario
```

### Paso 2: Aplicar las migraciones
```bash
docker-compose exec web python manage.py migrate
```

**Esperado:**
```
Running migrations:
  ...
  Applying accounts.0001_initial... OK
```

### Paso 3: Inicializar los roles
```bash
docker-compose exec web python manage.py init_roles
```

**Esperado:**
```
✓ Rol "admin" creado correctamente
✓ Rol "organizador" creado correctamente
✓ Rol "usuario" creado correctamente

✓ Inicialización de roles completada
```

### Paso 4: Crear superusuario
```bash
docker-compose exec web python manage.py createsuperuser
```

**Ingresa:**
- Username: `admin`
- Email: `admin@example.com`
- Password: `tu_contraseña_segura`
- Repeat password: `tu_contraseña_segura`

### Paso 5: Ejecutar la aplicación
```bash
docker-compose up
```

---

## 🌐 Acceso a URLs

| URL | Descripción | Protección |
|-----|-------------|-----------|
| `http://localhost:8000/` | Home | Pública |
| `http://localhost:8000/accounts/login/` | Iniciar sesión | Pública |
| `http://localhost:8000/accounts/registro/` | Registro | Pública |
| `http://localhost:8000/accounts/perfil/` | Mi perfil | Login requerido |
| `http://localhost:8000/accounts/logout/` | Cerrar sesión | Login requerido |
| `http://localhost:8000/admin/` | Panel Django | Login + Admin |

---

## 💻 Primeras Pruebas

### Test 1: Registro
1. Ve a http://localhost:8000/accounts/registro/
2. Completa el formulario:
   - Nombre: Juan
   - Apellido: Pérez
   - Usuario: juanperez
   - Email: juan@example.com
   - Contraseña: MiContraseña123
3. Haz clic en "Registrarse"
4. Te redirigirá a login

### Test 2: Login
1. Ve a http://localhost:8000/accounts/login/
2. Ingresa:
   - Usuario: juanperez
   - Contraseña: MiContraseña123
3. Haz clic en "Iniciar Sesión"
4. La barra de navegación mostrará tu nombre

### Test 3: Perfil
1. Después de loguearte, haz clic en tu nombre en la barra
2. Selecciona "Mi Perfil"
3. Deberías ver toda tu información

### Test 4: Logout
1. En tu perfil, haz clic en "Cerrar Sesión"
2. Serás redirigido al home

---

## 📂 Estructura de Archivos Creados

```
apps/accounts/
├── models.py                      # Modelos Usuario y Rol
├── views.py                       # Vistas de autenticación
├── forms.py                       # LoginForm y RegistroForm
├── urls.py                        # URLs de accounts
├── admin.py                       # Admin personalizado
├── apps.py                        # Configuración
├── decorators.py                  # @require_rol, @require_rols
├── migrations/
│   └── 0001_initial.py           # Migraciones iniciales
├── templates/accounts/
│   ├── login.html                # Formulario de login
│   ├── registro.html             # Formulario de registro
│   └── perfil.html               # Página de perfil
└── management/commands/
    └── init_roles.py             # Comando para crear roles

config/
├── settings.py                    # ✓ Actualizado con AUTH_USER_MODEL
├── urls.py                        # ✓ Actualizado con accounts/urls

templates/
└── base.html                      # ✓ Actualizado con navbar
```

---

## 🔐 Usándolo en Tus Vistas

### Proteger con login
```python
from django.contrib.auth.decorators import login_required

@login_required(login_url='accounts:login')
def mi_vista(request):
    return render(request, 'template.html')
```

### Proteger por rol
```python
from apps.accounts.decorators import require_rol

@require_rol('organizador')
def crear_evento(request):
    return render(request, 'evento.html')
```

### En templates
```django
{% if user.is_authenticated %}
    Hola {{ user.get_full_name }}!
    {% if user.es_admin %}
        <a href="{% url 'admin:dashboard' %}">Panel</a>
    {% endif %}
{% else %}
    <a href="{% url 'accounts:login' %}">Inicia sesión</a>
{% endif %}
```

---

## 📚 Documentación Adicional

Consulta estos archivos para más información:

1. **`AUTENTICACION.md`** - Documentación completa del sistema
2. **`EJEMPLOS_AUTENTICACION.md`** - Ejemplos prácticos de uso
3. **`apps/accounts/models.py`** - Definición de modelos
4. **`apps/accounts/decorators.py`** - Decoradores disponibles

---

## ✨ Próximas Mejoras (Opcionales)

- [ ] Recuperación de contraseña por email
- [ ] Verificación de email al registrarse
- [ ] Cambio de contraseña seguro
- [ ] Autenticación de dos factores (2FA)
- [ ] Social login (Google, Facebook)
- [ ] Permisos granulares por entidad
- [ ] Auditoría de actividad de usuarios

---

## 🆘 Troubleshooting

### Error: "AUTH_USER_MODEL is not defined"
✓ Ya está configurado en settings.py

### Error: "No such table: accounts_usuario"
→ Ejecuta: `docker-compose exec web python manage.py migrate`

### Error: "Rol does not exist"
→ Ejecuta: `docker-compose exec web python manage.py init_roles`

### Login no funciona
→ Verifica que la ruta sea correcta: `/accounts/login/`

---

## 📞 Soporte

Si necesitas ayuda, consulta:
- Django Docs: https://docs.djangoproject.com/
- Decoradores: `apps/accounts/decorators.py`
- Ejemplos: `EJEMPLOS_AUTENTICACION.md`

---

**¡Listo para usar tu sistema de autenticación! 🎉**
