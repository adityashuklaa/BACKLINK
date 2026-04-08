"""
Stealth browser factory — every context gets anti-detection applied.
"""
import random
from playwright.sync_api import sync_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

VIEWPORTS = [
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1536, "height": 864},
    {"width": 1920, "height": 1080},
    {"width": 1280, "height": 800},
]

FINGERPRINT_DOMAINS = ["datadome", "fingerprintjs", "perimeterx", "kasada", "queue-it", "hcaptcha.com/1"]


def get_browser(config: dict, headed_override: bool = False):
    """Launch browser. Returns (pw, browser). Callers use new_page() for pages."""
    browser_cfg = config.get("browser", {})
    headless = not headed_override and browser_cfg.get("headless", True)
    slow_mo = browser_cfg.get("slow_mo_ms", 200)

    proxy_cfg = config.get("proxy", {})
    proxy = None
    if proxy_cfg.get("enabled") and proxy_cfg.get("server"):
        proxy = {"server": proxy_cfg["server"]}

    pw = sync_playwright().start()
    launch_kwargs = {"headless": headless, "slow_mo": slow_mo}
    if proxy:
        launch_kwargs["proxy"] = proxy

    browser = pw.chromium.launch(**launch_kwargs)
    return pw, browser


def new_page(browser, config: dict):
    """Create a stealth context + page. ALWAYS applies anti-detection.
    Returns (context, page). Caller must close context when done.
    """
    viewport = random.choice(VIEWPORTS)
    ua = random.choice(USER_AGENTS)

    context = browser.new_context(
        viewport=viewport,
        user_agent=ua,
        locale="en-US",
        timezone_id="America/New_York",
        java_script_enabled=True,
    )

    # Apply playwright-stealth to EVERY context
    try:
        from playwright_stealth import stealth_sync
        stealth_sync(context)
    except ImportError:
        pass

    # Override navigator.webdriver
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        window.chrome = {runtime: {}};
    """)

    # Block fingerprint detection scripts
    def _block_fingerprints(route):
        route.abort()

    for domain in FINGERPRINT_DOMAINS:
        try:
            context.route(f"**/*{domain}*", _block_fingerprints)
        except Exception:
            pass

    page = context.new_page()
    return context, page
