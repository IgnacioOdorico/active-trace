<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=002045,1a365d,003765&height=200&section=header&text=activia-trace&fontSize=60&fontAlignY=35&fontColor=adc7f7&animation=fadeIn" width="100%" />

<a href="https://readme-typing-svg.demolab.com/demo/">
  <img src="https://readme-typing-svg.demolab.com/?lines=Gesti%C3%B3n+acad%C3%A9mica+multi-tenant;Trazabilidad+y+auditor%C3%ADa+completa;Integraci%C3%B3n+con+Moodle&font=IBM+Plex+Sans&center=true&width=800&height=60&color=002045&vCenter=true&size=22&pause=1000" alt="Typing SVG" />
</a>
</div>

## Demo

<div align="center">
  <a href="https://youtu.be/VJqg8g3Y4zc" target="_blank">
    <img src="https://img.youtube.com/vi/VJqg8g3Y4zc/maxresdefault.jpg" alt="Demo Video" width="600" style="border-radius: 8px; border: 1px solid #c4c6cf;" onerror="this.src='https://img.youtube.com/vi/VJqg8g3Y4zc/hqdefault.jpg'" />
  </a>
  <br /><br />
  <a href="https://youtu.be/VJqg8g3Y4zc" target="_blank">
    <img src="https://img.shields.io/badge/▶_Ver_Demo-FF0000?style=for-the-badge&logo=youtube&logoColor=white&labelColor=CC0000" alt="Ver Demo" />
  </a>
</div>

## Badges

<div align="center">
  <img src="https://img.shields.io/badge/Python_3.13-002045?style=for-the-badge&logo=python&logoColor=adc7f7" />
  <img src="https://img.shields.io/badge/FastAPI-003765?style=for-the-badge&logo=fastapi&logoColor=adc7f7" />
  <img src="https://img.shields.io/badge/React_18-1a365d?style=for-the-badge&logo=react&logoColor=adc7f7" />
  <img src="https://img.shields.io/badge/TypeScript-002045?style=for-the-badge&logo=typescript&logoColor=adc7f7" />
  <img src="https://img.shields.io/badge/PostgreSQL-003765?style=for-the-badge&logo=postgresql&logoColor=adc7f7" />
  <img src="https://img.shields.io/badge/Docker-1a365d?style=for-the-badge&logo=docker&logoColor=adc7f7" />
  <br />
  <img src="https://img.shields.io/badge/license-Proprietary-43474e?style=for-the-badge" />
  <img src="https://img.shields.io/badge/status-Active_Development-2d476f?style=for-the-badge" />
  <img src="https://img.shields.io/badge/coverage-%3E80%25-1a365d?style=for-the-badge" />
</div>

## Tech Icons

<div align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,fastapi,react,ts,vite,tailwind,postgres,docker,githubactions,opentelemetry&perline=10&theme=dark" />
  </a>
</div>

<br />

<details>
<summary><b>📑 Tabla de Contenidos</b></summary>
<br />

- [✨ Features](#-features)
- [🛠 Tech Stack](#-tech-stack)
- [🚀 Instalación](#-instalación)
- [📸 Screenshots](#-screenshots)

</details>



## ✨ Features

### 📊 Ingesta de Datos desde Moodle
- **Importación de calificaciones** por materia desde archivos exportados del LMS, con vista previa y selección de actividades.
- **Importación de padrones** de alumnos y actividades (upsert destructivo).
- **Reporte de finalización** de actividades para detectar entregas sin corregir.
- **Vaciar datos** de una materia sin afectar el resto.

### 📈 Análisis Académico
- **Umbral de aprobación** configurable por materia (default 60%).
- **Detección de alumnos atrasados** con nota inferior al umbral o actividades faltantes.
- **Ranking** de actividades aprobadas por alumno.
- **Reportes rápidos** con métricas clave por materia.
- **Notas finales agrupadas** y exportables.
- **Monitor de seguimiento** con filtros por materia, comisión, alumno y estado.

### 📬 Comunicaciones
- **Composición y vista previa** de mensajes antes del envío.
- **Envío masivo** con cola de estados (Pendiente → En envío → Enviado / Fallido / Cancelado).
- **Aprobación** de envíos masivos por rol con permiso `comunicacion:aprobar`.
- **Bandeja de mensajes** interna con hilos y respuestas.
- **Tablón de avisos** con alcance configurable, severidad, vigencia y confirmación de lectura.

### 👥 Gestión de Equipos Docentes
- **Administración de usuarios** docentes con datos personales, fiscales y bancarios.
- **Asignaciones individuales y masivas** a materias × carrera × cohorte.
- **Clonación de equipos** entre períodos académicos.
- **Exportación** del equipo docente.

### 🏛 Estructura Académica
- Administración de **carreras**, **cohortes** y **programas de materia**.
- Gestión de **fechas de evaluaciones** con vista de calendario.
- Generación de contenido para el aula virtual del LMS.

### 📅 Encuentros y Coloquios
- Creación de **encuentros recurrentes** (semanal) y **únicos**.
- Edición de instancias con enlaces de videoconferencia y grabación.
- **Registro de guardias** de tutores.
- **Coloquios**: convocatorias, reservas, registro de notas y panel de métricas.

### ✅ Tareas Internas
- **Vista de mis tareas** con filtros por contexto académico.
- **Delegación** de tareas entre docentes con trazabilidad.
- **Administración global** con filtros y cambio de estado.

### 💰 Liquidaciones y Honorarios
- **Vista de liquidaciones** del período con detalle por rol, comisiones, salario base y plus.
- **Cierre de liquidación** inmutable.
- **Grilla salarial**: salario base por rol y plus adicionales con vigencia temporal.
- **Gestión de facturas** para docentes que facturan.
- **Historial** de liquidaciones cerradas.

### 🔒 Seguridad y Auditoría
- **Multi-tenancy** con aislamiento completo de datos por institución.
- **Autenticación JWT** con refresh rotation y 2FA opcional (TOTP).
- **RBAC con permisos finos** (`modulo:accion`), sin superusuario binario.
- **Cifrado AES-256** de PII sensible (CBU, DNI, CUIL).
- **Passwords con Argon2id**.
- **Auditoría completa** inmutable y no borrable.
- **Impersonación** controlada y auditada.
- **Panel de auditoría** con gráficos de actividad.

### 👤 Perfil y Sesión
- Edición de perfil propio con datos personales, fiscales y bancarios.
- Recuperación de contraseña con tokens seguros.
- Bandeja de mensajes propia y cierre de sesión.


## 🛠 Tech Stack

### Backend

| Componente | Tecnología |
|------------|-----------|
| Lenguaje | **Python 3.13** |
| Framework | **FastAPI** (API REST async) |
| ORM | **SQLAlchemy 2.0** (async) |
| Migraciones | **Alembic** |
| Base de datos | **PostgreSQL** (con JSONB) |
| Validación | **Pydantic v2** |
| Auth | JWT (access + refresh rotation) + **Argon2id** |
| Cifrado | **AES-256** para PII sensible |
| Background jobs | Worker async (cola de comunicaciones) |
| Testing | **pytest** + coverage (≥80% líneas, ≥90% RN) |
| Observabilidad | **OpenTelemetry** + logs JSON |

### Frontend

| Componente | Tecnología |
|------------|-----------|
| Framework | **React 18** + **TypeScript** |
| Bundler | **Vite** |
| Server state | **TanStack Query** |
| Forms | **React Hook Form** + **Zod** |
| Estilos | **Tailwind CSS** |
| HTTP | **Axios** |
| Routing | **React Router v7** |
| Testing | **Vitest** + **Testing Library** |

### Infraestructura

| Componente | Tecnología |
|------------|-----------|
| Contenedores | **Docker** + docker-compose |
| Deploy | **Easypanel** |
| CI/CD | Build + test + lint automatizado |
| Integraciones | **Moodle Web Services**, **N8N** |


## 🚀 Instalación

### Requisitos
- Docker y Docker Compose
- Node.js 20+ y pnpm (`npm install -g pnpm`)

### 1. Clonar el repo
```bash
git clone https://github.com/IgnacioOdorico/active-trace.git
cd active-trace
```

### 2. Backend (Docker)
```bash
# El backend completo se levanta con Docker
docker compose up --build -d

# Ejecutar migraciones
docker compose exec api alembic upgrade head

# Poblar datos de prueba
docker compose exec api python -m app.core.bootstrap
docker compose exec api python -m app.core.seed_data
```

### 3. Frontend
```bash
cd frontend
pnpm install
pnpm dev
```

### 4. Acceder
| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| Docs API | http://localhost:8000/docs |
| Postgres | localhost:5432 |

### Usuarios de prueba

| Rol | Email | Password |
|-----|-------|----------|
| ADMIN | admin@demo.local | Admin1234! |
| PROFESOR | profesor1@demo.local | Demo1234! |
| COORDINADOR | coordinador1@demo.local | Demo1234! |
| TUTOR | tutor1@demo.local | Demo1234! |
| ALUMNO | alumno1@demo.local | Demo1234! |
| NEXO | nexo1@demo.local | Demo1234! |
| FINANZAS | finanzas1@demo.local | Demo1234! |


## 📸 Screenshots

> *(Grabá tus propios GIFs y pegálos acá)*

<div align="center">

### Panel de Administración

```
[GIF AQUÍ — Navegación por el panel de administración]
```

### Importación de Calificaciones

```
[GIF AQUÍ — Flujo de importación desde Moodle]
```

### Comunicaciones y Avisos

```
[GIF AQUÍ — Envío de comunicaciones y tablón de avisos]
```

### Liquidaciones

```
[GIF AQUÍ — Vista de liquidaciones y grilla salarial]
```

### Panel de Auditoría

```
[GIF AQUÍ — Log de auditoría y métricas de uso]
```

</div>


<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=003765,1a365d,002045&height=150&section=footer&text=activia-trace&fontSize=30&fontAlignY=65&fontColor=adc7f7" width="100%" />
</div>
