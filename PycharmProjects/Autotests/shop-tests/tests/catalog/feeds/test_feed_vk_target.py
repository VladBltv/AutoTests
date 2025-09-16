import json
import allure
from allure_commons.types import Severity
from requests import Response
from utils import files
from befree.api_model import api, db_connection
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
import os



class TestFeedVkTarget(QueriesCatalog):
    @allure.id("1505")
    @allure.title("Фид vk_target: категории и оферы")
    @allure.label("service", "Catalog")
    @allure.feature("VK", "Фиды")
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
        Консольная команда для генерации фида: php artisan befree:generate_feed vk
        Путь до файла фида: {{SERVER_CATALOG}}/storage/feeds/vk.xml"""
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_vk_target_categories_and_offers(self):
        with allure.step("Сгенерировать фид"):
            with allure.step("Генерация фида проходит успешно"):
                """Перед вызовом теста выполнить команду генерации фида на сервере используемой среды php artisan befree:generate_feed vk"""
                pass

        with allure.step("Запросить фид"):
            feed_vk: Response = api.storage_session.get("/storage/feeds/vk.xml")
            assert feed_vk.status_code == 200

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(
                files.generate_absolute_path("resources/vk.xml"),
                feed_vk.text,
            )
            files.xml_to_json(files.generate_absolute_path("resources/vk.xml"), "vk")

            vk_feed_data = json.loads(files.read(files.generate_absolute_path("resources/vk.json")))

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
                        vk_feed_data["yml_catalog"]["shop"]["categories"]["category"],
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
                        vk_feed_data["yml_catalog"]["shop"]["offers"]["offer"],
                    )
                )
                assert len(list(set(offers_base) ^ set(offers_feed))) == 0

        with allure.step("В оффере параметр group_id идет перед параметром id"):
            offer_example = vk_feed_data["yml_catalog"]["shop"]["offers"]["offer"][0]
            offer_structure = []
            for key in offer_example:
                offer_structure.append(key)
            assert offer_structure[0] == "@group_id" and offer_structure[1] == "@id"

    @allure.id("2562")
    @allure.title("Фид vk структура данных")
    @allure.label("service", "Catalog")
    @allure.feature("VK", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description("Проверяем корректное формирование структуры офера в фидe vk")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_vk_target_data_structure(self):
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
