import json
from befree.api_model import api
from requests import Response


def change_settings_orders(settings):
    query_data = json.dumps({"settings": settings})
    response: Response = api.orders_private_session.post(
        url="/settings/update",
        data=query_data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    return response
