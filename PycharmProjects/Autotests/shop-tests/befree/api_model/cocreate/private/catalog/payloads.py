import json


class Payloads:
    def get_compilations(self, **kwargs):
        payload = {}
        filter_opts = {}

        public_title = kwargs.pop("public_title") if "public_title" in kwargs else None
        filter_opts["with_deleted"] = kwargs.pop("with_deleted") if "with_deleted" in kwargs else None
        filter_opts["is_category"] = kwargs.pop("is_category") if "is_category" in kwargs else None
        filter_opts["parent_id"] = kwargs.pop("parent_id") if "parent_id" in kwargs else None
        filter_opts["gender"] = kwargs.pop("gender") if "gender" in kwargs else None

        if not all(value is None for value in filter_opts.values()):
            payload["filter"] = {}
            for key in filter_opts:
                if filter_opts[key] is not None:
                    payload["filter"][key] = filter_opts[key]

        if public_title is not None:
            payload["search"] = {}
            payload["search"]["public_title"] = public_title

        return json.dumps(payload)
