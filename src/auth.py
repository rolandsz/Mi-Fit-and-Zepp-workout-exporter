import logging
from typing import Optional

from furl import furl
from install_playwright import install

from src import constants

_logger = logging.getLogger(__name__)


def _get_gdpr_url() -> str:
    return furl(
        "https://user.huami.com/privacy2/index.html",
        args={
            "platform_app": constants.APP_NAME,
            "loginPlatform": constants.APP_PLATFORM,
        },
    ).url


def get_app_token() -> Optional[str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        _logger.error(
            "Couldn't find playwright, "
            "please provide the token manually using the -t argument"
        )
        return None

    with sync_playwright() as playwright:
        install(playwright.firefox)
        browser = playwright.firefox.launch(headless=False)
        page = browser.new_page()

        _logger.info("Opening GDPR URL")
        page.goto(_get_gdpr_url())

        _logger.info("Waiting for export data button to appear")
        export_data_locator = page.locator("div.gdpr-operation-output")
        export_data_locator.click()

        _logger.info("Waiting for login")
        export_data_locator = page.locator("div.gdpr-operation-output")
        export_data_locator.wait_for(timeout=0)

        if not (
            token_cookie := next(
                (c for c in page.context.cookies() if c["name"] == "apptoken"), None
            )
        ):
            _logger.error(
                "Couldn't extract the app token automatically, "
                "please provide it manually using the -t argument"
            )
            return None

        browser.close()
        return token_cookie["value"]
