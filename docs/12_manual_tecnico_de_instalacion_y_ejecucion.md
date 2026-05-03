# 12. Manual técnico de instalación y ejecución

Este manual describe el procedimiento para instalar y ejecutar ArquiControl en un entorno de desarrollo local sobre Windows 10/11 con Visual Studio Code y MongoDB Atlas como base de datos.

## Requisitos previos

| Componente | Versión | Observación |
|---|---|---|
| Visual Studio Code | última estable | editor recomendado |
| Python | 3.11 o 3.12 | marcar *Add python.exe to PATH* al instalar |
| Node.js | 18 LTS o 20 LTS | instalador oficial desde nodejs.org |
| Yarn | 1.22 o superior | instalar con `npm install -g yarn` |
| Git | última estable | para clonar el repositorio |
| Cuenta de MongoDB Atlas | — | cluster gratuito M0 es suficiente |

## Variables de entorno

### Backend (`backend/.env`)

| Variable | Descripción |
|---|---|
| `MONGO_URL` | cadena de conexión completa de MongoDB Atlas (mongodb+srv://...) |
| `DB_NAME` | nombre de la base dentro del cluster (por ejemplo `arquicontrol`) |
| `CORS_ORIGINS` | orígenes permitidos separados por coma (ej. `http://localhost:3000`) |
| `JWT_SECRET_KEY` | cadena aleatoria larga para firmar los tokens JWT |
| `UPLOADS_DIR` | ruta relativa o absoluta para archivos subidos (ej. `./uploads`) |

Ambos proyectos incluyen un archivo `.env.example` que sirve como plantilla.

### Frontend (`frontend/.env`)

| Variable | Descripción |
|---|---|
| `REACT_APP_BACKEND_URL` | URL base donde responde el backend (ej. `http://localhost:8001`) |

## Configuración de MongoDB Atlas

1. Crear una cuenta gratuita en https://www.mongodb.com/cloud/atlas/register.
2. Crear un proyecto y un cluster M0 gratuito en la región más cercana.
3. En *Security → Database Access* crear un usuario con rol **Read and write to any database**.
4. En *Security → Network Access* permitir la IP de desarrollo (o `0.0.0.0/0` para entorno académico).
5. En *Database → Connect → Drivers → Python* copiar la cadena de conexión y reemplazar `<password>` por la contraseña del usuario creado.
6. Pegar la cadena en `MONGO_URL` dentro de `backend/.env`.

## Instalación de dependencias

### Backend

Desde una terminal de PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Completar los valores de `backend\.env` con los datos reales del cluster de Atlas.

Si PowerShell bloquea la activación del entorno virtual, ejecutar una única vez en una terminal con permisos de administrador:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Frontend

En una segunda terminal de PowerShell:

```powershell
cd frontend
yarn install
copy .env.example .env
```

## Cómo levantar backend y frontend

### Backend

Con el entorno virtual activado:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Verificación: abrir http://localhost:8001/api/health debe retornar `{"status":"ok","service":"ArquiControl API"}`.

### Frontend

```powershell
cd frontend
yarn start
```

El navegador abrirá http://localhost:3000 de forma automática.

### Credenciales iniciales

Después del primer arranque se genera el usuario demo:

- Correo: `admin@arquicontrol.com`
- Contraseña: `ArquiControl2026!`

## Cómo correr pruebas

Con el backend corriendo en `localhost:8001`, desde una tercera terminal:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
$env:REACT_APP_BACKEND_URL="http://localhost:8001"
pytest tests/ -q
```

## Cómo cargar seed data

No existe un comando CLI independiente para carga inicial. La inserción de datos se ejecuta automáticamente en el evento `startup` del backend mediante `seed_initial_data()`.

### Comportamiento real

- Si la colección `usuarios` está vacía, el sistema inserta datos iniciales (1 usuario, 5 clientes, 5 contratistas, 4 proveedores, 6 materiales, 3 proyectos de ejemplo).
- Si ya existe al menos un usuario, el seed no se ejecuta para evitar duplicados.
- Para reiniciar la base: eliminar las colecciones desde Atlas (o desde MongoDB for VS Code) y levantar el backend nuevamente.

## Estructura de carpetas generadas en tiempo de ejecución

- `backend/uploads/` — archivos subidos por los usuarios durante el uso del sistema.
- `backend/venv/` — entorno virtual de Python (ignorado por git).
- `frontend/node_modules/` — dependencias de Node (ignoradas por git).

## Solución de problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `ModuleNotFoundError` al iniciar uvicorn | entorno virtual inactivo | ejecutar `.\venv\Scripts\Activate.ps1` antes de uvicorn |
| `pymongo.errors.ServerSelectionTimeoutError` | IP no autorizada en Atlas | agregar la IP en *Network Access* |
| `Authentication failed` al conectar | usuario o contraseña incorrectos en `MONGO_URL` | verificar *Database Access* y codificar caracteres especiales |
| CORS error en el navegador | `CORS_ORIGINS` no incluye el origen del frontend | agregar `http://localhost:3000` en `backend/.env` |
| Puerto 8001 o 3000 ocupado | otra aplicación lo usa | cerrar la aplicación o cambiar el puerto en el comando de arranque |

## Nota sobre despliegue

Este manual cubre únicamente el entorno de desarrollo local. Un despliegue productivo requeriría pasos adicionales (servidor de aplicaciones, reverse proxy, HTTPS, variables de entorno gestionadas de forma segura) que están fuera del alcance actual del proyecto.
