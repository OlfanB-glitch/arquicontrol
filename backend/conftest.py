"""
Configuración raíz de pytest para ArquiControl.

Carga las variables de entorno desde backend/.env y agrega
la carpeta backend al sys.path para que los imports funcionen.
"""

import sys
from pathlib import Path

# Agregar la carpeta backend al path de Python
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Cargar variables de entorno desde .env ANTES de que
# cualquier módulo importe app.core.config.settings
from dotenv import load_dotenv

load_dotenv(backend_dir / ".env")