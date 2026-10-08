# -*- coding: utf-8 -*-
"""
Funciones para leer los campos del formulario web.
"""

from datetime import datetime
from selenium.webdriver.common.by import By

from .config import CAMPOS_INPUT, CAMPOS_SELECT


def leer_input(driver, id_campo):
    """Lee el value de un <input> por id. Devuelve '' si falla."""
    try:
        return driver.find_element(By.ID, id_campo).get_attribute("value") or ""
    except Exception:
        return ""


def leer_select(driver, id_campo):
    """Lee el texto visible de un Bootstrap Select por su id."""
    try:
        return driver.find_element(
            By.CSS_SELECTOR,
            f"div.bootstrap-select.{id_campo} span.filter-option"
        ).text
    except Exception:
        return ""


def capturar_datos(driver) -> dict:
    """
    Captura todos los campos del formulario y devuelve un dict.
    """
    datos = {
        "fecha_captura": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Inputs
    for nombre, id_campo in CAMPOS_INPUT.items():
        datos[nombre] = leer_input(driver, id_campo)

    # Selects
    for nombre, id_campo in CAMPOS_SELECT.items():
        datos[nombre] = leer_select(driver, id_campo)

    return datos