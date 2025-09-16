import allure
from allure_commons.types import Severity
import json
from befree.api_model import api, db_connection
from requests import Response
from befree.api_model.listings import (
    compare_cardsCount_in_database_and_api,
)
from befree.api_model.test_data.listing.cards_count_from_products import (
    compilations,
)


@allure.id("1329")
@allure.title(
    "Количество товаров в компиляции с составом от категорий: без категории + свойство + атрибут"
)
@allure.description(
    "Проверяем, что количество карточек в компиляции с составом от категорий: без категории + свойство + атрибут, совпадает с количеством из БД"
)
@allure.label("service", "Catalog")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Состав листинга")
@allure.label("owner", "Balakireva")
def test_compare_cards_count1():
    gender = "female"
    # compilation_id = 404
    compilation_slug = "proverka-selection-settings-atribut-svoistvo"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Получаем из БД количество доступных карточек для компиляции"):
        cardsCount_query = f"""
                    select count(distinct v.listing_card_id)
                    from product_compilations pc 
                    join products p on p.id = pc.product_id 
                    join variations v on v.product_id = p.id 
                    join variation_inventories vi on vi.variation_id = v.id 
                    join variation_attribute_values vav on vav.variation_id = v.id 
                    where (vi.city_id = 2 or vi.city_id is null) and p.gender = 'female' 
                        and 
                        (
                            exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (variation_attribute_values.attribute_id =106 
                                                and variation_attribute_values.attribute_value_id in (98)))
                            and v.size_id in (2))
                   """

        cardsCount_from_database = db_connection.catalog.get_data(cardsCount_query)
        with allure.step("Сравниваем количество карточек, полученных через апи и бд"):
            assert (
                len(response_public_compilation.json()["data"]["items"])
                == cardsCount_from_database[0]["count"]
            ), "Некорректное количество карточек в листинге"


@allure.id("1294")
@allure.title(
    "Количество товаров в компиляции с составом от категорий: без категории + свойство + свойство"
)
@allure.description(
    "Проверяем, что количество карточек в компиляции с составом от категорий: без категории + свойство + свойство, совпадает с количеством из БД"
)
@allure.label("service", "Catalog")
@allure.tag("API Test")
@allure.feature("Состав листинга")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.label("owner", "Balakireva")
def test_compare_cards_count2():
    gender = "female"
    # compilation_id = 405
    compilation_slug = "proverka-selection-settings-svoistvo-svoistvo"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Получаем из БД количество доступных карточек для компиляции"):
        cardsCount_query = f"""
                    select count(distinct v.listing_card_id)
                    from product_compilations pc 
                    join products p on p.id = pc.product_id 
                    join variations v on v.product_id = p.id 
                    join variation_inventories vi on vi.variation_id = v.id 
                    join variation_attribute_values vav on vav.variation_id = v.id 
                    where (vi.city_id = 2 or vi.city_id is null) and p.gender = 'female' 
                        and 
                        ( v.color_id in (9) and (v.size_id in (2)))		
                   """

        cardsCount_from_database = db_connection.catalog.get_data(cardsCount_query)
        with allure.step("Сравниваем количество карточек, полученных через апи и бд"):
            assert (
                response_public_compilation.json()["data"]["cards_count"]
                == cardsCount_from_database[0]["count"]
            ), "Некорректное количество карточек в листинге"


@allure.id("1298")
@allure.title(
    "Количество товаров в компиляции с составом от категорий: без категории + атрибут + атрибут"
)
@allure.description(
    "Проверяем, что количество карточек в компиляции с составом от категорий: без категории + атрибут + атрибут, совпадает с количеством из БД"
)
@allure.label("service", "Catalog")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Состав листинга")
@allure.label("owner", "Balakireva")
def test_compare_cards_count3():
    gender = "female"
    # compilation_id = 406
    compilation_slug = "proverka-selection-settings-atribut-atribut"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Получаем из БД количество доступных карточек для компиляции"):
        cardsCount_query = f"""
                    select count(distinct v.listing_card_id)
                    from product_compilations pc 
                    join products p on p.id = pc.product_id 
                    join variations v on v.product_id = p.id 
                    join variation_inventories vi on vi.variation_id = v.id 
                    join variation_attribute_values vav on vav.variation_id = v.id 
                    where (vi.city_id = 2 or vi.city_id is null) and p.gender = 'female' 
                        and 
                        (
                            exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (variation_attribute_values.attribute_id =110 
                                                and variation_attribute_values.attribute_value_id in (210)))
                            and exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (variation_attribute_values.attribute_id =121 
                                                and variation_attribute_values.attribute_value_id in (153)))
                    )		
                   """

        cardsCount_from_database = db_connection.catalog.get_data(cardsCount_query)
        with allure.step("Сравниваем количество карточек, полученных через апи и бд"):
            assert (
                len(response_public_compilation.json()["data"]["items"])
                == cardsCount_from_database[0]["count"]
            ), "Некорректное количество карточек в листинге"


@allure.id("1299")
@allure.title(
    "Количество товаров в компиляции с составом от категорий: с категорией + атрибут + свойство"
)
@allure.description(
    "Проверяем, что количество карточек в компиляции с составом от категорий: с категорией + атрибут + свойство, совпадает с количеством из БД"
)
@allure.label("service", "Catalog")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Состав листинга")
@allure.label("owner", "Balakireva")
def test_compare_cards_count4():
    gender = "female"
    # compilation_id = 407
    compilation_slug = "proverka-selection-settings-kategoriia-atribut-svoistvo"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Получаем из БД количество доступных карточек для компиляции"):
        cardsCount_query = f"""
                    select count(distinct v.listing_card_id)
                    from product_compilations pc 
                    join products p on p.id = pc.product_id 
                    join variations v on v.product_id = p.id 
                    join variation_inventories vi on vi.variation_id = v.id 
                    join variation_attribute_values vav on vav.variation_id = v.id 
                    where (vi.city_id = 2 or vi.city_id is null) and p.gender = 'female' 
                        and 
                        (p.category_id = 113
                            and exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (variation_attribute_values.attribute_id =110 
                                                and variation_attribute_values.attribute_value_id in (151)))
                            and exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (v.size_id in (2)))
)			
                   """

        cardsCount_from_database = db_connection.catalog.get_data(cardsCount_query)
        with allure.step("Сравниваем количество карточек, полученных через апи и бд"):
            assert (
                len(response_public_compilation.json()["data"]["items"])
                == cardsCount_from_database[0]["count"]
            ), "Некорректное количество карточек в листинге"


@allure.id("1296")
@allure.title(
    "Количество товаров в компиляции с составом от категорий: несколько групп селекшен-сеттингов"
)
@allure.description(
    "Проверяем, что количество карточек в компиляции с составом от категорий: с категорией + атрибут + свойство и без категории + атрибут + свойство, совпадает с количеством из БД"
)
@allure.label("service", "Catalog")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Состав листинга")
@allure.label("owner", "Balakireva")
def test_compare_cards_count5():
    gender = "female"
    # compilation_id = 408
    compilation_slug = "proverka-selection-settings-2-gruppy"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Получаем из БД количество доступных карточек для компиляции"):
        cardsCount_query = f"""
                   select count(distinct v.listing_card_id)
                    from product_compilations pc 
                    join products p on p.id = pc.product_id 
                    join variations v on v.product_id = p.id 
                    join variation_inventories vi on vi.variation_id = v.id 
                    join variation_attribute_values vav on vav.variation_id = v.id 
                    where (vi.city_id = 2 or vi.city_id is null) and p.gender = 'female' 
                        and 
                        ((p.category_id = 71
                            and exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (variation_attribute_values.attribute_id =106 
                                                and variation_attribute_values.attribute_value_id in (22035)))
                                and exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (v.color_id in (10,1,2)))
                    )		or (exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (variation_attribute_values.attribute_id =110 
                                                and variation_attribute_values.attribute_value_id in (96)))
                                and exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (v.size_id in (2)))
                                )
                    )
                    """

        cardsCount_from_database = db_connection.catalog.get_data(cardsCount_query)
        with allure.step("Сравниваем количество карточек, полученных через апи и бд"):
            assert (
                response_public_compilation.json()["data"]["cards_count"]
                == cardsCount_from_database[0]["count"]
            ), "Некорректное количество карточек в листинге"


@allure.id("1326")
@allure.title(
    "Количество товаров в компиляции с составом от категорий: без категории + свойство + стикер системный"
)
@allure.description(
    "Проверяем, что количество карточек в компиляции с составом от категорий: без категории + свойство + стикер системный, совпадает с количеством из БД"
)
@allure.label("service", "Catalog")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Состав листинга")
@allure.label("owner", "Balakireva")
def test_compare_cards_count6():
    gender = "female"
    # compilation_id = 412
    compilation_slug = "proverka-selection-settings-svoistvo-stiker-sistemnyi"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Получаем из БД количество доступных карточек для компиляции"):
        cardsCount_query = f"""
                        select count(distinct v.listing_card_id)
                        from product_compilations pc 
                        join products p on p.id = pc.product_id 
                        join variations v on v.product_id = p.id 
                        join variation_inventories vi on vi.variation_id = v.id 
                        where (vi.city_id = 2 or vi.city_id is null) and p.gender = 'female' 
                               and p.sticker_new=true and v.color_id  in (8)
                       """

        cardsCount_from_database = db_connection.catalog.get_data(cardsCount_query)
        with allure.step("Сравниваем количество карточек, полученных через апи и бд"):
            assert (
                len(response_public_compilation.json()["data"]["items"])
                == cardsCount_from_database[0]["count"]
            ), "Некорректное количество карточек в листинге"


@allure.id("1328")
@allure.title(
    "Количество товаров в компиляции с составом от категорий: без категории + атрибут + стикер кастомный"
)
@allure.description(
    "Проверяем, что количество карточек в компиляции с составом от категорий: без категории + атрибут + стикер, совпадает с количеством из БД"
)
@allure.label("service", "Catalog")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Состав листинга")
@allure.label("owner", "Balakireva")
def test_compare_cards_count7():
    gender = "female"
    # compilation_id = 413
    compilation_slug = "proverka-selection-settings-atribut-stiker-kastomnyi"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Получаем из БД количество доступных карточек для компиляции"):
        cardsCount_query = f"""
                    select count(distinct v.listing_card_id)
                    from product_compilations pc 
                    join products p on p.id = pc.product_id 
                    join variations v on v.product_id = p.id 
                    join variation_inventories vi on vi.variation_id = v.id 
                    join variation_attribute_values vav on vav.variation_id = v.id 
                    where (vi.city_id = 2 or vi.city_id is null) and p.gender = 'female' 
                        and p.sticker_custom = 10 and
                        (
                            exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (variation_attribute_values.attribute_id =110 
                                                and variation_attribute_values.attribute_value_id in (96,97,14)))
                            )
                           """

        cardsCount_from_database = db_connection.catalog.get_data(cardsCount_query)
        with allure.step("Сравниваем количество карточек, полученных через апи и бд"):
            assert (
                len(response_public_compilation.json()["data"]["items"])
                == cardsCount_from_database[0]["count"]
            ), "Некорректное количество карточек в листинге"


@allure.id("1330")
@allure.title(
    "Количество товаров в компиляции с составом от категорий: без категории + стикер системный + стикер кастомный"
)
@allure.description(
    "Проверяем, что количество карточек в компиляции с составом от категорий: без категории + стикер + стикер, совпадает с количеством из БД"
)
@allure.label("service", "Catalog")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Состав листинга")
@allure.label("owner", "Balakireva")
def test_compare_cards_count8():
    gender = "female"
    # compilation_id = 414
    compilation_slug = "proverka-selection-settings-stiker-stiker"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Получаем из БД количество доступных карточек для компиляции"):
        cardsCount_query = f"""
                    select count(distinct v.listing_card_id)
                    from product_compilations pc 
                    join products p on p.id = pc.product_id 
                    join variations v on v.product_id = p.id 
                    join variation_inventories vi on vi.variation_id = v.id 
                    where (vi.city_id = 2 or vi.city_id is null) and p.gender = 'female' 
                        and p.sticker_custom = 10 and p.sticker_hit=true
                               """

        cardsCount_from_database = db_connection.catalog.get_data(cardsCount_query)
        with allure.step("Сравниваем количество карточек, полученных через апи и бд"):
            assert (
                len(response_public_compilation.json()["data"]["items"])
                == cardsCount_from_database[0]["count"]
            ), "Некорректное количество карточек в листинге"


@allure.id("1327")
@allure.title(
    "Количество товаров в компиляции с составом от категорий: категория + стикер системный + свойство + атрибут"
)
@allure.description(
    "Проверяем, что количество карточек в компиляции с составом от категорий: категория + стикер системный + свойство + атрибут, совпадает с количеством из БД"
)
@allure.label("service", "Catalog")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Состав листинга")
@allure.label("owner", "Balakireva")
def test_compare_cards_count9():
    gender = "female"
    # compilation_id = 415
    compilation_slug = "proverka-selection-settings-kategoriia-stiker-atribut-svoistvo"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Получаем из БД количество доступных карточек для компиляции"):
        cardsCount_query = f"""
                    select count(distinct v.listing_card_id)
                    from product_compilations pc 
                    join products p on p.id = pc.product_id 
                    join variations v on v.product_id = p.id 
                    join variation_inventories vi on vi.variation_id = v.id 
                    join variation_attribute_values vav on vav.variation_id = v.id 
                    where (vi.city_id = 2 or vi.city_id is null) and p.gender = 'female' 
                        and p.category_id= 113 and p.sticker_new=true and
                        (
                            exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (variation_attribute_values.attribute_id =110 
                                                and variation_attribute_values.attribute_value_id in (14)))
                            and v.size_id in (2,3))
                                   """

        cardsCount_from_database = db_connection.catalog.get_data(cardsCount_query)
        with allure.step("Сравниваем количество карточек, полученных через апи и бд"):
            assert (
                len(response_public_compilation.json()["data"]["items"])
                == cardsCount_from_database[0]["count"]
            ), "Некорректное количество карточек в листинге"


@allure.id("1329")
@allure.title(
    "Количество товаров в компиляции с составом от категорий: несколько групп селекшен-сеттингов + стикер"
)
@allure.description(
    "Проверяем, что количество карточек в компиляции с составом от категорий: с категорией + атрибут + стикер системный и без категории + свойство + стикер кастомный, совпадает с количеством из БД"
)
@allure.label("service", "Catalog")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.feature("Состав листинга")
@allure.label("owner", "Balakireva")
def test_compare_cards_count10():
    gender = "female"
    # compilation_id = 416
    compilation_slug = "proverka-selection-settings-2-gruppy-stikery"

    with allure.step("Формируем тело запроса и отправляем запрос на получении компиляции"):
        listing_data = json.dumps(
            {
                "gender": gender,
                "cityData": {
                    "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                    "goldenRecord": "sank-823938",
                },
            }
        )

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilation_slug}",
            data=listing_data,
            headers={"Content-Type": "application/json"},
        )

    with allure.step("Проверяем, что запрос прошел успешно"):
        assert response_public_compilation.status_code == 200

    with allure.step("Получаем из БД количество доступных карточек для компиляции"):
        cardsCount_query = f"""
                   select count(distinct v.listing_card_id)
                    from product_compilations pc 
                    join products p on p.id = pc.product_id 
                    join variations v on v.product_id = p.id 
                    join variation_inventories vi on vi.variation_id = v.id 
                    join variation_attribute_values vav on vav.variation_id = v.id 
                    where (vi.city_id = 2 or vi.city_id is null) and p.gender = 'female' 
                        and 
                       ( (p.category_id = 113 and p.sticker_new = true
                            and v.size_id in (2,3)
                    )		or (p.sticker_custom = 10 and 
                    exists(select * from variation_attribute_values
                                             where variation_id = v.id
                                                and (variation_attribute_values.attribute_id =110 
                                                and variation_attribute_values.attribute_value_id in (97,14)))
                                ))
                    """

        cardsCount_from_database = db_connection.catalog.get_data(cardsCount_query)
        with allure.step("Сравниваем количество карточек, полученных через апи и бд"):
            assert (
                response_public_compilation.json()["data"]["cards_count"]
                == cardsCount_from_database[0]["count"]
            ), "Некорректное количество карточек в листинге"


@allure.id("1297")
@allure.title("Количество товаров в компиляции с составом от товаров")
@allure.description("Проверяем, что количество карточек в компиляции с составом от товаров")
@allure.label("service", "Catalog")
@allure.tag("API Test")
@allure.feature("Состав листинга")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.label("owner", "Balakireva")
def test_compare_cards_count_from_products():
    # gender = "female"
    # compilation_id = 409
    # compilation_slug = "podborka-ot-tovarov-z"

    with allure.step("Устанавливаем значение города - Санкт-Петербург"):
        city = {
            "id": 2,
            "cityData": {
                "fiasId": "c2deb16a-0330-4f05-821f-1d09c93331e6",
                "goldenRecord": "sank-823938",
            },
        }

    with allure.step(
        "Сравниваем количество карточек всех компиляций по женскому гендеру в г.Санкт-Петербург"
    ):
        database_card_count = compare_cardsCount_in_database_and_api(compilations, city)
        assert database_card_count, "Не совпадает количество карточек в БД и через АПИ"
