# Espía de Facturas

Captura datos de facturas desde un formulario web y los exporta a Excel.

## Requisitos

- Ubuntu
- Brave Browser
- Python 3.10+
- Brave abierto con `--remote-debugging-port=9222`

## Instalación

1. Instalar Brave (si no lo tenés):
   Ver instrucciones en https://brave.com/linux/

2. Crear entorno virtual e instalar dependencias:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt