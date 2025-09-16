import allure
from allure_commons.types import Severity
from befree.api_model.catalog.public import CatalogPublic


class TestService(CatalogPublic):
    @allure.id("1138")
    @allure.tag("API Tests")
    @allure.severity(Severity.BLOCKER)
    @allure.suite("Service")
    @allure.label("owner", "Potegova")
    @allure.description("Проверяем, что все основные сервисы живы")
    @allure.title("Статус работоспособности сервисов")
    @allure.label("service", "Catalog")
    def test_get_heartbeat(self):
        with allure.step("Отправить запрос"):
            response = self.api_service.heartbeat()
            
        with allure.step("Проверить, что метод отдал успешный ответ"):
            assert response.status_code == 200
            assert response.json()["data"]["service"] is True
            assert response.json()["data"]["db"] is True
            assert response.json()["data"]["redis"] is True
            assert response.json()["data"]["rabbit"] is True
