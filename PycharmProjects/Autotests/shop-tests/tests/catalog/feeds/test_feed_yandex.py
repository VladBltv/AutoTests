import json
import allure
from allure_commons.types import Severity
from requests import Response
from utils import files
from befree.api_model import api, db_connection
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
import os


class TestFeedYandex(QueriesCatalog):
    @allure.id("2563")
    @allure.title("Фид yandex: категории и оферы")
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
        Консольная команда для генерации фида: php artisan befree:generate_feed yandex
        Путь до файла фида: {{SERVER_CATALOG}}/storage/feeds/yandex.xml"""
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_yandex_categories_and_offers(self):
        with allure.step("Сгенерировать фид"):
            with allure.step("Генерация фида проходит успешно"):
                """Перед вызовом теста выполнить команду генерации фида на сервере используемой среды php artisan befree:generate_feed yandex"""
                pass

        with allure.step("Запросить фид"):
            feed_yandex: Response = api.storage_session.get("/storage/feeds/yandex.xml")
            assert feed_yandex.status_code == 200

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(
                files.generate_absolute_path("resources/yandex.xml"),
                feed_yandex.text,
            )
            files.xml_to_json(files.generate_absolute_path("resources/yandex.xml"), "yandex")

            yandex_feed_data = json.loads(
                files.read(files.generate_absolute_path("resources/yandex.json"))
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
                        yandex_feed_data["yml_catalog"]["shop"]["categories"]["category"],
                    )
                )

                assert len(list(set(categories_base) ^ set(categories_feed))) == 0
        with allure.step(
            "Сформировать в базе список цветомоделей подпадающих под условия отбора в фида"
        ):
            min_qty_ff = os.getenv("MIN_QTY_FF")
            query = f"""
                        select CONCAT(p.article , '/', v.color_code_id) as color_code
                        from variations as v 
                        join products as p on v.product_id=p.id 
                        where v.fulfilment_qty >= {min_qty_ff} and v.deleted_at is null and p.fulfilment_frozen is false
                        group by p.id , p.article, v.color_code_id 
                    """

            offers_base = list(
                map(lambda n: n["color_code"], db_connection.catalog.get_data(query))
            )

            with allure.step("Варианты из списка совпадают с вариантами в фиде"):
                offers_feed = list(
                    map(
                        lambda n: "/".join(n["url"].split("/")[-2:]),
                        yandex_feed_data["yml_catalog"]["shop"]["offers"]["offer"],
                    )
                )

                offers_base_not_in_feed = set(offers_base) - set(offers_feed)
                offers_feed_not_in_base = set(offers_feed) - set(offers_base)

                assert len(list(set(offers_base) ^ set(offers_feed))) == 0

    @allure.id("2564")
    @allure.title("Фид yandex структура данных")
    @allure.label("service", "Catalog")
    @allure.feature("Yandex", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description("Проверяем корректное формирование структуры офера в фидe yandex")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_yandex_data_structure(self):
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
