from voluptuous import PREVENT_EXTRA, ALLOW_EXTRA, Schema, Boolean, Any

cms_collaborations_list = Schema(
    {
        "data": {
            "collaborations": [
                {
                    "id": int,
                    "title": str,
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