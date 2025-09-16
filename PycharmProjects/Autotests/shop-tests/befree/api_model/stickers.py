from requests import Response

from befree.api_model import api, db_connection
from utils.data_generation import rand_str, rand_hex


def get_sticker_by_id_from_base(sticker_id):
    query = f"""
        select *
        from product_stickers ps 
        where ps.id = {sticker_id}
    """
    return db_connection.catalog.get_data(query)[0]


def get_sticker_by_id_via_api(sticker_id):
    response: Response = api.private_session.get(url=f"/stickers/{sticker_id}")

    return response.json()


def any_custom_sticker_given():
    custom_sticker_query = """
        select *
        from product_stickers ps 
        where ps.id > 4
        order by ps.id 
        limit 1
    """
    custom_sticker = db_connection.catalog.get_data(custom_sticker_query)

    if len(custom_sticker) == 0:
        data_for_new_sticker = {
            "title": rand_str(n=5),
            "front_color_hex": rand_hex(),
            "front_bg_color_hex": rand_hex(),
            "is_visible": 1,
        }
        response: Response = api.private_session.post(
            url="/stickers", data=data_for_new_sticker
        )
        custom_sticker = get_sticker_by_id_from_base(response.json()["data"]["id"])
    else:
        custom_sticker = custom_sticker[0]

    return custom_sticker


def empty_sticker_given():
    existing_sticker_query = """
        select *
        from product_stickers ps 
        where ps.products_count = 0 and ps.id > 4 and ps.is_visible is true
        order by ps.id desc 
        limit 1
    """

    empty_sticker = db_connection.catalog.get_data(existing_sticker_query)

    if len(empty_sticker) == 0:
        data_for_new_sticker = {
            "title": rand_str(n=5),
            "front_color_hex": rand_hex(),
            "front_bg_color_hex": rand_hex(),
            "is_visible": 1,
        }
        response: Response = api.private_session.post(
            url="/stickers", data=data_for_new_sticker
        )
        empty_sticker = get_sticker_by_id_from_base(response.json()["data"]["id"])
    else:
        empty_sticker = empty_sticker[0]

    return empty_sticker


def sticker_with_products_given():
    existing_sticker_query = """
        select *
        from product_stickers ps 
        where ps.products_count > 1 and ps.id > 4 and ps.is_visible is true
        order by ps.id desc 
        limit 1
    """

    product_articles_query = """
        select p.article 
        from products p  
        where p.deleted_at is null
        order by p.id desc 
        limit 2
    """

    sticker_with_product = db_connection.catalog.get_data(existing_sticker_query)
    product_articles = db_connection.catalog.get_data(product_articles_query)

    if len(sticker_with_product) == 0:
        data_for_new_sticker = {
            "title": rand_str(n=5),
            "front_color_hex": rand_hex(),
            "front_bg_color_hex": rand_hex(),
            "is_visible": 1,
            "products_articles": ",".join([i["article"] for i in product_articles]),
        }

        response_post: Response = api.private_session.post(
            url="/stickers", data=data_for_new_sticker
        )

        sticker_with_product = get_sticker_by_id_from_base(
            response_post.json()["data"]["id"]
        )
    else:
        sticker_with_product = sticker_with_product[0]

    return sticker_with_product


def get_10_products_without_custom_sticker():
    query = """
        select p.article 
        from products p  
        where p.deleted_at is null and p.sticker_custom is null
        order by p.id desc 
        limit 10
    """

    product_articles = db_connection.catalog.get_data(query)

    return product_articles


def get_any_products_with_custom_sticker():
    query = """
        select string_agg(p.article::character varying, ',') as articles, p.sticker_custom 
        from products p  
        where p.sticker_custom is not null
        group by p.sticker_custom
        limit  1
    """

    product_articles = db_connection.catalog.get_data(query)

    return product_articles


def get_products_by_sticker_id(sticker_id):
    query = f"""
        select p.article 
        from products p  
        where p.sticker_custom = {sticker_id}
    """

    product_articles = db_connection.catalog.get_data(query)

    return product_articles


def edit_with_list_of_articles(
    sticker,
    products_articles,
    action_flag,
):
    request_data = {
        "title": sticker["title"],
        "front_color_hex": sticker["front_color_hex"],
        "front_bg_color_hex": sticker["front_bg_color_hex"],
        "products_articles": products_articles,
        "is_visible": "1",
        "_method": "PUT",
        "product_action_flag": action_flag,
    }

    sticker_id = sticker["id"]
    response_post: Response = api.private_session.post(
        url=f"/stickers/{sticker_id}", data=request_data
    )

    assert response_post.status_code == 200
