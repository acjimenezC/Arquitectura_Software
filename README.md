### TicketFisher

Plataforma de gestión de eventos y tickets desarrollada en Python Django. El proyecto está configurado por defecto para SQLite local (`db.sqlite3`).

**Desarrollado por:**
- Anyela Jimenez
- Jeronimo Restrepo
- Sofia Vélez

---

# 🚀 Guía de Instalación y Ejecución

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.11+ (si ejecutas localmente)
- Git
- PostgreSQL (opcional, solo si decides configurar el proyecto para usar PostgreSQL)

---

## Opción 1: Usar Docker Compose (Recomendado) ⭐
 Debes tener docker desktop descargado y abierto.


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

Nota: el proyecto está configurado por defecto para usar SQLite local (`db.sqlite3`). Si quieres usar PostgreSQL, cambia la configuración de `DATABASES` en `config/settings.py`.

### 3. Crear las migraciones
```bash
docker-compose exec -T web python manage.py makemigrations
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
- **Explorar Eventos**: [http://localhost:8000/eventos/](http://localhost:8000/eventos/)
- **Panel Admin**: [http://localhost:8000/admin](http://localhost:8000/admin)

---

### 🛑 Detener los contenedores

```bash
docker-compose down
```

Para eliminar los volúmenes (Base de datos):
```bash
docker-compose down -v
```


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
El proyecto usa SQLite por defecto en `db.sqlite3`, por lo que no es necesario editar `config/settings.py` para ejecutarlo localmente.

Si deseas usar PostgreSQL local o con Docker, actualiza `DATABASES` en `config/settings.py` y asegúrate de apuntar al servicio `db` definido en `docker-compose.yml`.

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

## 🎫 Búsqueda y categorías

- El sitio principal permite buscar eventos por texto (`q`) y filtrar por fecha o lugar.
- Las categorías en la página de inicio (`Empresariales`, `Conciertos`, `Deportes`, `Festivales`) envían al listado de eventos filtrado por categoría.
- La creación de eventos ahora incluye el campo `Categoría`.
- La página de inicio muestra los 3 eventos activos más recientes como “Eventos Destacados”.
- El botón `Ver todos` en la página de inicio redirige a `/user/eventos/`, donde se muestran todos los eventos disponibles.

---

## 📌 URLs Principales

| URL | Descripción |
|-----|-------------|
| `/` | Página de inicio |
| `/accounts/login/` | Iniciar sesión |
| `/accounts/registro/` | Registro de usuarios |
| `/accounts/perfil/` | Mi perfil |
| `/user/eventos/` | Ver todos los eventos disponibles |
| `/eventos/crear_evento/` | Crear nuevo evento (Organizadores/Admin) |
| `/eventos/mis-eventos/` | Ver mis eventos (Organizadores/Admin) |
| `/eventos/?categoria=Conciertos` | Filtrar eventos por categoría |
| `/eventos/?q=<termino>` | Buscar eventos por nombre, descripción o lugar |
| `/organizer/events/` | Panel de organizador con eventos propios y estadísticas |
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



### Error: "psycopg2 no se puede instalar"
En Windows, es mejor usar la versión binaria:

```bash
pip install psycopg2-binary
```



### Error: "Conexión a PostgreSQL rechazada"
Verifica que PostgreSQL esté ejecutándose o usa Docker que lo maneja automáticamente.

---

## Recomendación

**Usa Docker Compose (Opción 1)** - Es la forma más sencilla porque:
- No necesitas configurar PostgreSQL manualmente
- Evitas problemas de dependencias
- El proyecto corre igual en cualquier máquina
- Solo necesitas Docker Desktop instalado

---

## 📚 Documentación Adicional

- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)


