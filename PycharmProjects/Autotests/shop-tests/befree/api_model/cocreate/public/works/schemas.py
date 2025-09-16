from voluptuous import PREVENT_EXTRA, ALLOW_EXTRA, Schema, Boolean, Any

update_work_request_schema = Schema(
    {"id": int, "contest": Any(int, None), "title": str, "description": str, "cover": str},
    extra=ALLOW_EXTRA,
    required=False,
)
