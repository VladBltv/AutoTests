from playwright.sync_api import sync_playwright, expect

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

def test_new():
    assert 1 == 1