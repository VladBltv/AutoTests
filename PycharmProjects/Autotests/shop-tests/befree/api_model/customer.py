import json
from befree.api_model import api
from mimesis import Person, Datetime
from requests import Response


class Customer:
    def __init__(self, email, password, **kwargs):
        self.email = email
        self.password = password

    def register(self, **kwargs):
        person = Person("en")
        date = Datetime()

        first_name = person.first_name()
        last_name = person.last_name()

        date_of_birth = date.formatted_date("%Y-%m-%d")
        phone = person.phone_number(mask="+7-(###)-###-##-##")

        query_data = json.dumps(
            {
                "email": self.email,
                "password": self.password,
                "password_confirmation": self.password,
                "first_name": first_name,
                "last_name": last_name,
                "gender": "Female",
                "date_of_birth": date_of_birth,
                "phone": phone,
                "MindBox": {
                    "endpointId": "BefreeIOS",
                    "UUID": "",
                },
            }
        )

        response_register: Response = api.monolith_session.post(
            url="/register",
            data=query_data,
            headers={"Content-Type": "application/json"},
        )
        return response_register

    def login(self, **kwargs):
        query_data = json.dumps(
            {
                "email": self.email,
                "password": self.password,
                "MindBox": {
                    "endpointId": "BefreeIOS",
                    "UUID": "",
                },
            }
        )
        response_login: Response = api.monolith_session.post(
            url="/login",
            data=query_data,
            headers={"Content-Type": "application/json"},
        )
        return response_login

    def get_customer(self, token, **kwargs):
        response: Response = api.monolith_session.get(
            url="/customer",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )
        return response
