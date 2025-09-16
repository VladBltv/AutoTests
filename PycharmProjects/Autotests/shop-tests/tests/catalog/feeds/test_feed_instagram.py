import json
import allure
from allure_commons.types import Severity
from requests import Response
from utils import files
from befree.api_model import api, db_connection
from befree.api_model.catalog.db_queries.queries import QueriesCatalog
import os


class TestFeedInstagram(QueriesCatalog):
    @allure.id("2560")
    @allure.title("Фид instagram: оферы")
    @allure.label("service", "Catalog")
    @allure.feature("Instagram", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description(
        """Требования к формированию фида

        Для наполнения items должны выполняться следующие условия
        Товар не в заморозке по складу fulfilment
        Товар не помечен на удаление
        Остаток товара по складу fulfilment > 1
        Текущая цена не равна 0: свойство варианта current_price != 0
        Консольная команда для генерации фида: php artisan befree:generate_feed instagram
        Путь до файла фида: {{SERVER_CATALOG}}/storage/feeds/instagram.xml"""
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_instagram_offers(self):
        with allure.step("Сгенерировать фид"):
            with allure.step("Генерация фида проходит успешно"):
                """Перед вызовом теста выполнить команду генерации фида на сервере используемой среды php artisan befree:generate_feed instagram"""
                pass
        with allure.step("Запросить фид"):
            feed_instagram: Response = api.storage_session.get("/storage/feeds/instagram.xml")
            assert feed_instagram.status_code == 200

        with allure.step("Записать фид в файл, конвертировать его в json, записать в объект"):
            files.write_as_is(files.generate_absolute_path("resources/instagram.xml"), feed_instagram.text)
            files.xml_to_json(files.generate_absolute_path("resources/instagram.xml"), "instagram")

            instagram_feed_data = json.loads(files.read(files.generate_absolute_path("resources/instagram.json")))

        with allure.step("Сформировать в базе список вариантов подпадающих под условия отбора в фида"):
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
                        lambda n: int(n["g:id"]),
                        instagram_feed_data["rss"]["channel"]["item"],
                    )
                )
                assert len(list(set(offers_base) ^ set(offers_feed))) == 0

    @allure.id("2559")
    @allure.title("Фид instagram структура данных")
    @allure.label("service", "Catalog")
    @allure.feature("Instagram", "Фиды")
    @allure.label("suite", "Listing")
    @allure.label("owner", "potegovaav")
    @allure.description("Проверяем корректное формирование структуры офера в фидe instagram")
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    def test_feed_instagram_data_structure(self):
        with allure.step("В каждый оффер передаются релевантные значения полей. Структура оффера соответствует схеме"):
            pass
        with allure.step("Порядок изображений варианта соответствует порядку, установленному в товаре"):
            with allure.step("Поменять порядок изображений в админке"):
                with allure.step("В оффере порядок изображений меняется"):
                    pass
