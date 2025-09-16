import allure
from allure_commons.types import Severity


class TestSubcategories:
    @allure.title("Вывод блока с субкатегориями в листинге")
    @allure.description(
        """Проверяем, что для категории, для которой заданы субкатегории формируется 
        перелинковочный блок со ссылками на подкатегории"""
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    @allure.label("feature", "Состав листинга")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Public")
    @allure.label("layers", "ui")
    def test_subcategories_exist(self, shop):
        with allure.step("Перейти на страницу листинга, который является категорией, в которой созданы субкатегории"):
            shop.listing_page.navigate(slug="platia")
        with allure.step("Проверить, что на странице выводится блок с субкатегориями"):
            shop.listing_page.check_subcategories_exist()

    @allure.title("Локатор для flocktory на странице листинга")
    @allure.description(
        """Проверяем, что на странице листинга присутствует локатор для flocktory class=flocktory-filters-container"""
    )
    @allure.severity(Severity.CRITICAL)
    @allure.suite("Listing")
    @allure.label("feature", "Состав листинга")
    @allure.label("owner", "Potegova")
    @allure.label("service", "Public")
    @allure.label("layers", "ui")
    def test_flocktory_locator_exist(self, shop):
        with allure.step("Перейти на страницу листинга, который является категорией"):
            shop.listing_page.navigate(slug="platia")
        with allure.step("Проверить, что на странице присутствует локатор для flocktory"):
            shop.listing_page.check_flocktory_container_exist()
        with allure.step("Перейти на страницу листинга, который является субкатегорией"):
            shop.listing_page.navigate(slug="povsednevnye-platia")
        with allure.step("Проверить, что на странице присутствует локатор для flocktory"):
            shop.listing_page.check_flocktory_container_exist()
        with allure.step("Перейти на страницу листинга, который является подборкой"):
            shop.listing_page.navigate(slug="zen-odezda")
        with allure.step("Проверить, что на странице присутствует локатор для flocktory"):
            shop.listing_page.check_flocktory_container_exist()
