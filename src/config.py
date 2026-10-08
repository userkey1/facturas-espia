# -*- coding: utf-8 -*-
"""
Configuración central del espía de facturas.
Todos los IDs y rutas en un solo lugar para fácil ajuste.
"""

import os
from pathlib import Path

# ============================================================
# RUTAS
# ============================================================
# Base del proyecto (donde está main.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Excel destino en el escritorio de Ubuntu
EXCEL_PATH = Path.home() / "Escritorio" / "facturas.xlsx"

# Alternativa si tu escritorio está en inglés:
# EXCEL_PATH = Path.home() / "Desktop" / "facturas.xlsx"

# Log de errores
LOG_PATH = BASE_DIR / "errores.log"


# ============================================================
# CONEXIÓN AL NAVEGADOR
# ============================================================
# Brave con debugging remoto
DEBUGGER_ADDRESS = "127.0.0.1:9222"

# ¿Qué botón escuchamos?
BOTON_ID = "guardarFacturaRecibida"

# Intervalo de chequeo (segundos)
INTERVALO = 0.5


# ============================================================
# SELECTORES DE CAMPOS  ← AJUSTÁ SI CAMBIA EL SISTEMA
# ============================================================

# Campos con id simple (se leen con get_attribute("value"))
CAMPOS_INPUT = {
    "fecha_emision":   "Fecha",
    "periodo":         "Periodo",
    "sucursal":        "CodSucursal",
    "nro_comprobante": "NroComprobante",
    "importe_total":   "ImporteBruto",
}

# Campos tipo Bootstrap Select (se leen con .text del span.filter-option)
CAMPOS_SELECT = {
    "tipo_comprobante": "IdTipoComprobante",
    "proveedor":        "Entidad",
}


# ============================================================
# COLUMNAS DEL EXCEL (orden final)
# ============================================================
COLUMNAS_EXCEL = [
    "fecha_captura",
    "fecha_emision",
    "periodo",
    "sucursal",
    "nro_comprobante",
    "importe_total",
    "tipo_comprobante",
    "proveedor",
]