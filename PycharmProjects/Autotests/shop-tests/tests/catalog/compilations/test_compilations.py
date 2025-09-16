import allure

from allure_commons.types import Severity
from befree.api_model.catalog.private import CatalogPrivate
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from befree.api_model.catalog.private.compilations import shemas
from pytest_voluptuous import S
from mimesis import Text


class TestCompilations(CatalogPrivate, QueriesCatalog):
    @allure.title("Список всех компиляций")
    @allure.label("service", "Catalog")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    @allure.label("feature", "Компиляции")
    @allure.description("Проверяем вывод списка всех компиляций и соотвтествие схеме")
    def test_compilations(self):
        with allure.step("Получаем список всех компиляций"):
            compilations_response = self.api_compilations.get_list()
            assert compilations_response.status_code == 200
        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.list_compilations) == compilations_response.json()

    @allure.id("2260")
    @allure.title("Компиляция с типом категория")
    @allure.label("service", "Catalog")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    @allure.label("feature", "Компиляции")
    @allure.description("Проверяем работу приватных методов с компиляцией типа категория")
    def test_category(self):
        with allure.step("Находим категорию в бд"):
            category_id, slug, gender = self.get_compilation(
                param="is_category", condition="=", value="true"
            )

        with allure.step("Получаем данные категории через апи"):
            category_response = self.api_compilations.get(compilation_id=category_id)
            assert category_response.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.category) == category_response.json()

        with allure.step("Изменяем данные категории через апи"):
            attribute = category_response.json()["data"]["filter_attributes"]["disabled"][0]
            filter_attributes = {"enabled": [attribute]}
            is_promo = 0 if category_response.json()["data"]["is_promo"] else 1

            update_response = self.api_compilations.update(
                compilation_id=category_id,
                title=category_response.json()["data"]["public_title"],
                slug=slug,
                is_promo=is_promo,
                gender=category_response.json()["data"]["gender"],
                filter_attributes=filter_attributes,
            )
            assert update_response.status_code == 200

        with allure.step("Проверяем, что данные изменились"):
            assert update_response.json()["data"]["is_promo"] == is_promo
            assert update_response.json()["data"]["filter_attributes"]["enabled"][0] == attribute

    @allure.id("2261")
    @allure.title("Компиляция с типом субкатегория")
    @allure.label("service", "Catalog")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    @allure.label("feature", "Компиляции")
    @allure.description("Проверяем работу приватных методов с компиляцией типа субкатегория")
    def test_subcategory(self):
        with allure.step("Находим субкатегорию в бд"):
            subcategory_id, slug, gender = self.get_compilation(
                param="parent_id", condition="is not", value="null"
            )

        with allure.step("Получаем данные субкатегории через апи"):
            subcategory_response = self.api_compilations.get(compilation_id=subcategory_id)
            assert subcategory_response.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.sub_category) == subcategory_response.json()

        with (allure.step("Изменяем данные субкатегории через апи")):
            with allure.step("Получаем атрибуты и значения родительской категории"):
                category_id = subcategory_response.json()["data"]["parent_id"]

                attributes_response = self.api_attributes.get(category_id=category_id)
                assert attributes_response.status_code == 200
                attribute_id = attributes_response.json()["data"][0]["id"]

                attribute_values_response = self.api_attributes.get_values(
                    compilation_id=category_id, attribute_id=attribute_id
                )
                assert attribute_values_response.status_code == 200
                attribute_value_id = attribute_values_response.json()["data"][0]["id"]

            with allure.step("Формируем отбор по атрибутам для субкатегории"):
                selection_settings = [
                    {
                        "group": 1,
                        "category_id": category_id,
                        "attributes": [
                            {"attribute_id": attribute_id, "attribute_value_id": attribute_value_id}
                        ],
                    }
                ]

            with allure.step("Отправляем запрос на изменение"):
                update_response = self.api_compilations.update(
                    compilation_id=subcategory_id,
                    title=subcategory_response.json()["data"]["public_title"],
                    slug=slug,
                    gender=subcategory_response.json()["data"]["gender"],
                    filter_type="filter",
                    selection_settings=selection_settings,
                )
                assert update_response.status_code == 200

        with allure.step("Проверяем, что данные изменились"):
            assert (
                update_response.json()["data"]["selection_settings"][0]["attribute_id"]
                == attribute_id
            )
            assert (
                update_response.json()["data"]["selection_settings"][0]["attribute_value_id"]
                == attribute_value_id
            )

        with allure.step("Создаем субкатегорию"):
            create_response = self.api_compilations.create(
                title=Text("ru").sentence()[:100],
                slug=Text("ru").sentence()[:100],
                is_sub_category=1,
                parent_id=category_id,
                filter_type="filter",
                selection_settings=selection_settings,
            )
            assert create_response.status_code == 200

    @allure.id("2542")
    @allure.title("Компиляция с типом подборка от товаров")
    @allure.label("service", "Catalog")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    @allure.label("feature", "Компиляции")
    @allure.description("Проверяем работу приватных методов с компиляцией типа подборка от товаров")
    def test_selection_by_products(self):
        with allure.step("Находим подборку в бд с типом products"):
            conditions = ["parent_id is null and is_category = false and filter_type  = 'products'"]
            selection_id, slug, gender = self.get_compilation_by_conditions(conditions=conditions)

        with allure.step("Получаем данные подборки через апи"):
            selection_response = self.api_compilations.get(compilation_id=selection_id)
            assert selection_response.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.selection_by_products) == selection_response.json()

        with allure.step("Изменяем данные подборки через апи"):
            attribute = selection_response.json()["data"]["filter_attributes"]["disabled"][0]
            filter_attributes = {"enabled": [attribute]}
            is_promo = 0 if selection_response.json()["data"]["is_promo"] else 1

            update_response = self.api_compilations.update(
                compilation_id=selection_id,
                title=selection_response.json()["data"]["public_title"],
                slug=slug,
                is_promo=is_promo,
                filter_attributes=filter_attributes,
            )
            assert update_response.status_code == 200

        with allure.step("Проверяем, что данные изменились"):
            assert update_response.json()["data"]["is_promo"] == is_promo
            assert update_response.json()["data"]["filter_attributes"]["enabled"][0] == attribute

        with allure.step("Создаем поборку от товаров"):
            create_response = self.api_compilations.create(
                title=Text("ru").sentence()[:100],
                slug=Text("ru").sentence()[:100],
                filter_type="products",
                product_action_flag="add",
            )
            assert create_response.status_code == 200

        with allure.step("Добавляем товары в подборку"):
            variation = self.find_omniAndSf_stocks(qty=3, city_id=6, store_id=1)
            product = self.get_product_by_variation(variation_id=variation)
            product_articles = [product["article"]]
            update_response = self.api_compilations.update(
                compilation_id=create_response.json()["data"]["id"],
                title=create_response.json()["data"]["public_title"],
                slug=create_response.json()["data"]["slug"],
                filter_type="products",
                product_action_flag="add",
                product_articles=product_articles,
            )
            assert update_response.status_code == 200

        with allure.step("Проверяем, что товары добавились в подборку"):
            assert update_response.json()["data"]["products_count"] > 0

    @allure.id("2543")
    @allure.title("Компиляция с типом подборка от категорий")
    @allure.label("service", "Catalog")
    @allure.label("owner", "balakirevams")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    @allure.label("feature", "Компиляции")
    @allure.description(
        "Проверяем работу приватных методов с компиляцией типа подборка от категорий"
    )
    def test_selection_by_categories(self):
        with allure.step("Находим подборку в бд с типом filter"):
            conditions = ["parent_id is null and is_category = false and filter_type  = 'filter'"]
            selection_id, slug, gender = self.get_compilation_by_conditions(conditions=conditions)

        with allure.step("Получаем данные подборки через апи"):
            selection_response = self.api_compilations.get(compilation_id=selection_id)
            assert selection_response.status_code == 200

        with allure.step("Проверяем, что полученная структура соответствует схеме"):
            assert S(shemas.selection_by_filter) == selection_response.json()

        with (allure.step("Изменяем данные субкатегории через апи")):
            with allure.step("Получаем атрибуты и значения родительской категории"):
                attributes_response = self.api_attributes.get()
                assert attributes_response.status_code == 200
                attribute_id = attributes_response.json()["data"][0]["id"]

                attribute_values_response = self.api_attributes.get_values(
                    attribute_id=attribute_id
                )
                assert attribute_values_response.status_code == 200
                attribute_value_id = attribute_values_response.json()["data"][0]["id"]

            with allure.step("Формируем отбор по атрибутам для подборки"):
                selection_settings = [
                    {
                        "group": 1,
                        "category_id": None,
                        "attributes": [
                            {"attribute_id": attribute_id, "attribute_value_id": attribute_value_id}
                        ],
                    }
                ]

            with allure.step("Отправляем запрос на изменение"):
                update_response = self.api_compilations.update(
                    compilation_id=selection_id,
                    title=selection_response.json()["data"]["public_title"],
                    slug=slug,
                    filter_type="filter",
                    selection_settings=selection_settings,
                )
                assert update_response.status_code == 200

        with allure.step("Проверяем, что данные изменились"):
            assert (
                update_response.json()["data"]["selection_settings"][0]["attribute_id"]
                == attribute_id
            )
            assert (
                update_response.json()["data"]["selection_settings"][0]["attribute_value_id"]
                == attribute_value_id
            )

        with allure.step("Создаем поборку от категорий"):
            create_response = self.api_compilations.create(
                title=Text("ru").sentence()[:100],
                slug=Text("ru").sentence()[:50],
                filter_type="filter",
                selection_settings=selection_settings,
            )
            assert create_response.status_code == 200
