from requests import Response
from befree.api_model import api, db_connection
import allure
from allure_commons.types import AttachmentType
import json


def random_from_database():
    query = f"""
        select p.id, p.article, p.title, p.marketing_title, p.category_id, c.public_title, c.slug, p.gender  
        from products p 
        join compilations c on c.id = p.category_id
        where p.marketing_title is not null
        limit 1
    """
    return db_connection.catalog.get_data(query)


def get_via_api(product_article, city_kladr):
    response_product_card: Response = api.public_session.get(url=f"/products/{product_article}?city={city_kladr}")
    assert response_product_card.status_code == 200

    return response_product_card.json()["data"]


def random_from_database_without_stickers():
    query = f"""
        select  p.id, p.article, p.title, p.marketing_title, p.category_id, p.gender
        from products p 
        where p.sticker_new = false and p.sticker_hit =false and p.sticker_custom is null
        limit 1
    """
    return db_connection.catalog.get_data(query)


def check_stickers(product_article, kladr, list_of_stickers):
    product_api = get_via_api(product_article, kladr)

    assert len(product_api["stickers"]) == len(list_of_stickers), "Неверное количество стикеров"

    for i in range(0, len(list_of_stickers)):
        assert product_api["stickers"][i]["id"] == list_of_stickers[i]["id"] and product_api["stickers"][i]["text"] == list_of_stickers[i]["title"]


def with_condition_from_database(param, condition, value):
    query = f"""
        select  p.id, p.article, v.calculated_price_level_0
        from products p 
        join variations v on v.product_id = p.id
        where p.deleted_at is null and {param} {condition} {value}
        limit 1
    """
    return db_connection.catalog.get_data(query)


def compare_colors(reference, api):
    # Инициализация
    comparing_result = dict()
    comparing_result["status"] = True
    comparing_result["items"] = []

    # сравниваем количество цветом
    assert len(reference) == len(api), "Не совпадает количество цветов"

    # сравниваем по цветам
    for i in range(0, len(reference)):
        if (
            reference[i]["color_id"] != api[i]["color_id"]
            or reference[i]["color_code_id"] != api[i]["color_code_id"]
            or reference[i]["enable"] != api[i]["enable"]
        ):
            comparing_result["status"] = False
            comparing_result["items"].append(
                {
                    "actual_result": api[i],
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


def compare_variations(reference, api):
    # Инициализация
    comparing_result = dict()
    comparing_result["status"] = True
    comparing_result["items"] = []

    # сравниваем количество вариантов
    assert len(reference) == len(api), "Не совпадает количество вариантов"

    # сравниваем по вариантам
    for i in range(0, len(reference)):
        if reference[i]["id"] != api[i]["id"] or reference[i]["sku"] != api[i]["sku"]:
            comparing_result["status"] = False
            comparing_result["items"].append(
                {
                    "actual_result": api[i],
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


def get_undeleted_variation():
    query = f"""
           select p.id as product_id, p.article , v.id as variation_id, v.sku 
            from variations v 
            join products p on p.id = v.product_id 
            where p.deleted_at  is null and v.deleted_at is null 
            limit 1
       """

    request = db_connection.catalog.get_data(query)
    return (
        request[0]["product_id"],
        request[0]["article"],
        request[0]["variation_id"],
        request[0]["sku"],
    )


def get_article_by_variation_id(variation_id):
    query = f"""
                select p.article , v.color_code_id , v.size_id
                from products p
                join variations v on v.product_id  = p.id
                where v.id = {variation_id}
           """

    request = db_connection.catalog.get_data(query)
    return (
        request[0]["article"],
        request[0]["color_code_id"],
        request[0]["size_id"],
    )
