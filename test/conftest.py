import pytest

from app import create_app
from app.models import blog_storage

import threading
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture
def app():
    """
    Fixture que crea una instancia de la aplicación para testing

    ¿Qué es un fixture?
    - Función que prepara datos/objetos para las pruebas
    - Se ejecuta antes de cada test que lo necesite
    - Garantiza un estado limpio para cada prueba
    """
    # Crear aplicación en modo testing
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Desactivar CSRF para testing

    return app


@pytest.fixture
def client(app):
    """
    Fixture que crea un cliente de testing para hacer peticiones HTTP

    ¿Para qué sirve?
    - Simula un navegador web
    - Permite hacer GET, POST, PUT, DELETE
    - No necesita servidor real corriendo
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Fixture para testing de comandos CLI (si los tuviéramos)
    """
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def reset_storage():
    """
    Fixture que resetea el almacenamiento antes de cada test

    ¿Por qué autouse=True?
    - Se ejecuta automáticamente antes de cada test
    - Garantiza que cada test empiece con datos limpios
    - Evita que los tests se afecten entre sí
    """
    # Limpiar todos los posts
    blog_storage._posts.clear()
    blog_storage._next_id = 1

    # Recrear posts de ejemplo para tests consistentes
    blog_storage._create_sample_posts()

    yield

    # Cleanup después del test (si fuera necesario)
    pass


@pytest.fixture(scope="session")
def flask_test_app():
    """
    Fixture que inicia una aplicación Flask real para pruebas E2E con Selenium.
    Se ejecuta una sola vez durante toda la sesión de pruebas.
    """
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    def run_app():
        app.run(
            host="127.0.0.1",
            port=5001,
            debug=False,
            use_reloader=False
        )

    server_thread = threading.Thread(target=run_app, daemon=True)
    server_thread.start()

    # Esperar a que el servidor inicie
    time.sleep(3)

    yield app


@pytest.fixture
def selenium_driver():
    """
    Fixture que crea un navegador Chrome en modo headless para pruebas E2E.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Descargar el driver
    driver_path = ChromeDriverManager().install()

    # Corregir bug de webdriver-manager que devuelve THIRD_PARTY_NOTICES
    if "THIRD_PARTY_NOTICES" in driver_path:
        driver_path = str(Path(driver_path).parent / "chromedriver.exe")

    service = Service(driver_path)

    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture
def e2e_base_url():
    """
    URL base utilizada por las pruebas End-to-End.
    """
    return "http://127.0.0.1:5001"