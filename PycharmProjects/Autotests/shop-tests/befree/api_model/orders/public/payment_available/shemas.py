from voluptuous import PREVENT_EXTRA, Schema, Boolean, Any

payment_available = Schema(
    {
        "data": {
            "paymentMethods": [
                {
                    "key": Any("podeli", "sber", "sbp", "cash"),
                    "title": Any(
                        "подели - оплата по частям",
                        "онлайн",
                        "система быстрых платежей",
                        "при получении",
                    ),
                    "description": str,
                    "helper": str,
                }
            ]
        },
        "status": str,
    },
    extra=PREVENT_EXTRA,
    required=True,
)
