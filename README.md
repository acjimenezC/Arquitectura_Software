### TicketFisher

Plataforma de gestión de eventos y tickets desarrollada en Python Django con base de datos PostgreSQL.

**Desarrollado por:**
- Anyela Jimenez
- Jeronimo Restrepo
- Sofia Velez

---

# 🚀 Guía de Instalación y Ejecución

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.11+ (si ejecutas localmente)
- PostgreSQL (si no usas Docker)
- Git

---

## Opción 1: Usar Docker Compose (Recomendado) ⭐

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd Arquitectura_Software
```

### 2. Levantar los contenedores
```bash
docker-compose up -d
```

Esto levanta dos contenedores:
- **django_app**: Aplicación Django en puerto 8000
- **postgres_db**: Base de datos PostgreSQL en puerto 5432

### 3. Crear las migraciones
```bash
docker-compose exec -T web python manage.py makemigrations accounts
```

### 4. Aplicar las migraciones
```bash
docker-compose exec -T web python manage.py migrate
```

### 5. Inicializar los roles
```bash
docker-compose exec -T web python manage.py init_roles
```

**Resultado esperado:**
```
⚠ Rol "admin" ya existe
⚠ Rol "organizador" ya existe
⚠ Rol "usuario" ya existe

✓ Inicialización de roles completada
```

### 6. Crear un superusuario (admin)
```bash
docker-compose exec web python manage.py createsuperuser
```

Ingresa:
- **Username**: `admin`
- **Email**: `admin@example.com`
- **Password**: Tu contraseña segura

### 7. ¡Listo! Accede a la aplicación
- **Aplicación**: [http://localhost:8000](http://localhost:8000)
- **Panel Admin**: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## Opción 2: Entorno Virtual Local (sin Docker)

### 1. Crear el entorno virtual
```bash
cd Arquitectura_Software
python -m venv venv
```

### 2. Activar el entorno virtual
```bash
# En PowerShell
venv\Scripts\Activate.ps1

# O en CMD
venv\Scripts\activate.bat
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos
Edita `config/settings.py` y actualiza:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ticker_fisher',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Inicializar roles
```bash
python manage.py init_roles
```

### 7. Crear superusuario
```bash
python manage.py createsuperuser
```

### 8. Ejecutar el servidor
```bash
python manage.py runserver
```

La app estará disponible en: **http://localhost:8000**

---

## 🔑 Roles y Permisos

| Rol | Permisos | Acceso |
|-----|----------|--------|
| **Admin** | Acceso total al sistema | Panel de administración |
| **Organizador** | Crear y gestionar eventos | Mis eventos, crear eventos |
| **Usuario** | Ver eventos y comprar tickets | Ver eventos disponibles |

---

## 📌 URLs Principales

| URL | Descripción |
|-----|-------------|
| `/` | Página de inicio |
| `/accounts/login/` | Iniciar sesión |
| `/accounts/registro/` | Registro de usuarios |
| `/accounts/perfil/` | Mi perfil |
| `/eventos/crear/` | Crear nuevo evento (Organizadores/Admin) |
| `/eventos/mis-eventos/` | Ver mis eventos (Organizadores/Admin) |
| `/admin/` | Panel de administración Django |

---

## 🗂️ Estructura del Proyecto

```
Arquitectura_Software/
├── apps/
│   ├── accounts/         # Autenticación y usuarios
│   ├── events/          # Gestión de eventos
│   ├── tickets/         # Sistema de tickets
│   ├── organizer/       # Panel organizador
│   ├── end_user/        # Panel usuario final
│   ├── panel_admin/     # Panel administrativo
│   └── access/          # Control de acceso
├── config/              # Configuración Django
├── templates/           # Templates globales
├── static/              # CSS, JS, imágenes
├── manage.py            
├── docker-compose.yml   
├── dockerfile           
└── requirements.txt     
```

---

## 🛑 Detener los contenedores

```bash
docker-compose down
```

Para eliminar los volúmenes (Base de datos):
```bash
docker-compose down -v
```

---

## 🐛 Solución de Problemas

### El servidor no inicia
```bash
# Verificar que los contenedores estén corriendo
docker-compose ps

# Ver los logs
docker-compose logs web
```

### Error de conexión a BD
```bash
# Reiniciar los contenedores
docker-compose restart

# O recrearlos
docker-compose down
docker-compose up -d
```

### Limpiar completamente
```bash
docker-compose down -v
docker-compose up -d
docker-compose exec -T web python manage.py migrate
docker-compose exec -T web python manage.py init_roles
```

---

## 📚 Documentación Adicional

- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)



---

## Opción 2: Con Docker Compose (Recomendado)

### 1. Instalar Docker Desktop
- Descarga desde: https://www.docker.com/products/docker-desktop
- Instala y abre Docker Desktop

### 2. Ejecutar con Docker Compose
```bash
cd c:\Users\USUARIO\Desktop\Ticker_fisher
docker-compose up --build
```

Este comando:
- Construye la imagen Docker
- Crea los contenedores de Django y PostgreSQL
- Inicia ambos servicios automáticamente

### 3. Acceder a la aplicación
- **App Django:** http://localhost:8000
- **Base de datos PostgreSQL:** localhost:5432
  - Usuario: django_user
  - Contraseña: django_pass
  - Base de datos: django_db

### 4. Para parar los contenedores
```bash
docker-compose down
```

### 5. Para ver los logs en tiempo real
```bash
docker-compose logs -f
```

### 6. Para ejecutar comandos dentro del contenedor
```bash
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py migrate
```

---

## Requisitos Previos



### Para  (Docker):
- Docker Desktop instalado
- (No necesitas nada más instalado localmente)

---

## Solución de Problemas

### Error: "psycopg2 no se puede instalar"
En Windows, es mejor usar la versión binaria:
```bash
pip install psycopg2-binary
```

```

### Error: "Conexión a PostgreSQL rechazada"
Verifica que PostgreSQL esté ejecutándose o usa Docker que lo maneja automáticamente.

---

## Recomendación

**Usa Docker Compose (Opción 2)** - Es la forma más sencilla porque:
- No necesitas configurar PostgreSQL manualmente
- Evitas problemas de dependencias
- El proyecto corre igual en cualquier máquina
- Solo necesitas Docker Desktop instalado

---

## URLs principales del proyecto

- Panel de Administración: http://localhost:8000/admin/
- Panel Admin Custom: http://localhost:8000/admin/panel/
- Validación de Acceso: http://localhost:8000/access/
- Sección Organizador: http://localhost:8000/organizer/
- Usuario Asistente: http://localhost:8000/user/
