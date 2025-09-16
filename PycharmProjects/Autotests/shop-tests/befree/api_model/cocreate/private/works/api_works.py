from .endpoints import Endpoints
from .payloads import Payloads
from befree.api_model.config.headers import Headers
from befree.api_model import api
from requests import Response
from befree.api_model.cocreate.enums import WorkStatus


class Works:
    def __init__(self):
        self._endpoints = Endpoints()
        self._payloads = Payloads()
        self._headers = Headers()

    def get_list(self, query="", page=1, per_page=10, **kwargs):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_works,
            data=self._payloads.get_works(query=query, page=page, per_page=per_page, **kwargs),
            headers=self._headers.common,
        )
        return response

    def get_one(self, work_id):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.get_work(work_id=work_id),
            headers=self._headers.common,
        )
        return response

    def delete(self, work_id):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.delete_work(work_id=work_id),
            headers=self._headers.common,
        )
        return response

    def update(self, work_id, current_data, **kwargs):
        response: Response = api.cocreate_private_session.post(
            url=self._endpoints.update_work(work_id=work_id),
            data=self._payloads.update_work(current_data=current_data, **kwargs),
            headers=self._headers.common,
        )
        return response
