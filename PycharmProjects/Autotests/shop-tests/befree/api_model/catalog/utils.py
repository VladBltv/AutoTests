import allure
from mimesis import Text

from befree.api_model.catalog.private import CatalogPrivate


class Utils(CatalogPrivate):
    def generate_compilation_by_articles(self, articles: []):
        """Создание подборки от товаров"""
        with allure.step("Создаем поборку от товаров"):
            create_response = self.api_compilations.create(
                title=Text("ru").sentence()[:50],
                slug=" ".join(Text("en").words(quantity=3)),
                filter_type="products",
                product_action_flag="add"
            )
            assert create_response.status_code == 200
            compilation_id = create_response.json()["data"]["id"]

        with allure.step("Добавляем товары в подборку"):
            update_response = self.api_compilations.update(
                compilation_id=compilation_id,
                title=create_response.json()["data"]["public_title"],
                slug=create_response.json()["data"]["slug"],
                filter_type="products",
                product_action_flag="add",
                product_articles=articles
            )
            assert update_response.status_code == 200

        return update_response.json()
