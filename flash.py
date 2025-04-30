import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By

# === CONFIGURACIÓN DEL USUARIO ===
NOMBRE_CONTACTO = "Vóleibol RedCUPS 🏐"  # Nombre exacto del grupo

# Lista de formularios a enviar con distintos datos
FORMULARIOS = [
    {"nombre": "Oscar Soto", "carne": "2020092336", "carrera": "Ingeniería en Computadores"},
    {"nombre": "Esteban Sixtin", "carne": "2020219753", "carrera": "Mantenimiento Industrial"},
]

# Expresión regular para detectar formularios
FORM_REGEX = r'https://(?:docs\.google\.com/forms/|forms\.gle)/[^\s]+'

# Iniciar navegador
driver = webdriver.Chrome()
driver.get("https://web.whatsapp.com/")
print("🔒 Escanea el código QR para iniciar sesión...")

input("✅ Presiona Enter cuando hayas iniciado sesión y WhatsApp Web esté completamente cargado...")

# === Funciones ===

def seleccionar_chat(nombre_contacto):
    try:
        for _ in range(5):  # Scrolls para buscar chat
            try:
                contacto = driver.find_element(By.XPATH, f'//span[@title="{nombre_contacto}"]')
                contacto.click()
                print(f"📨 Chat con '{nombre_contacto}' abierto.")
                return True
            except:
                panel_chats = driver.find_element(By.XPATH, '//div[@aria-label="Lista de chats"]')
                driver.execute_script("arguments[0].scrollTop += 300", panel_chats)
                time.sleep(0.5)

        # Búsqueda si no aparece visible
        buscar = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
        buscar.click()
        time.sleep(1)
        buscar.clear()
        buscar.send_keys(nombre_contacto)
        time.sleep(2)

        contacto = driver.find_element(By.XPATH, f'//span[@title="{nombre_contacto}"]')
        contacto.click()
        print(f"📨 Chat con '{nombre_contacto}' abierto desde búsqueda.")
        return True

    except Exception as e:
        print(f"❌ No se pudo abrir el chat: {e}")
        return False

def esperar_formulario(timeout=300):
    print("⏳ Esperando mensaje con Google Form...")
    inicio = time.time()
    vistos = set()

    while True:
        mensajes = driver.find_elements(By.XPATH, '//div[contains(@class, "message-in")]')
        ultimos = mensajes[-10:]

        for mensaje in reversed(ultimos):
            try:
                mensaje_id = mensaje.get_attribute("data-id") or mensaje.id
                if mensaje_id in vistos:
                    continue
                vistos.add(mensaje_id)

                texto = mensaje.get_attribute("innerText")
                match = re.search(FORM_REGEX, texto)
                if match:
                    form_url = match.group()
                    print(f"✅ ¡Formulario encontrado!: {form_url}")
                    return form_url
            except:
                continue

        time.sleep(0.3)

    print("⌛ Tiempo agotado sin encontrar formulario.")
    return None

def rellenar_formulario(nombre, carne, carrera):
    print(f"📝 Rellenando formulario para {nombre}...")

    try:
        time.sleep(0.5)
        campos = driver.find_elements(By.XPATH, '//input[@type="text"]')
        if len(campos) < 3:
            print("❌ No se encontraron suficientes campos.")
            return

        campos[0].send_keys(nombre)
        campos[1].send_keys(carne)
        campos[2].send_keys(carrera)
        print("✅ Campos completados.")

        boton_enviar = driver.find_element(By.XPATH, '//span[contains(text(), "Enviar") or contains(text(), "Submit")]/ancestor::div[@role="button"]')
        boton_enviar.click()
        print("📤 Formulario enviado.")
        time.sleep(0.3)

    except Exception as e:
        print(f"❌ Error al rellenar o enviar: {e}")

def click_enviar_otro():
    try:
        # Buscar botón en español o inglés
        boton_otro = driver.find_element(By.XPATH, '//a[contains(text(), "Enviar otra respuesta") or contains(text(), "Submit another response")]')
        boton_otro.click()
        print("🔁 Preparado para siguiente respuesta.")
        return True
    except Exception as e:
        print(f"❌ No se encontró botón 'Enviar otra respuesta': {e}")
        return False

# === Ejecución principal ===

if seleccionar_chat(NOMBRE_CONTACTO):
    form_link = esperar_formulario()
    if form_link:
        # Abrir el formulario una sola vez
        driver.execute_script(f"window.open('{form_link}');")
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[-1])

        for i, datos in enumerate(FORMULARIOS):
            rellenar_formulario(datos["nombre"], datos["carne"], datos["carrera"])
            if i < len(FORMULARIOS) - 1:
                if not click_enviar_otro():
                    break

        # Cerrar pestaña del formulario y volver a WhatsApp
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
