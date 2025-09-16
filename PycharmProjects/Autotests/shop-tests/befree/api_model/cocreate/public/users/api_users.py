from .endpoints import Endpoints
from .payloads import Payloads
from befree.api_model.config.headers import Headers

from befree.api_model import api
from requests import Response


class Users:
    def __init__(self):
        self._endpoints = Endpoints()
        self._payloads = Payloads()
        self._headers = Headers()

    def register(self, **kwargs):
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.register_user,
            data=self._payloads.register(**kwargs),
            headers=self._headers.common,
        )

        return response

    def login(self, **kwargs):
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.login_user,
            data=self._payloads.login(**kwargs),
            headers=self._headers.common,
        )

        return response

    def update(self, current_data, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.update_user,
            data=self._payloads.update_user(current_data=current_data, **kwargs),
            headers={**self._headers.common, **token},
        )

        return response

    def get_one(self, user_id, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.get_user(user_id=user_id),
            headers={**self._headers.common, **token},
        )

        return response

    def update_avatar(self, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.update_avatar,
            files=self._payloads.set_avatar(**kwargs),
            headers=token,
        )

        return response

    def delete_avatar(self, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.delete_avatar,
            headers={**self._headers.common, **token},
        )

        return response

    def verify_send(self, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.verify_send,
            data=self._payloads.get_code(**kwargs),
            headers={**self._headers.common, **token},
        )

        return response

    def verify_check(self, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.verify_check,
            data=self._payloads.check_code(**kwargs),
            headers={**self._headers.common, **token},
        )

        return response

    def get_likes(self, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.get_likes,
            headers={**self._headers.common, **token},
        )

        return response
