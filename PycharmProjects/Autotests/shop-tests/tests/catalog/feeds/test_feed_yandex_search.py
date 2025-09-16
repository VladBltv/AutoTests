import json
import allure
from allure_commons.types import Severity
from requests import Response
from utils import files
from befree.api_model import api, db_connection
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
from pytest_check import check
import os



class TestFeedYandexSearch(QueriesCatalog):
    @allure.id("1505")
    @allure.title("Фид yandex_search: категории и оферы")
    @allure.label("service", "Catalog")
    @allure.feature("Yandex", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description(
        """Требования к формированию фида

        В секции categories записываются все сущности компиляций с параметром is_category = true
        В секции categories не помещаются сущности компиляций, которые имеют параметр is_category = false
        Для наполнения offers должны выполняться следующие условия
        Товар не в заморозке по складу fulfilment
        Товар не помечен на удаление
        Остаток товара по складу fulfilment > 2
        Консольная команда для генерации фида: php artisan befree:generate_feed yandex_search
        Путь до файла фида: {{SERVER_CATALOG}}/storage/feeds/yandex_search.xml"""
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_yandex_search_categories_and_offers(self):
        with allure.step("Сгенерировать фид"):
            with allure.step("Генерация фида проходит успешно"):
                """Перед вызовом теста выполнить команду генерации фида на сервере используемой среды php artisan befree:generate_feed yandex_search"""
                pass

        with allure.step("Запросить фид"):
            feed_yandex_search: Response = api.storage_session.get(
                "/storage/feeds/yandex_search.xml"
            )
            assert feed_yandex_search.status_code == 200

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(
                files.generate_absolute_path("resources/yandex_search.xml"),
                feed_yandex_search.text,
            )
            files.xml_to_json(
                files.generate_absolute_path("resources/yandex_search.xml"), "yandex_search"
            )

            yandex_search_feed_data = json.loads(
                files.read(files.generate_absolute_path("resources/yandex_search.json"))
            )

        with allure.step("Сформировать в базе список актуальных id категорий"):
            query = f"""
                    select c.id
                    from compilations c 
                    where c.deleted_at is null and c.is_category is true
                """

            categories_base = list(map(lambda n: n["id"], db_connection.catalog.get_data(query)))

            with allure.step("Список должен совпадать со списком категорий в фиде"):
                categories_feed = list(
                    map(
                        lambda n: int(n["@id"]),
                        yandex_search_feed_data["yml_catalog"]["shop"]["categories"]["category"],
                    )
                )

                assert len(list(set(categories_base) ^ set(categories_feed))) == 0
        with allure.step(
            "Сформировать в базе список вариантов подпадающих под условия отбора в фида"
        ):
            min_qty_ff = os.getenv("MIN_QTY_FF")
            query = f"""
                        select v.id
                        from variations as v 
                        join products as p on v.product_id=p.id 
                        where v.fulfilment_qty >= {min_qty_ff} and v.deleted_at is null and p.fulfilment_frozen is false
                    """

            offers_base = list(map(lambda n: n["id"], db_connection.catalog.get_data(query)))

            with allure.step("Варианты из списка совпадают с вариантами в фиде"):
                offers_feed = list(
                    map(
                        lambda n: int(n["@id"]),
                        yandex_search_feed_data["yml_catalog"]["shop"]["offers"]["offer"],
                    )
                )
                offers_base_not_in_feed = list(set(offers_base) - set(offers_feed))
                print("offers_base_not_in_feed", offers_base_not_in_feed)
                offers_feed_not_in_base = list(set(offers_feed) - set(offers_base))
                print("offers_feed_not_in_base", offers_feed_not_in_base)

                check.equal(len(offers_base_not_in_feed), 0, "Offers base not in feed exist")
                check.equal(len(offers_feed_not_in_base), 0, "Offers feed not in base exist")

    @allure.id("2566")
    @allure.title("Фид yandex_search структура данных")
    @allure.label("service", "Catalog")
    @allure.feature("Yandex", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description("Проверяем корректное формирование структуры офера в фидe yandex_search")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_yandex_search_data_structure(self):
        with allure.step(
            "В каждый оффер передаются релевантные значения полей. Структура оффера соответствует схеме"
        ):
            pass
        with allure.step(
            "Порядок изображений варианта соответствует порядку, установленному в товаре"
        ):
            with allure.step("Поменять порядок изображений в админке"):
                with allure.step("В оффере порядок изображений меняется"):
                    pass
