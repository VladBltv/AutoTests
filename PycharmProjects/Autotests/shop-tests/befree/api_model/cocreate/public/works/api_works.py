from .endpoints import Endpoints
from .payloads import Payloads
from befree.api_model.config.headers import Headers

from befree.api_model import api
from requests import Response


class Works:
    def __init__(self):
        self._endpoints = Endpoints()
        self._payloads = Payloads()
        self._headers = Headers()

    def create(self, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.create_work,
            data=self._payloads.create_work(**kwargs),
            files=self._payloads.files(**kwargs),
            headers={**token},
        )

        return response

    def update(self, work_id, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.update_work(work_id=work_id),
            data=self._payloads.update_work(**kwargs),
            files=self._payloads.files(**kwargs),
            headers={**token},
        )

        return response

    def get_list(self, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.get_works,
            data=self._payloads.get_works(**kwargs),
            headers={**self._headers.common, **token},
        )

        return response

    def get_one(self, work_id, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.get_work(work_id=work_id),
            headers={**self._headers.common, **token},
        )

        return response

    def delete(self, work_id, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.delete_work(work_id=work_id),
            headers={**self._headers.common, **token},
        )

        return response

    def get_likes(self, work_id, **kwargs):
        token = dict()
        token["Authorization"] = f"Bearer {kwargs.pop('token') if 'token' in kwargs else ''}"
        response: Response = api.cocreate_public_session.post(
            url=self._endpoints.get_likes(work_id=work_id),
            headers={**self._headers.common, **token},
        )

        return response
