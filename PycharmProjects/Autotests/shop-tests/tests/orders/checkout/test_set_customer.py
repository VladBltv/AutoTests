import allure
from allure_commons.types import Severity


@allure.id("1968")
@allure.title("Сохранение опции подписки для майндбокса")
@allure.description("Проверяем, что опция подписки в заказе сохраняется корректно")
@allure.tag("API Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Checkout")
@allure.label("owner", "Potegova")
@allure.label("service", "Orders")
@allure.label("feature", "Оформление доставки")
def test_set_subscription():
    with allure.step("Создать корзину с нуля"):
        ...

    with allure.step("Проверить, что опция подписки для Mindbox не определена"):
        ...

    with allure.step("На стейте checkout передать значение false"):
        ...

    with allure.step("Проверить, что опция подписки для Mindbox установлена в false"):
        ...

    with allure.step("На стейте checkout передать значение true"):
        ...

    with allure.step("Проверить, что опция подписки для Mindbox установлена в true"):
        ...

    with allure.step("На стейте checkout установить какие либо другие данные"):
        ...

    with allure.step(
        "Проверить, что опция подписки для Mindbox не изменилась и установлена в true"
    ):
        ...

    with allure.step(
        "Оформить заказ без дополнительной передачи флага подписки в методе создания заказа"
    ):
        ...

    with allure.step(
        "Проверить, что опция подписки для Mindbox не изменилась и установлена в true"
    ):
        ...
