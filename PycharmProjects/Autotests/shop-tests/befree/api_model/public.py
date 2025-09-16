def set_cookie(browser, cookie_name, cookie_value):
    cookie = dict()
    cookie["name"] = cookie_name
    cookie["value"] = cookie_value
    browser.driver.add_cookie(cookie_dict=cookie)
