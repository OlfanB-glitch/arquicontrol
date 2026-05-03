# ArquiControl

Sistema web full-stack para la gestión operativa, documental y financiera de un arquitecto independiente. Centraliza clientes, proyectos, fases, seguimientos, pagos, contratistas, compras, documentos, bitácora operativa y reportes básicos sobre un modelo de datos documental con `proyectos` como agregado raíz.

## Stack tecnológico

- **Frontend:** React 19, React Router, Tailwind CSS, Shadcn/UI, Axios.
- **Backend:** FastAPI, Pydantic, Motor (MongoDB async).
- **Base de datos:** MongoDB Atlas (cluster gratuito M0).
- **Autenticación:** JWT con `python-jose` y `passlib`.
- **Reportes:** PDF con `reportlab`; exportaciones CSV nativas.
- **Pruebas:** `pytest` + `requests`.

## Arquitectura

- **Estilo:** monolito modular.
- **Backend por capas:** `presentation`, `application`, `domain`, `infrastructure`.
- **Patrones implementados:** Repository, Singleton, Strategy, Factory Method, Observer.

## Estructura del proyecto

```text
arquicontrol/
├── backend/
│   ├── app/
│   │   ├── core/          # config, database, security
│   │   ├── modules/       # auth, clientes, proyectos, etc.
│   │   ├── seed/          # datos iniciales
│   │   └── shared/        # catálogos y utilidades
│   ├── tests/
│   ├── server.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   └── .env.example
├── docs/                  # documentación técnica y académica
├── uploads/               # archivos subidos por usuarios (ignorado por git)
└── README.md
```

---

# Guía de instalación en Windows + VS Code

Esta guía asume que estás empezando desde cero en Windows 10/11.

## 1. Herramientas necesarias

Antes de clonar el proyecto instala:

| Herramienta | Versión mínima | Dónde conseguirla |
|---|---|---|
| **Visual Studio Code** | última | https://code.visualstudio.com/ |
| **Python** | 3.11 o 3.12 | https://www.python.org/downloads/ (marca *Add python.exe to PATH* en el instalador) |
| **Node.js** | 18 LTS o 20 LTS | https://nodejs.org/ |
| **Yarn** | 1.22+ | En PowerShell: `npm install -g yarn` |
| **Git** | última | https://git-scm.com/download/win |

### Extensiones recomendadas de VS Code

Abre VS Code, ve a *Extensions* (`Ctrl+Shift+X`) e instala:

- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **ESLint** (Microsoft)
- **Prettier - Code formatter**
- **Tailwind CSS IntelliSense**
- **MongoDB for VS Code** (opcional, útil para inspeccionar la base)

## 2. Crear el cluster de MongoDB Atlas

1. Entra a [https://www.mongodb.com/cloud/atlas/register](https://www.mongodb.com/cloud/atlas/register) y crea una cuenta gratuita.
2. Al iniciar sesión, crea un proyecto nuevo (por ejemplo `ArquiControl`).
3. Dentro del proyecto haz clic en **Build a Database** y elige la opción **M0 Free**.
4. Selecciona un proveedor cercano (AWS · Virginia o São Paulo suele ser lo más rápido desde Colombia) y crea el cluster. La creación tarda 1–3 minutos.
5. **Crear un usuario de base de datos:**
   - En *Security → Database Access* haz clic en **Add New Database User**.
   - Autenticación: **Password**. Elige un usuario (por ejemplo `arquicontrol_app`) y genera una contraseña segura. **Guárdala**, la necesitarás después.
   - Rol: **Read and write to any database**.
6. **Permitir tu IP:**
   - En *Security → Network Access* haz clic en **Add IP Address**.
   - Para desarrollo, elige **Allow Access from Anywhere** (`0.0.0.0/0`). Si prefieres mayor seguridad, usa tu IP actual.
7. **Obtener la cadena de conexión:**
   - Vuelve a *Database → Connect* sobre tu cluster.
   - Elige **Drivers → Python → 3.12 or later**.
   - Copia la cadena que aparece, algo como:
     ```
     mongodb+srv://arquicontrol_app:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
     ```
   - **Reemplaza `<password>`** por la contraseña del usuario que creaste. Si tu contraseña contiene caracteres especiales (`@`, `:`, `/`, etc.), debes codificarlos (por ejemplo `@` → `%40`).

## 3. Clonar y abrir el proyecto

Abre **PowerShell** y navega a la carpeta donde quieras guardar el proyecto:

```powershell
cd C:\Users\TU_USUARIO\Documents
git clone <URL-DE-TU-REPOSITORIO> arquicontrol
cd arquicontrol
code .
```

El último comando abre la carpeta en VS Code.

## 4. Configurar el backend

Abre una terminal dentro de VS Code (``Ctrl+` ``) y ejecuta:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

> **Si PowerShell bloquea la activación del entorno virtual**, ejecuta una sola vez (como administrador):
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

Crea el archivo `.env` copiando el ejemplo:

```powershell
copy .env.example .env
```

Abre `backend\.env` en VS Code y completa:

```env
MONGO_URL=mongodb+srv://arquicontrol_app:TU_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=arquicontrol
CORS_ORIGINS=http://localhost:3000
JWT_SECRET_KEY=pega-aqui-una-cadena-aleatoria-larga
UPLOADS_DIR=./uploads
```

Para generar una clave JWT segura en PowerShell:

```powershell
[Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(48))
```

Copia el resultado y pégalo como valor de `JWT_SECRET_KEY`.

### Levantar el backend

Con el entorno virtual activado y desde la carpeta `backend`:

```powershell
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Verifica que funciona abriendo [http://localhost:8001/api/health](http://localhost:8001/api/health) — deberías ver `{"status":"ok","service":"ArquiControl API"}`.

La primera vez que arranca, el backend ejecuta `seed_initial_data()` y carga automáticamente 1 usuario, 5 clientes, 5 contratistas, 4 proveedores, 6 materiales y 3 proyectos de ejemplo en tu cluster de Atlas.

## 5. Configurar el frontend

Abre una **segunda terminal** en VS Code (deja el backend corriendo en la primera):

```powershell
cd frontend
yarn install
copy .env.example .env
```

Abre `frontend\.env` y confirma que tiene:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Levantar el frontend

```powershell
yarn start
```

El navegador abrirá automáticamente [http://localhost:3000](http://localhost:3000).

## 6. Credenciales de acceso

Después del primer arranque, inicia sesión con:

- **Correo:** `admin@arquicontrol.com`
- **Contraseña:** `ArquiControl2026!`

---

## Ejecutar las pruebas

Con el backend corriendo en `localhost:8001`, en una tercera terminal:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
$env:REACT_APP_BACKEND_URL="http://localhost:8001"
pytest tests/ -q
```

## Comandos útiles del día a día

```powershell
# Activar el entorno virtual del backend
cd backend
.\venv\Scripts\Activate.ps1

# Correr solo el backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Correr solo el frontend
cd frontend
yarn start

# Instalar una nueva dependencia Python
pip install <paquete>
pip freeze > requirements.txt

# Instalar una nueva dependencia de React
cd frontend
yarn add <paquete>
```

## Documentación

La documentación técnica y académica está en [`docs/`](./docs):

- `00_resumen_ejecutivo.md`
- `01_planteamiento_del_problema_y_objetivos.md`
- `02_alcance_del_sistema.md`
- `03_requerimientos_funcionales_y_no_funcionales.md`
- `04_casos_de_uso_del_sistema.md`
- `05_modelo_de_datos_no_relacional.md`
- `06_arquitectura_del_sistema.md`
- `07_patrones_de_diseno_aplicados.md`
- `08_modulos_backend_y_frontend.md`
- `09_api_y_endpoints.md`
- `10_validaciones_y_reglas_de_negocio.md`
- `11_pruebas_realizadas_y_resultados.md`
- `12_manual_tecnico_de_instalacion_y_ejecucion.md`
- `13_manual_de_usuario.md`
- `14_guion_de_demostracion_y_sustentacion.md`
- `15_conclusiones_y_trabajo_futuro.md`

## Solución de problemas comunes

| Problema | Solución |
|---|---|
| `ModuleNotFoundError` al iniciar el backend | Asegúrate de haber activado el entorno virtual (`.\venv\Scripts\Activate.ps1`) antes de ejecutar uvicorn. |
| `pymongo.errors.ServerSelectionTimeoutError` | La IP no está autorizada en Atlas, o la cadena de conexión es incorrecta. Verifica *Network Access* en Atlas. |
| `Authentication failed` al conectar a Atlas | El usuario/contraseña de la cadena de conexión no coincide con el creado en *Database Access*. |
| `CORS error` en el navegador | Revisa que `CORS_ORIGINS` en `backend\.env` incluya `http://localhost:3000`. |
| Puerto 8001 o 3000 ocupado | Cierra la otra aplicación o cambia el puerto (`--port 8002` para uvicorn; `set PORT=3001 && yarn start` para React). |
| `yarn` no se reconoce | Ejecuta `npm install -g yarn` y reinicia PowerShell. |
| Caracteres raros en la contraseña Atlas | Codifica los caracteres especiales en la URL (ej. `@` → `%40`, `#` → `%23`). |
