import os
import time
import random
from pathlib import Path
from typing import Optional, Generator
from contextlib import contextmanager
from playwright.sync_api import sync_playwright, BrowserContext, Page

from config.config import SESSION_DIR, AppConfig

CHROME_PROFILE_DIR = SESSION_DIR / "chrome_profile"
CHROME_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

STEALTH_JS = """
// Mask navigator.webdriver
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// Mock plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});

// Mock languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

// Mock chrome runtime
window.chrome = {
    runtime: {},
    loadTimes: function() {},
    csi: function() {},
    app: {}
};
"""


class BrowserManager:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self._playwright = None
        self.context: Optional[BrowserContext] = None

    def start(self) -> BrowserContext:
        self._playwright = sync_playwright().start()

        # Launch persistent context using system Google Chrome
        self.context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE_DIR),
            channel="chrome",
            headless=self.headless,
            viewport={"width": 1440, "height": 900},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--start-maximized",
            ],
            ignore_default_args=["--enable-automation"],
        )

        # Inject stealth scripts to every newly created page
        self.context.add_init_script(STEALTH_JS)
        return self.context

    def stop(self):
        if self.context:
            try:
                self.context.close()
            except Exception:
                pass
            self.context = None
        if self._playwright:
            try:
                self._playwright.stop()
            except Exception:
                pass
            self._playwright = None


@contextmanager
def get_browser(headless: bool = False) -> Generator[BrowserContext, None, None]:
    manager = BrowserManager(headless=headless)
    context = manager.start()
    try:
        yield context
    finally:
        manager.stop()


def human_delay(min_sec: float = 2.0, max_sec: float = 4.5):
    """Add a randomized human delay to prevent heuristic bot triggers."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def human_type(page: Page, selector: str, text: str, delay_range: tuple = (40, 110)):
    """Type text into an input field with randomized human typing speed."""
    element = page.locator(selector).first
    element.click()
    element.fill("")  # Clear field first
    for char in text:
        element.type(char, delay=random.randint(*delay_range))


def smooth_scroll(page: Page, steps: int = 5, distance: int = 300):
    """Smoothly scroll the page to simulate human reading."""
    for _ in range(steps):
        page.mouse.wheel(0, distance)
        time.sleep(random.uniform(0.3, 0.7))
