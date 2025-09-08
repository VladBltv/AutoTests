from playwright.sync_api import sync_playwright, expect
import pytest

ver = 1.0
@pytest.mark.skipif(ver == 1.0, reason='Для версии 1.0 тест не доступен')
def test_description():
    '''
    Проверяем что все аккардеоны закрыты
    '''
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://shop-fe-qa03.befree.ru/zhenskaya/product/BF2535346016/50?size=19')
        accordionitems = page.locator('//div[@data-bui-id="AccordionItem"]')
        count = accordionitems.count()
        for i in range(count):
            accordionitem = page.locator(f'//div[@data-bui-id="AccordionItem"][{i+1}]').locator('xpath=.//div[@style]')
            expect(accordionitem).to_have_attribute('style', 'max-height:0')
        context.storage_state(path='new_context.json')

@pytest.mark.skip(reason='По кайфу')
def test_new():
    assert 1 == 1

@pytest.mark.xfail(reason='Ну вот так вот')
def test_new1():
    assert 1 == 2

@pytest.mark.xfail
def test_new2():
    assert 1 == 1
