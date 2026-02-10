### TicketFisher

Este es un proyecto para la materia Arquitectura de Software
Desarrollado en python Django con una base de datos Postgress

Realizado por:
- Anyela Jimenez
- Jeronimo Restrepo
- Sofia Velez

# Instrucciones para ejecutar Ticker Fisher

## Opción 1: Entorno Virtual Local (sin Docker)

### 1. Crear el entorno virtual
```bash
cd c:\Users\USUARIO\Desktop\Ticker_fisher
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

### 4. Ejecutar migraciones
```bash
python manage.py migrate
```

### 5. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 6. Ejecutar el servidor
```bash
python manage.py runserver
```

La app estará disponible en: **http://localhost:8000**

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
