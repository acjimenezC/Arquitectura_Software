# 📋 Sistema de Autenticación - Ticker Fisher

## ✅ Tareas Completadas

Este documento detalla la implementación completa del sistema de autenticación con soporte para roles y protección de vistas.

---

## 1️⃣ App Accounts Creada

Se ha creado la aplicación `apps/accounts` con la siguiente estructura:

```
apps/accounts/
├── models.py              # Modelos de Usuario y Rol
├── views.py               # Vistas de autenticación
├── forms.py               # Formularios de login y registro
├── urls.py                # URLs de la app
├── admin.py               # Admin site personalizado
├── apps.py                # Configuración de la app
├── decorators.py          # Decoradores para proteger vistas
├── templates/accounts/    # Templates HTML
│   ├── login.html
│   ├── registro.html
│   └── perfil.html
└── management/commands/
    └── init_roles.py      # Comando para inicializar roles
```

---

## 2️⃣ Modelos Definidos

### `Rol`
Define los roles disponibles en el sistema:
- **admin**: Administrador del sistema
- **organizador**: Organizador de eventos
- **usuario**: Usuario final (asistente)

```python
class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    permisos = models.JSONField(default=dict, blank=True)
    activo = models.BooleanField(default=True)
```

### `Usuario`
Extiende el modelo de Usuario de Django:
```python
class Usuario(AbstractUser):
    rol = models.ForeignKey(Rol, ...)
    telefono = models.CharField(max_length=20, blank=True)
    cedula = models.CharField(max_length=20, unique=True, blank=True)
    genero = models.CharField(...)
    activo = models.BooleanField(default=True)
    verificado = models.BooleanField(default=False)
    foto_perfil = models.ImageField(...)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultimo_acceso = models.DateTimeField(null=True)
```

**Métodos útiles:**
- `es_admin()`: Verifica si es administrador
- `es_organizador()`: Verifica si es organizador
- `es_usuario()`: Verifica si es usuario final

---

## 3️⃣ Vistas Implementadas

### Login (`/accounts/login/`)
```python
def login_view(request):
    # Autentica al usuario
    # Actualiza último_acceso
    # Redirige según su rol
```

### Logout (`/accounts/logout/`)
```python
def logout_view(request):
    # Cierra la sesión
    # Redirige a home
```

### Registro (`/accounts/registro/`)
```python
def registro_view(request):
    # Crea nuevo usuario
    # Asigna rol 'usuario' por defecto
```

### Perfil (`/accounts/perfil/`)
```python
@login_required(login_url='accounts:login')
def perfil_view(request):
    # Muestra información del usuario
```

---

## 4️⃣ Formas de Proteger Vistas

### Con decorador `@login_required`
```python
from django.contrib.auth.decorators import login_required

@login_required(login_url='accounts:login')
def mi_vista(request):
    # Solo usuarios autenticados pueden acceder
    return render(request, 'template.html')
```

### Con decorador personalizado `@require_rol`
```python
from apps.accounts.decorators import require_rol

@require_rol('admin')
def vista_admin(request):
    # Solo administradores pueden acceder
    return render(request, 'admin.html')
```

### Con múltiples roles
```python
from apps.accounts.decorators import require_rols

@require_rols('admin', 'organizador')
def vista_admin_org(request):
    # Solo admin u organizador pueden acceder
    return render(request, 'eventos.html')
```

### Verificar usuario activo
```python
from apps.accounts.decorators import require_activo

@require_activo
@login_required(login_url='accounts:login')
def vista_usuario_activo(request):
    # Usuario debe estar autenticado y activo
    return render(request, 'template.html')
```

---

## 5️⃣ Manejo de Sesiones

Configurado en `settings.py`:

```python
# Almacenamiento de sesiones en BD
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Duración de sesión (2 semanas)
SESSION_COOKIE_AGE = 1209600

# Seguridad
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # True en producción
SESSION_COOKIE_SAMESITE = 'Lax'
```

**Acceder a sesiones en vistas:**
```python
def mi_vista(request):
    if request.user.is_authenticated:
        usuario = request.user
        # Acceder a datos del usuario
        nombre = usuario.get_full_name()
        rol = usuario.rol.nombre
```

---

## 🚀 Cómo Usar

### 1. Crear migraciones
```bash
docker-compose exec web python manage.py makemigrations accounts
docker-compose exec web python manage.py migrate
```

### 2. Inicializar roles
```bash
docker-compose exec web python manage.py init_roles
```

Resultado:
```
✓ Rol "admin" creado correctamente
✓ Rol "organizador" creado correctamente
✓ Rol "usuario" creado correctamente

✓ Inicialización de roles completada
```

### 3. Crear superusuario
```bash
docker-compose exec web python manage.py createsuperuser
```

### 4. Acceder a las vistas
- **Login**: http://localhost:8000/accounts/login/
- **Registro**: http://localhost:8000/accounts/registro/
- **Perfil**: http://localhost:8000/accounts/perfil/
- **Admin**: http://localhost:8000/admin/

---

## 📖 Ejemplos en Templates

### Mostrar contenido solo autenticados
```django
{% if user.is_authenticated %}
    <p>Hola {{ user.get_full_name }}!</p>
{% else %}
    <a href="{% url 'accounts:login' %}">Inicia sesión</a>
{% endif %}
```

### Mostrar por rol
```django
{% if user.es_admin %}
    <a href="{% url 'panel_admin:dashboard' %}">Panel Admin</a>
{% elif user.es_organizador %}
    <a href="{% url 'organizador:eventos' %}">Mis Eventos</a>
{% else %}
    <a href="{% url 'end_user:eventos' %}">Eventos</a>
{% endif %}
```

### Información del usuario
```django
<p>Rol: {{ user.rol.nombre }}</p>
<p>Email: {{ user.email }}</p>
<p>Teléfono: {{ user.telefono }}</p>
{% if user.verificado %}
    ✓ Email verificado
{% endif %}
```

---

## 🔐 Seguridad Implementada

✅ Contraseñas hasheadas (PBKDF2)
✅ CSRF protection en formularios
✅ HttpOnly cookies para sesiones
✅ Control de usuarios activos/inactivos
✅ Sistema de roles flexible
✅ Validación de permisos en vistas

---

## 📝 Notas Importantes

1. **AUTH_USER_MODEL** en settings.py apunta a `accounts.Usuario`
2. Las sesiones se almacenan en la BD (más seguro que cookies)
3. El último acceso se actualiza en cada login
4. Los nuevos usuarios se asignan el rol 'usuario' por defecto
5. El decorador `@require_rol` incluye automáticamente `@login_required`

---

## 🔗 URLs Disponibles

| URL | Vista | Protección |
|-----|-------|-----------|
| `/accounts/login/` | login_view | Pública |
| `/accounts/logout/` | logout_view | Login requerido |
| `/accounts/registro/` | registro_view | Pública |
| `/accounts/perfil/` | perfil_view | Login requerido |

---

## ✨ Próximos Pasos (Opcional)

- [ ] Implementar recuperación de contraseña
- [ ] Verificación de email
- [ ] Autenticación de dos factores
- [ ] Social login (Google, GitHub)
- [ ] Permisos granulares por entidad
