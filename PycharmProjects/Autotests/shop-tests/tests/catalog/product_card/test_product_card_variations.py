import allure
from befree.api_model import db_connection
from allure_commons.types import Severity
from befree.api_model.test_data.product_card.variations import product_articles
import befree.api_model.product as pc
from utils.database import filling_out_table


@allure.id("1285")
@allure.title("Неактивные товары не приходят")
@allure.description("Проверить, что в апи приходят только активные варианты")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.feature("Доступность")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_inactive_variations():
    kladr = "7800000000000"

    with allure.step(
        "Отправляем запрос на получение товара, у которого все есть неактивный вариант"
    ):
        product_api = pc.get_via_api(product_articles["inactive_variation"]["article"], kladr)

    with allure.step("Проверяем, что пришли только активные цвета"):
        result = pc.compare_variations(
            product_articles["inactive_variation"]["variations"],
            product_api["variations"],
        )
        assert (
            result
        ), f"""Некорректный состав массива variations[] у товара {product_articles["inactive_variation"]["article"]}"""


@allure.id("1302")
@allure.title("Товары в морозилке")
@allure.description("Проверить, что в апи не приходят варианты, добавленные в морозилку")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.feature("Доступность")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_frozen():
    kladr = "7800000000000"

    with allure.step("Находим в БД товар, добавленный в морозилку по всем складам "):
        frozen_query = """
            select p.article  
            from products p  
            where p.deleted_at is null and p.fulfilment_frozen = true and p.omni_frozen = true
            limit 1
        """

        frozen_article = db_connection.catalog.get_data(frozen_query)

    with allure.step(
        "Отправляем запрос на получение товара, добавленного по всем складам в морозилку"
    ):
        product_api = pc.get_via_api(frozen_article[0]["article"], kladr)
    with allure.step("Проверяем, что пришел пустой массив variations[]"):
        assert product_api["variations"] == []

    with allure.step("Находим в БД товар, добавленный в морозилку только по fulfilment "):
        frozen_query = """
            select p.article 
            from products p  
            where p.deleted_at is null and p.fulfilment_frozen = true and p.omni_frozen = false
            limit 1
        """
        frozen_article = db_connection.catalog.get_data(frozen_query)
    with allure.step(
        "Отправляем запрос на получение товара, добавленного в морозилку только по fulfilment"
    ):
        product_api = pc.get_via_api(frozen_article[0]["article"], kladr)

    with allure.step("Проверяем, что массиве stocks[] нулевые остатки по fulfilment"):
        for i in range(0, len(product_api["variations"])):
            assert product_api["variations"][i]["stocks"]["fulfilment"] == 0

    with allure.step("Находим в БД товар, добавленный в морозилку только по омни "):
        frozen_query = """
            select p.article 
            from products p  
            where p.deleted_at is null and p.fulfilment_frozen = false and p.omni_frozen = true
            order by p.id desc
            limit 1 
        """
        frozen_article = db_connection.catalog.get_data(frozen_query)

    with allure.step(
        "Отправляем запрос на получение товара, добавленного в морозилку только по омни"
    ):
        product_api = pc.get_via_api(frozen_article[0]["article"], kladr)

    with allure.step("Проверяем, что массиве stocks[] нулевые остатки по омни"):
        for i in range(0, len(product_api["variations"])):
            assert product_api["variations"][i]["stocks"]["omni"] == 0


@allure.id("1303")
@allure.title("Остатки по fulfilment")
@allure.description("Проверить, что корректно приходят остатки по fulfilment")
@allure.tag("API Test")
@allure.feature("Доступность")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_stock_lamoda():
    kladr = "7800000000000"

    with allure.step(
        "Отправляем запрос на получение товара, у которого остатки по fulfilment = 0, но доступен в омни"
    ):
        product_article = "2326036006"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что массиве stocks[] нулевые остатки по fulfilment"):
        for i in range(0, len(product_api["variations"])):
            assert product_api["variations"][i]["stocks"]["fulfilment"] == 0

    with allure.step("Отправляем запрос на получение товара, у которого остатки по fulfilment = 1"):
        product_article = "2231144304"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step(
        "Проверяем, что пришли все варианты и в массиве stocks[] все остатки по fulfilment = 1"
    ):
        print(len(product_api["variations"]))
        assert len(product_api["variations"]) == 16
        for i in range(0, len(product_api["variations"])):
            assert product_api["variations"][i]["stocks"]["fulfilment"] == 1


@allure.id("1304")
@allure.title("Остатки по омни")
@allure.description("Проверить, что корректно приходят остатки по омни")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.feature("Доступность")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_stock_omni():
    kladr = "7800000000000"

    with allure.step(
        "Отправляем запрос на получение товара, у которого остатки по омни = 0, но доступен в fulfilment"
    ):
        product_article = "2316018006"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что массиве stocks[] нулевые остатки по омни"):
        for i in range(0, len(product_api["variations"])):
            assert product_api["variations"][i]["stocks"]["omni"] == 0

    with allure.step("Отправляем запрос на получение товара, у которого остатки по омни = 1"):
        product_article = "2316018000"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что массиве stocks[] нулевые остатки по омни"):
        for i in range(0, len(product_api["variations"])):
            assert product_api["variations"][i]["stocks"]["omni"] == 0
        assert product_api["variations"][i]["stores"] == []

    with allure.step("Отправляем запрос на получение товара, у которого остатки по омни = 2"):
        product_article = "2316015000"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что массиве stocks[] остатки по омни == 1"):
        assert product_api["variations"][0]["stocks"]["omni"] == 1
    with allure.step(
        "Проверяем количество магазинов в массиве stores[], чтобы пришли только те, у которых pickup_enabled_omni1=true "
    ):
        assert len(product_api["variations"][i]["stores"]) == 6

    with allure.step("Отправляем запрос на получение товара, у которого много остатков по омни"):
        product_article = "2336018026"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step(
        "Проверяем, что omni = max(stores[]) и чтобы пришли только те, у которых pickup_enabled_omni1=true "
    ):
        for i in range(0, len(product_api["variations"])):
            max_qty = max(
                product_api["variations"][i]["stores"][j]["qty"]
                for j in range(0, len(product_api["variations"][i]["stores"]))
            )
            assert product_api["variations"][i]["stocks"]["omni"] == max_qty


@allure.id("1305")
@allure.title("Методы доставки")
@allure.description(
    "Проверить, что корректно приходят методы доставки в зависимости от наличия на стоке"
)
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.feature("Доступность")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_delivery():
    kladr = "7800000000000"

    with allure.step("Отправляем запрос на получение товара, доступного только в fulfilment"):
        product_article = "2316018006"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что доступны доставки: pickup, delivery и post"):
        assert product_api["variations"][0]["deliveries"] == [2, 3, 4]

    with allure.step("Отправляем запрос на получение товара, доступного только в omni"):
        product_article = "2326036006"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что доступны доставки: omni"):
        for i in range(0, len(product_api["variations"])):
            assert product_api["variations"][i]["deliveries"] == [1]

    with allure.step(
        "Отправляем запрос на получение товара, у которого есть остатки и в fulfilment, и по омни"
    ):
        product_article = "2336018026"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что доступны доставки: omni,pickup, delivery и post"):
        for i in range(0, len(product_api["variations"])):
            assert product_api["variations"][i]["deliveries"] == [1, 2, 3, 4]


@allure.id("1306")
@allure.title("Методы оплаты")
@allure.description(
    "Проверить, что корректно приходят методы оплаты в зависимости от наличия на стоке"
)
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.feature("Доступность")
@allure.label("owner", "Balakireva")
@allure.label("service", "Catalog")
def test_product_card_payments():
    kladr = "7800000000000"

    with allure.step("Отправляем запрос на получение товара, доступного только в fulfilment"):
        product_article = "2316018006"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что доступны оплаты: podeli, card, raiffeisen и cash"):
        assert product_api["variations"][0]["payments"] == [1, 2, 3, 4]

    with allure.step("Отправляем запрос на получение товара, доступного только в omni"):
        product_article = "2326036006"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что доступны оплаты: raiffeisen и cash"):
        for i in range(0, len(product_api["variations"])):
            assert product_api["variations"][i]["payments"] == [3, 4]

    with allure.step(
        "Отправляем запрос на получение товара, у которого есть остатки и в fulfilment, и по омни"
    ):
        product_article = "2336018026"
        product_api = pc.get_via_api(product_article, kladr)

    with allure.step("Проверяем, что доступны оплаты: podeli, card, raiffeisen и cash"):
        for i in range(0, len(product_api["variations"])):
            assert product_api["variations"][i]["payments"] == [1, 2, 3, 4]
