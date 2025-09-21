import pytest
from pages.create_course_page import CreateCoursePage
from playwright.sync_api import Page

@pytest.fixture(scope='function')
def create_course_page(chromium_page_with_state: Page) -> CreateCoursePage:
    return CreateCoursePage(chromium_page_with_state)