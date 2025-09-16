import re
from playwright.sync_api import Page, expect, Request
from typing import Dict, Any, List


# def test_has_title(page: Page) -> None:
#     page.goto("https://cocreate.befree.ru/")
#
#     # Expect a title "to contain" a substring.
#     expect(page).to_have_title(re.compile("Объединяем таланты"))


# def test_get_started_link(page: Page) -> None:
#     page.goto("https://playwright.dev/")
#
#     # Click the get started link.
#     page.get_by_role("link", name="Get started").click()
#
#     # Expects page to have a heading with the name of Installation.
#     expect(page.get_by_role("heading", name="Installation")).to_be_visible()


# def test_add_todo(page: Page) -> None:
#     page.goto("https://demo.playwright.dev/todomvc/#/")
#     page.get_by_placeholder("What needs to be done?").click()
#     page.get_by_placeholder("What needs to be done?").fill("Создать первый сценарий playwright")
#     page.get_by_placeholder("What needs to be done?").press("Enter")


def test_success_registration_desc(shop_page):
    shop_page.goto(url="/zhenskaya")
    shop_page.locator(".sc-5850cff1-0 > .sc-2b366990-0").click()
    shop_page.get_by_text("создать").click()
    shop_page.locator("#firstName").click()
    shop_page.locator("#firstName").fill("Test")
    shop_page.locator("#lastName").click()
    shop_page.locator("#lastName").fill("Test")
    shop_page.locator("#email").click()
    shop_page.locator("#email").fill("test@test123.ru")
    shop_page.locator("#phone").click()
    shop_page.locator("#phone").fill("+7 (123) 456-78-90")
    shop_page.get_by_test_id("signup-form-input-gender").click()
    shop_page.get_by_test_id("signup-form-input-gender").get_by_text("женский").click()
    shop_page.get_by_test_id("signup-form-input-birthDate").get_by_role("textbox").click()
    shop_page.get_by_test_id("signup-form-input-birthDate").get_by_role("textbox").fill("2000-10-10")
    shop_page.locator("#password").click()
    shop_page.locator("#password").fill("aA123456")
    shop_page.locator("#repeatPassword").click()
    shop_page.locator("#repeatPassword").fill("aA123456")
    shop_page.get_by_test_id("signup-form-button-submit").click()
    expect(shop_page.get_by_text("личный кабинет")).to_be_visible()

def test_handle_and_inspect_requests(shop_page: Page) -> None:
    # Example 1: Basic request interception
    def handle_request(route):
        request = route.request
        print(f"Request URL: {request.url}")
        print(f"Request Method: {request.method}")
        print(f"Request Headers: {request.headers}")
        
        # Check if request has specific parameters
        if "search" in request.url:
            print(f"Search query: {request.url.split('search=')[1]}")
        
        # Continue the request
        route.continue_()
    
    # Enable request interception
    shop_page.route("**/*", handle_request)
    
    # Navigate to the page
    shop_page.goto("/")
    
    # Example 2: Wait for specific request and check its parameters
    with shop_page.expect_request("**/api/*") as request_info:
        # Perform action that triggers the request
        shop_page.get_by_role("link", name="женская одежда").click()
    
    request = request_info.value
    print(f"Intercepted API Request: {request.url}")
    print(f"Request Method: {request.method}")
    
    # Example 3: Wait for response and check its content
    with shop_page.expect_response("**/api/*") as response_info:
        # Perform action that triggers the request
        shop_page.get_by_role("link", name="платья").click()
    
    response = response_info.value
    print(f"Response Status: {response.status}")
    print(f"Response Headers: {response.headers}")
    
    # Example 4: Mock a response for specific requests
    def mock_response(route):
        if "api/products" in route.request.url:
            route.fulfill(
                status=200,
                content_type="application/json",
                body='{"products": ["product1", "product2"]}'
            )
        else:
            route.continue_()
    
    shop_page.route("**/*", mock_response)
    
    # Example 5: Check request body for POST requests
    def check_post_request(route):
        request = route.request
        if request.method == "POST":
            try:
                body = request.post_data
                print(f"POST Request Body: {body}")
            except:
                print("No POST data available")
        route.continue_()
    
    shop_page.route("**/*", check_post_request)
    
    # Example 6: Block specific requests
    def block_resources(route):
        if route.request.resource_type in ["image", "stylesheet", "font"]:
            route.abort()
        else:
            route.continue_()
    
    shop_page.route("**/*", block_resources)
    
    # Example 7: Wait for network idle
    shop_page.wait_for_load_state("networkidle")

def test_advanced_request_handling(shop_page: Page) -> None:
    # Create a list to store request data
    requests_data: List[Dict[str, Any]] = []
    
    def collect_request_data(route):
        request = route.request
        requests_data.append({
            "url": request.url,
            "method": request.method,
            "headers": request.headers,
            "resource_type": request.resource_type,
            "is_navigation_request": request.is_navigation_request(),
            "post_data": request.post_data if request.method == "POST" else None
        })
        route.continue_()
    
    # Enable request collection
    shop_page.route("**/*", collect_request_data)
    
    # Navigate and perform actions
    shop_page.goto("/")
    shop_page.get_by_role("link", name="женская одежда").click()
    
    # Wait for network idle
    shop_page.wait_for_load_state("networkidle")
    
    # Analyze collected requests
    for request in requests_data:
        print("\nRequest Details:")
        print(f"URL: {request['url']}")
        print(f"Method: {request['method']}")
        print(f"Resource Type: {request['resource_type']}")
        if request['post_data']:
            print(f"POST Data: {request['post_data']}")
    
    # Example: Check for specific API calls
    api_requests = [r for r in requests_data if "api" in r["url"]]
    print(f"\nFound {len(api_requests)} API requests")

def test_handle_product_card_clicks(shop_page: Page) -> None:
    # Template for handling product card click parameters
    def handle_product_clicks(route):
        request = route.request
        url = request.url
        
        # Pattern to match product card click URLs
        # Example URL: https://befree.ru/product/123?click=card&position=1&category=women
        product_click_pattern = r"https://befree\.ru/product/\d+\?.*"
        
        if re.match(product_click_pattern, url):
            # Parse URL parameters
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # Extract specific parameters
            product_id = parsed_url.path.split('/')[-1]
            click_type = query_params.get('click', [''])[0]
            position = query_params.get('position', [''])[0]
            category = query_params.get('category', [''])[0]
            
            print("Product Card Click Detected:")
            print(f"Product ID: {product_id}")
            print(f"Click Type: {click_type}")
            print(f"Position: {position}")
            print(f"Category: {category}")
            
            # You can add assertions or validations here
            assert click_type == "card", "Click type should be 'card'"
            assert position.isdigit(), "Position should be a number"
            
        route.continue_()
    
    # Enable request handling
    shop_page.route("**/*", handle_product_clicks)
    
    # Navigate to a product listing page
    shop_page.goto("/zhenskaya")
    
    # Click on a product card (example)
    shop_page.locator(".product-card").first.click()
    
    # Wait for network idle to ensure all requests are processed
    shop_page.wait_for_load_state("networkidle")
    
    # Alternative: Wait specifically for product click request
    with shop_page.expect_request(lambda request: "product" in request.url and "click=card" in request.url) as request_info:
        shop_page.locator(".product-card").first.click()
    
    request = request_info.value
    print(f"Intercepted Product Click Request: {request.url}")

def test_handle_specific_requests(shop_page: Page) -> None:
    # Example 1: Handle requests by URL pattern
    def handle_by_url_pattern(route):
        request = route.request
        if "api/products" in request.url:
            print(f"Intercepted products API request: {request.url}")
            # You can modify the response
            route.fulfill(
                status=200,
                content_type="application/json",
                body='{"products": ["product1", "product2"]}'
            )
        else:
            route.continue_()
    
    # Example 2: Handle requests by method
    def handle_by_method(route):
        request = route.request
        if request.method == "POST":
            print(f"Intercepted POST request: {request.url}")
            # Log POST data
            if request.post_data:
                print(f"POST data: {request.post_data}")
        route.continue_()
    
    # Example 3: Handle requests by resource type
    def handle_by_resource_type(route):
        request = route.request
        if request.resource_type == "xhr":
            print(f"Intercepted XHR request: {request.url}")
        elif request.resource_type == "fetch":
            print(f"Intercepted fetch request: {request.url}")
        route.continue_()
    
    # Example 4: Handle requests by headers
    def handle_by_headers(route):
        request = route.request
        headers = request.headers
        if "Authorization" in headers:
            print(f"Intercepted authenticated request: {request.url}")
            print(f"Auth token: {headers['Authorization']}")
        route.continue_()
    
    # Example 5: Handle requests by query parameters
    def handle_by_query_params(route):
        request = route.request
        if "search" in request.url:
            search_query = request.url.split("search=")[1].split("&")[0]
            print(f"Intercepted search request with query: {search_query}")
        route.continue_()
    
    # Example 6: Block specific requests
    def block_requests(route):
        request = route.request
        if request.resource_type in ["image", "stylesheet", "font"]:
            print(f"Blocked resource: {request.url}")
            route.abort()
        else:
            route.continue_()
    
    # Example 7: Handle requests with custom conditions
    def handle_custom_conditions(route):
        request = route.request
        url = request.url
        
        # Check multiple conditions
        if (
            request.method == "GET" and
            "api" in url and
            "products" in url and
            request.resource_type == "xhr"
        ):
            print(f"Intercepted specific API request: {url}")
            # Mock response
            route.fulfill(
                status=200,
                content_type="application/json",
                body='{"status": "success", "data": {"products": []}}'
            )
        else:
            route.continue_()
    
    # Example 8: Handle requests with timeout
    def handle_with_timeout(route):
        request = route.request
        if "slow-api" in request.url:
            print(f"Intercepted slow API request: {request.url}")
            # Add delay to response
            import time
            time.sleep(2)  # Simulate slow response
        route.continue_()
    
    # Enable request handling (you can use any of the handlers above)
    shop_page.route("**/*", handle_custom_conditions)
    
    # Navigate to the page
    shop_page.goto("/")
    
    # Wait for network idle
    shop_page.wait_for_load_state("networkidle")
    
    # Example: Wait for specific request and check its parameters
    with shop_page.expect_request("**/api/*") as request_info:
        # Perform action that triggers the request
        shop_page.get_by_role("link", name="женская одежда").click()
    
    request = request_info.value
    print(f"Intercepted API Request: {request.url}")
    
    # Example: Wait for response and check its content
    with shop_page.expect_response("**/api/*") as response_info:
        # Perform action that triggers the request
        shop_page.get_by_role("link", name="платья").click()
    
    response = response_info.value
    print(f"Response Status: {response.status}")

def test_expect_request_with_regex(shop_page: Page) -> None:
    # Example 1: Basic regex pattern matching
    with shop_page.expect_request(re.compile(r"https://befree\.ru/api/products/\d+")) as request_info:
        # Perform action that triggers the request
        shop_page.get_by_role("link", name="женская одежда").click()
    
    request = request_info.value
    print(f"Intercepted request matching product API pattern: {request.url}")
    
    # Example 2: Complex regex pattern with query parameters
    product_click_pattern = re.compile(r"https://befree\.ru/product/\d+\?.*click=card.*")
    with shop_page.expect_request(product_click_pattern) as request_info:
        shop_page.locator(".product-card").first.click()
    
    request = request_info.value
    print(f"Intercepted product card click: {request.url}")
    
    # Example 3: Multiple patterns using list of regex
    patterns = [
        re.compile(r"https://befree\.ru/api/categories"),
        re.compile(r"https://befree\.ru/api/products")
    ]
    with shop_page.expect_request(patterns) as request_info:
        shop_page.get_by_role("link", name="каталог").click()
    
    request = request_info.value
    print(f"Intercepted category or product API request: {request.url}")
    
    # Example 4: Custom regex pattern with lambda
    def custom_pattern(request: Request) -> bool:
        return bool(
            re.match(r"https://befree\.ru/api/.*", request.url) and
            request.method == "POST" and
            "Authorization" in request.headers
        )
    
    with shop_page.expect_request(custom_pattern) as request_info:
        shop_page.get_by_role("button", name="Добавить в корзину").click()
    
    request = request_info.value
    print(f"Intercepted authenticated POST request: {request.url}")
    
    # Example 5: Complex regex with multiple conditions
    def complex_pattern(request: Request) -> bool:
        url_pattern = re.compile(r"https://befree\.ru/api/orders/\d+")
        return bool(
            url_pattern.match(request.url) and
            request.method == "POST" and
            request.resource_type == "xhr" and
            "application/json" in request.headers.get("content-type", "")
        )
    
    with shop_page.expect_request(complex_pattern) as request_info:
        shop_page.get_by_role("button", name="Оформить заказ").click()
    
    request = request_info.value
    print(f"Intercepted order creation request: {request.url}")
    
    # Example 6: Regex with query parameter extraction
    def extract_query_params(request: Request) -> Dict[str, str]:
        if re.match(r"https://befree\.ru/api/search\?", request.url):
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(request.url)
            return dict(parse_qs(parsed.query))
        return {}
    
    with shop_page.expect_request(re.compile(r"https://befree\.ru/api/search\?")) as request_info:
        shop_page.get_by_placeholder("Поиск").fill("платье")
        shop_page.keyboard.press("Enter")
    
    request = request_info.value
    params = extract_query_params(request)
    print(f"Search parameters: {params}")
    
    # Example 7: Regex with response validation
    with shop_page.expect_request(re.compile(r"https://befree\.ru/api/cart")) as request_info:
        with shop_page.expect_response(re.compile(r"https://befree\.ru/api/cart")) as response_info:
            shop_page.get_by_role("button", name="Обновить корзину").click()
            
            request = request_info.value
            response = response_info.value
            
            print(f"Cart update request: {request.url}")
            print(f"Response status: {response.status}")
            print(f"Response body: {response.json()}")