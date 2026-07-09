import pytest

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestBasicE2E:
    """Clase que agrupa tests básicos de End-to-End"""

    def test_homepage_loads(
        self,
        selenium_driver,
        e2e_base_url,
        flask_test_app,
    ):
        """Test E2E: La página principal carga correctamente"""
        selenium_driver.get(e2e_base_url)

        # Verificar que el título de la página sea correcto
        assert "DevBlog" in selenium_driver.title

        try:
            # Esperar hasta que aparezca contenido
            WebDriverWait(selenium_driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Verificar que DevBlog aparece en algún lugar de la página
            assert "DevBlog" in selenium_driver.page_source

            # Verificar que hay contenido de posts
            assert (
                "Posts" in selenium_driver.page_source
                or "Bienvenido" in selenium_driver.page_source
            )

        except TimeoutException:
            selenium_driver.save_screenshot("test_homepage_failed.png")
            raise AssertionError("La página principal no cargó correctamente")

    def test_navigation_to_create_post(
        self,
        selenium_driver,
        e2e_base_url,
        flask_test_app,
    ):
        """Test E2E: Navegación a la página de crear post"""

        # Ir directamente a la página de crear post
        selenium_driver.get(f"{e2e_base_url}/create")

        try:
            # Verificar que llegamos a la página correcta
            WebDriverWait(selenium_driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )

            assert "/create" in selenium_driver.current_url

            # Verificar campos del formulario
            title_field = selenium_driver.find_element(By.NAME, "title")
            content_field = selenium_driver.find_element(By.NAME, "content")

            assert title_field.is_displayed()
            assert content_field.is_displayed()

        except TimeoutException:
            selenium_driver.save_screenshot("test_create_page_failed.png")
            raise AssertionError("No se pudo cargar la página de crear post")
        
        def test_search_page_loads(
        self,
        selenium_driver,
        e2e_base_url,
        flask_test_app):
            """Test E2E: La página de búsqueda funciona"""
            selenium_driver.get(f"{e2e_base_url}/search")

            try:
                # Verificar que la página carga
                WebDriverWait(selenium_driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                # Verificar que contiene elementos de búsqueda
                assert (
                    "Buscar" in selenium_driver.page_source
                    or "search" in selenium_driver.page_source
                )

            except TimeoutException:
                selenium_driver.save_screenshot("test_search_page_failed.png")
                raise AssertionError("La página de búsqueda no cargó correctamente")

        def test_api_health_check_accessible(
            self,
            selenium_driver,
            e2e_base_url,
            flask_test_app,
        ):
            """Test E2E: El endpoint de health check es accesible desde navegador"""
            selenium_driver.get(f"{e2e_base_url}/api/health")

            try:
                # Esperar que aparezca contenido JSON
                WebDriverWait(selenium_driver, 10).until(
                    lambda driver: (
                        "healthy" in driver.page_source
                        or "status" in driver.page_source
                    )
                )

                page_content = selenium_driver.page_source
                assert (
                    "status" in page_content
                    or "healthy" in page_content
                )

            except TimeoutException:
                selenium_driver.save_screenshot("test_health_check_failed.png")
                raise AssertionError("El health check no respondió correctamente")