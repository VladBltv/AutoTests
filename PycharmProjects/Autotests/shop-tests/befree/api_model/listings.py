import json
import math
from befree.api_model import api, db_connection
import allure
from allure_commons.types import AttachmentType
from requests import Response


def get_listing_id_and_slug_and_gender(param, value, condition):
    existing_compilation_query = f"""
                select c.id, c.slug, c.gender 
                from compilations c 
                where c.deleted_at is null and {param} {condition} {value}
                order by c.products_count desc
                limit 1
            """
    compilation = db_connection.catalog.get_data(existing_compilation_query)

    return compilation[0]["id"], compilation[0]["slug"], compilation[0]["gender"]


def compare_with_reference(listing, reference):
    # Инициализация
    comparing_result = dict()
    comparing_result["status"] = True
    comparing_result["items"] = []

    # Распарсиваем структуру json'а листинга
    listing_map = list(
        map(
            lambda item: {
                "id": item["id"],
                "article": item["article"],
                "calculated_price": item["calculated_price"],
                "discount_percent": item["discount_percent"],
                "color_code": item["color_code"],
                "colors_count": item["colors_count"],
            },
            listing,
        )
    )

    for i in range(len(listing)):
        if (
                listing_map[i]["id"] != reference[i]["id"]
                or listing_map[i]["article"] != reference[i]["article"]
                or listing_map[i]["calculated_price"] != reference[i]["calculated_price"]
                or listing_map[i]["discount_percent"] != reference[i]["discount_percent"]
                or listing_map[i]["color_code"] != reference[i]["color_code"]
                or listing_map[i]["colors_count"] != reference[i]["colors_count"]
        ):
            comparing_result["status"] = False
            comparing_result["items"].append(
                {
                    "actual_result": listing_map[i],
                    "expected_result": reference[i],
                    "item": i,
                }
            )

    if comparing_result["status"] != True:
        allure.attach(
            body=json.dumps(comparing_result["items"], indent=4).encode("utf8"),
            attachment_type=AttachmentType.JSON,
            extension=".json",
        )

    return comparing_result["status"]


def compare_sub_menu_with_reference(sub_menu, reference):
    comparing_result = dict()
    comparing_result["status"] = True
    comparing_result["items"] = []

    # Распарсиваем структуру json'а саб меню листинга
    sub_menu_map = list(
        map(
            lambda item: {
                "id": item["id"],
                "slug": item["slug"],
                "public_title": item["public_title"],
            },
            sub_menu,
        )
    )
    for i in range(len(sub_menu)):
        if (
                sub_menu_map[i]["id"] != reference[i]["id"]
                or sub_menu_map[i]["slug"] != reference[i]["slug"]
                or sub_menu_map[i]["public_title"] != reference[i]["public_title"]
        ):
            comparing_result["status"] = False
            comparing_result["items"].append(
                {
                    "actual_result": sub_menu_map[i],
                    "expected_result": reference[i],
                    "item": i,
                }
            )

    if comparing_result["status"] != True:
        allure.attach(
            body=json.dumps(comparing_result["items"], indent=4).encode("utf8"),
            attachment_type=AttachmentType.JSON,
            extension=".json",
        )

    return comparing_result["status"]


def get_all_active_compilations(gender):
    compilation_query = f"""
                select c.id, c.slug, c.gender , c.filter_type
                from compilations c 
                where c.deleted_at is null  and c.gender = '{gender}'
            """
    compilations = db_connection.catalog.get_data(compilation_query)

    compilations_map = list(
        map(
            lambda item: {
                "id": item["id"],
                "slug": item["slug"],
                "gender": item["gender"],
                "filter_type": item["filter_type"],
            },
            compilations,
        )
    )

    return compilations_map


def get_cardsCount_compilation_from_database(compilation_id, city_id, gender):
    cardsCount_of_compilation_query = f"""
           select count (distinct v.listing_card_id )
           from product_compilations pc 
           join products p on p.id = pc.product_id 
           join variations v on v.product_id = p.id 
           join variation_inventories vi on vi.variation_id = v.id 
           where pc.compilation_id = {compilation_id} and (vi.city_id = {city_id} or vi.city_id is null) and p.gender = '{gender}'
       """

    return db_connection.catalog.get_data(cardsCount_of_compilation_query)


def compare_cardsCount_in_database_and_api(compilations, city):
    # Инициализация
    comparing_result = dict()
    comparing_result["status"] = True
    comparing_result["items"] = []

    # Сравнение
    for i in range(len(compilations)):
        # Получаем количество карточек по компиляции из БД
        database_quantity = get_cardsCount_compilation_from_database(
            compilations[i]["id"], city["id"], compilations[i]["gender"]
        )

        # Получаем количество карточек по компиляции через апи
        listing_data = json.dumps({"gender": compilations[i]["gender"], "cityData": city["cityData"]})

        response_public_compilation: Response = api.public_session.post(
            url=f"/compilations/{compilations[i]['slug']}", data=listing_data,
            headers={"Content-Type": "application/json"},
        )
        assert response_public_compilation.status_code == 200
        api_quantity = response_public_compilation.json()["data"]["cards_count"]

        if database_quantity[0]["count"] != 0:
            if (
                    (
                            math.fabs(database_quantity[0]["count"] - api_quantity)
                            // database_quantity[0]["count"]
                    )
                    * 100
            ) > 2:
                comparing_result["status"] = False
                comparing_result["items"].append(
                    {
                        "database_quantity": database_quantity[i]["count"],
                        "api_quantity": api_quantity,
                        "compilation_id": compilations[i]["id"],
                    }
                )

    if comparing_result["status"] != True:
        allure.attach(
            body=json.dumps(comparing_result["items"], indent=4).encode("utf8"),
            attachment_type=AttachmentType.JSON,
            extension=".json",
        )

    return comparing_result["status"]
