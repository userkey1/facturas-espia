# -*- coding: utf-8 -*-
"""
Espía principal: se conecta a Brave ya abierto y captura datos
con Ctrl+S, botón flotante, o al hacer click en Guardar.
"""

import json
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from .config import (
    DEBUGGER_ADDRESS, BOTON_ID, INTERVALO, LOG_PATH
)
from .excel import guardar_en_excel


# ============================================================
# JAVASCRIPT: listener que se inyecta en la página
# ============================================================
JS_LISTENER = """
(function() {
    if (window.__espia_instalado__) return;
    window.__espia_instalado__ = true;

    // -------- Función que captura los datos --------
    function capturarDatos(origen) {
        const datos = {
            fecha_emision:    (document.getElementById('Fecha') || {}).value || '',
            periodo:          (document.getElementById('Periodo') || {}).value || '',
            sucursal:         (document.getElementById('CodSucursal') || {}).value || '',
            nro_comprobante:  (document.getElementById('NroComprobante') || {}).value || '',
            importe_total:    (document.getElementById('ImporteBruto') || {}).value || '',
            tipo_comprobante: (document.querySelector('div.bootstrap-select.IdTipoComprobante span.filter-option') || {}).textContent || '',
            proveedor:        (document.querySelector('div.bootstrap-select.Entidad span.filter-option') || {}).textContent || '',
            origen:           origen || 'manual',
            timestamp:        new Date().toISOString(),
        };

        let div = document.getElementById('__espia_datos__');
        if (!div) {
            div = document.createElement('div');
            div.id = '__espia_datos__';
            div.style.display = 'none';
            document.body.appendChild(div);
        }
        div.textContent = JSON.stringify(datos);

        // Feedback visual
        mostrarToast('📸 Datos capturados');
    }

    // -------- Toast de confirmación --------
    function mostrarToast(msg) {
        let t = document.getElementById('__espia_toast__');
        if (!t) {
            t = document.createElement('div');
            t.id = '__espia_toast__';
            t.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 99999;
                background: #4472C4;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-family: sans-serif;
                font-size: 14px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                transition: opacity 0.3s;
                opacity: 1;
            `;
            document.body.appendChild(t);
        }
        t.textContent = msg;
        t.style.opacity = '1';
        clearTimeout(window.__espia_toast_timeout__);
        window.__espia_toast_timeout__ = setTimeout(() => {
            t.style.opacity = '0';
        }, 2000);
    }

    // -------- 1. Ctrl+S --------
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            capturarDatos('ctrl+s');
        }
    });

    // -------- 2. Botón flotante --------
    function crearBoton() {
        if (document.getElementById('__espia_btn__')) return;
        const btn = document.createElement('button');
        btn.id = '__espia_btn__';
        btn.textContent = '📸 Capturar';
        btn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 99999;
            padding: 10px 20px;
            background: #4472C4;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-family: sans-serif;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        `;
        btn.onclick = () => capturarDatos('boton');
        document.body.appendChild(btn);
    }

    // El botón se recrea cuando cambia el DOM (por si el form se recarga)
    crearBoton();
    new MutationObserver(crearBoton).observe(document.body, { childList: true });

    // -------- 3. Interceptar Guardar (con confirmación) --------
    document.addEventListener('click', function(e) {
        const boton = e.target.closest('#%BOTON_ID%');
        if (!boton) return;

        // Capturamos SIEMPRE
        capturarDatos('click-guardar');

        // Preguntamos si querés enviar
        // Si el navegador no tiene red o querés solo probar, decís NO
        const enviar = confirm('¿Enviar la factura al sistema?\\n\\nAceptar = enviar\\nCancelar = solo capturar');
        if (!enviar) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            return false;
        }
    }, true);  // true = captura antes que el sistema

})();
""".replace("%BOTON_ID%", BOTON_ID)


def conectar_a_brave():
    """Se conecta al Brave que ya está abierto con --remote-debugging-port."""
    options = Options()
    options.add_experimental_option("debuggerAddress", DEBUGGER_ADDRESS)
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def log_error(mensaje: str):
    """Escribe una línea en el log de errores."""
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} | {mensaje}\n")


def inyectar_listener(driver):
    """Inyecta el listener JS en todas las pestañas que tengan el formulario."""
    inyectadas = 0
    for handle in driver.window_handles:
        try:
            driver.switch_to.window(handle)
            ya = driver.execute_script("return !!window.__espia_instalado__;")
            if ya:
                continue
            # Solo inyectamos si estamos en una página con el form
            if not driver.find_elements("id", "Fecha"):
                continue
            driver.execute_script(JS_LISTENER)
            inyectadas += 1
        except Exception as e:
            log_error(f"Error inyectando en pestaña: {e}")
    return inyectadas


def leer_datos_capturados(driver):
    """Lee el JSON del div oculto si existe. Devuelve dict o None."""
    try:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            txt = driver.execute_script(
                "return (document.getElementById('__espia_datos__') || {}).textContent || '';"
            )
            if txt:
                # Resetear para no procesar dos veces
                driver.execute_script(
                    "document.getElementById('__espia_datos__').textContent = '';"
                )
                return json.loads(txt)
    except Exception:
        pass
    return None


def run():
    """Loop principal del espía."""
    print("🔌 Conectando a Brave...")
    try:
        driver = conectar_a_brave()
    except Exception as e:
        print(f"❌ No se pudo conectar a Brave: {e}")
        print("   Asegurate de abrir Brave con:")
        print("   brave-browser --remote-debugging-port=9222")
        return

    print("✅ Conectado.")
    print(f"   Pestañas abiertas: {len(driver.window_handles)}")
    print("   📸 Formas de capturar:")
    print("      - Ctrl+S")
    print("      - Botón flotante '📸 Capturar' (esquina inferior derecha)")
    print("      - Click en Guardar (pregunta si enviar o no)")
    print("   Ctrl+C para salir.\n")

    try:
        while True:
            try:
                # Reinyectar listener si hace falta
                inyectar_listener(driver)

                # ¿Hay datos capturados?
                datos = leer_datos_capturados(driver)
                if datos:
                    datos.pop("timestamp", None)
                    origen = datos.pop("origen", "?")
                    datos["fecha_captura"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    print(f"🎯 Captura ({origen}):")
                    for k, v in datos.items():
                        print(f"   {k}: {v}")

                    guardar_en_excel(datos)
                    print(f"   💾 Guardado en el Excel\n")

                time.sleep(INTERVALO)

            except Exception as e:
                log_error(f"Error en loop: {e}")
                time.sleep(INTERVALO)

    except KeyboardInterrupt:
        print("\n👋 Cerrando espía...")
    finally:
        try:
            driver.service.stop()
        except Exception:
            pass