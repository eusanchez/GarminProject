from pathlib import Path
import json
from playwright.sync_api import sync_playwright

COOKIES_FILE = Path("garmin_cookies.json")

def save_cookies(context):
    cookies = context.cookies()
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f)
    print("✅ Cookies guardadas en", COOKIES_FILE)

def main():
    with sync_playwright() as pw:
        # Lanzamos navegador visible
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context()

        # Nueva página
        page = context.new_page()
        print("🌐 Abriendo Garmin Connect...")
        page.goto("https://connect.garmin.com/")

        print("\n👉 Inicia sesión normalmente en la ventana (correo, clave, 2FA si pide).")
        input("Cuando ya estés dentro de Garmin Connect (ves tu dashboard), vuelve aquí y presiona Enter... ")

        # Guardamos cookies
        save_cookies(context)

        print("🎉 Listo: tu sesión quedó guardada, la próxima vez podemos usar estas cookies.")
        input("Presiona Enter para cerrar el navegador...")

        browser.close()

if __name__ == "__main__":
    main()
