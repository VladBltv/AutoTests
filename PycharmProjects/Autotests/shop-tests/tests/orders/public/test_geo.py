import allure

from befree.api_model.orders.public import OrdersPublic
from befree.api_model.orders.public.geo import shemas
from allure_commons.types import Severity
from pytest_voluptuous import S


class TestGeoAndSuggestions(OrdersPublic):
    @allure.id("2703")
    @allure.title("Получение города по айпи")
    @allure.label("service", "Orders")
    @allure.feature("Геолокация")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Common")
    @allure.description("Проверяем получение информации по городу по айпи")
    def test_city_by_ip(self):
        with allure.step("Запросить город по ip в апи"):
            city_response = self.api_geo.city_by_ip()
            assert city_response.status_code == 200

        with allure.step("Проверить, что полученная структура соответствует схеме"):
            assert S(shemas.city_by_ip) == city_response.json()

    @allure.id("2704")
    @allure.title("Получение данных города по строке")
    @allure.label("service", "Orders")
    @allure.feature("Подсказки адресов")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Common")
    @allure.description("Проверяем получение информации о городе по введенной строке")
    def test_suggestion_city(self):
        with allure.step("Запросить существующий город в апи"):
            city_response = self.api_geo.suggestion_city(query="москва")
            assert city_response.status_code == 200

        with allure.step("Проверить, что полученная структура соответствует схеме"):
            assert S(shemas.suggestion_city) == city_response.json()

        with allure.step("Запросить несуществующий город в апи"):
            city_response = self.api_geo.suggestion_city(query="qwerty")
            assert city_response.status_code == 200

        with allure.step("Проверить, что в ответе пришел пустой массив"):
            assert city_response.json()["data"] == []

        with allure.step("Запросить не город, а поселок в апи"):
            city_response = self.api_geo.suggestion_city(query="соддер")
            assert city_response.status_code == 200

        with allure.step("Проверить, что в ответе пришел поселок"):
            assert city_response.json()["data"][0]["fullName"].find("поселок")

    @allure.id("2702")
    @allure.title("Получение данных улицы по городу")
    @allure.label("service", "Orders")
    @allure.feature("Подсказки адресов")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.description("Проверяем получение информации об улице по введенной строке")
    def test_suggestion_street(self):
        with allure.step("Получаем фиас города"):
            city_response = self.api_geo.suggestion_city(query="москва")
            assert city_response.status_code == 200
            city_fias_id = city_response.json()["data"][0]["cityData"]["fiasId"]

        with allure.step("Запросить существующую улицу в апи"):
            street_response = self.api_geo.suggestion_street(
                city_fias_id=city_fias_id, query="оранжерейная"
            )
            assert street_response.status_code == 200

        with allure.step("Проверить, что полученная структура соответствует схеме"):
            assert S(shemas.suggestion_street) == street_response.json()

        with allure.step("Запросить несуществующую улицу в апи"):
            street_response = self.api_geo.suggestion_street(
                city_fias_id=city_fias_id, query="qwerty"
            )
            assert street_response.status_code == 200

        with allure.step("Проверить, что в ответе пришел пустой массив"):
            assert street_response.json()["data"] == []

    @allure.id("2700")
    @allure.title("Получение данных здания по улице")
    @allure.label("service", "Orders")
    @allure.feature("Подсказки адресов")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Checkout")
    @allure.description("Проверяем получение информации о здании по введенной улице")
    def test_suggestion_building(self):
        with allure.step("Получаем фиас города"):
            city_response = self.api_geo.suggestion_city(query="москва")
            assert city_response.status_code == 200
            city_fias_id = city_response.json()["data"][0]["cityData"]["fiasId"]

        with allure.step("Получаем фиас улицы"):
            street_response = self.api_geo.suggestion_street(
                city_fias_id=city_fias_id, query="оранжерейная"
            )
            assert street_response.status_code == 200
            street_fias_id = street_response.json()["data"][0]["fiasId"]

        with allure.step("Запросить существующую дом в апи"):
            building_response = self.api_geo.suggestion_building(
                street_fias_id=street_fias_id, query="2"
            )
            assert building_response.status_code == 200

        with allure.step("Проверить, что полученная структура соответствует схеме"):
            assert S(shemas.suggestion_building) == building_response.json()

        with allure.step("Запросить несуществующий дом в апи"):
            street_response = self.api_geo.suggestion_building(
                street_fias_id=street_fias_id, query="qwerty"
            )
            assert street_response.status_code == 200

        with allure.step("Проверить, что в ответе пришел пустой массив"):
            assert street_response.json()["data"] == []
