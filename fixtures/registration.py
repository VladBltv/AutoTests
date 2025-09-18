import pytest
from pages.RegistrationPage import RegistrationPage

@pytest.fixture
def init_page(chromium_page_with_state):
    return RegistrationPage(chromium_page_with_state)