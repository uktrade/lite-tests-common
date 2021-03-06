import os

from selenium import webdriver
from _pytest.fixtures import fixture
from ..fixtures.cci import enable_browser_stack


@fixture(scope="session", autouse=True)
def driver(request, api_client):
    if os.getenv("TEST_TYPE_BROWSER_STACK", "False") == "True":
        driver = enable_browser_stack(request)

        print(
            "Browser stack is running at https://automate.browserstack.com/dashboard/v2/builds/1a806eccbeccef94d17f35c360bb475d04949e21/sessions/"
            + driver.session_id
        )
        yield driver
        driver.close()
        driver.quit()

    else:
        browser = request.config.getoption("--driver")

        chrome_options = webdriver.ChromeOptions()
        if str(os.environ.get("TEST_TYPE_HEADLESS")) == "True":
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Use proxy settings provided in config file for security testing
        if os.environ.get("PROXY_IP_PORT") is not None:
            chrome_options.add_argument("--proxy-server=%s" % str(os.environ.get("PROXY_IP_PORT")))

        if browser == "chrome":
            if str(os.environ.get("ENVIRONMENT")) == "None":
                driver = webdriver.Chrome("chromedriver", options=chrome_options)  # noqa
            else:
                driver = webdriver.Chrome(options=chrome_options)  # noqa
            driver.get("about:blank")
            driver.maximize_window()

            yield driver

            driver.close()
            driver.quit()
        else:
            print("Only Chrome is supported at the moment")
