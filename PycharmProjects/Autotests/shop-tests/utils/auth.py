import json
from requests import Response, request


def get_token(host, client, secret):
    if client == "2":
        query_data = json.dumps(
            {
                "clientId": client,
                "clientSecret": secret,
                "login": "bf-it-shop-test1",
                "password": "#NoMartiniNoParty80",
            }
        )
    if client == "3":
        query_data = json.dumps(
            {
                "clientId": client,
                "clientSecret": secret,
                "login": "bf-it-cocr-test1",
                "password": "#LetMeSeeYouStripped09",
            }
        )
    response: Response = request(
        "post",
        url=f"{host}/auth",
        headers={"Content-Type": "application/json"},
        data=query_data,
    )
    return response.json()["token"]
