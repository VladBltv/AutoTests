from befree.api_model.cocreate.private.users.endpoints import Endpoints
from befree.api_model.cocreate.private.users.payloads import Payloads
from befree.api_model.config.headers import Headers

from befree.api_model import api
from requests import Response


class Users:
    def __init__(self):
        self._endpoints = Endpoints()
        self._payloads = Payloads()
        self._headers = Headers()

    def get_list(self, query="", page=1, per_page=10):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_users_list,
            data=self._payloads.get_users_list(query=query, page=page, per_page=per_page),
            headers=self._headers.common,
        )
        return response

    def get_one(self, user_id):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_user(user_id=user_id),
            headers=self._headers.common,
        )
        return response

    def login(self, login, password):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.user_login,
            data=self._payloads.user_login(login=login, password=password),
            headers=self._headers.common,
        )
        return response
