from playwright.sync_api import Page


class Locators:
    def __init__(self, page: Page):
        self.page = page

        self.title = page.get_by_test_id("catalog-title")
        self.counter = page.get_by_test_id("catalog-title-counter")
        self.subcategories = page.get_by_test_id("subcategories")
        self.subcategories_item = lambda name: page.get_by_test_id(f"subcategories-item-{name}")
        self.grid_view = lambda num: page.get_by_test_id(f"catalog-grid-{num}")
        self.filters = page.get_by_test_id("catalog-filters")
        self.listing = page.get_by_test_id("catalog")
        self.product_card = lambda id: page.get_by_test_id(f"product-card-{id}")
        self.product_card_image = lambda id: page.get_by_test_id(f"product-card-{id}-image")
        self.product_card_stickers = lambda id: page.get_by_test_id(f"product-card-{id}-stickers")
        self.product_card_stickers_item = lambda id, num: page.get_by_test_id(f"product-card-{id}-sticker-{num}")
        self.product_card_title = lambda id: page.get_by_test_id(f"product-card-{id}-title")
        self.product_card_price = lambda id: page.get_by_test_id(f"product-card-{id}-price")
        self.product_card_favorities_button = lambda id: page.get_by_test_id(f"product-card-{id}-favorites-button")
        self.breadcrumbs_item = lambda num: page.get_by_test_id(f"breadcrumbs-item-{num}")
        self.pagination = page.get_by_test_id("pagination")
        self.catalog_up_button = page.get_by_test_id("catalog-up-button")
        self.snackbar = page.get_by_test_id("snackbar-container")
        self.flocktory_container = page.locator(".flocktory-filters-container")
