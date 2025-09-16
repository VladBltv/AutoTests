from voluptuous import PREVENT_EXTRA, ALLOW_EXTRA, Schema, Boolean, Any

cms_contests_list = Schema(
    {
        "data": {
            "contests": [
                {
                    "id": int,
                    "title": str,
                    "status": {"key": str, "value": str},
                    "visible": Boolean(),
                    "createdAt": str,
                }
            ]
        },
        "status": str,
        "pagination": {
            "total": int,
            "perPage": int,
            "currentPage": int,
            "lastPage": int,
        },
    },
    extra=PREVENT_EXTRA,
    required=True,
)
