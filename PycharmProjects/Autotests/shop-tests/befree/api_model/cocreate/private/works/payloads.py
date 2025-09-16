import json

from befree.api_model.cocreate.private.works.schemas import cms_work_update
from utils import helpers


class Payloads:
    def get_works(self, query, page, per_page, **kwargs):
        """Get works payload. status and contest_id are optional."""
        filter = {}
        if "status" in kwargs:
            filter["status"] = kwargs.pop("status")
        if "contest_id" in kwargs:
            filter["contestId"] = kwargs.pop("contest_id")

        payload = json.dumps(
            {
                "query": query,
                "filter": filter,
                "page": page,
                "perPage": per_page,
            }
        )
        return payload

    def update_work(self, current_data, **kwargs):
        schema = cms_work_update
        current_data["status"] = current_data["status"]["key"]
        payload = helpers.get_payload_for_update(current_data=current_data, schema=schema, **kwargs)

        return json.dumps(payload)
