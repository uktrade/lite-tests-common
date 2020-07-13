import os

from selenium import webdriver
from _pytest.fixtures import fixture
from ..fixtures.cci import enable_browser_stack


@fixture(scope="session", autouse=True)
def driver():
    driver = build_driver()
    # TODO: replace with more apt name such as # IS_TARGETING_LOCAL_ENVIRONMENT
    if os.getenv("TEST_TYPE_BROWSER_STACK", "False") == "True":
        grant_driver_remote_access(driver)
    
    yield driver

    driver.close()
    driver.quit()