"""
Stealth browser factory with 50-profile rotation.
Every page gets a unique device identity — different browser, OS, GPU, timezone, screen size.
"""
import random
import logging
from playwright.sync_api import sync_playwright
from core.browser_profiles import get_profile, get_fingerprint_script, PROFILES

log = logging.getLogger("backlink")

FINGERPRINT_DOMAINS = ["datadome", "fingerprintjs", "perimeterx", "kasada", "queue-it"]


def get_browser(config: dict, headed_override: bool = False):
    """Launch browser. Returns (pw, browser)."""
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


def new_page(browser, config: dict, site_name: str = ""):
    """Create a stealth context + page with a unique rotated profile.
    Each call gets a different device identity.
    Returns (context, page).
    """
    # Get a unique profile for this session
    profile = get_profile(site_name)
    log.info("[browser] Using profile: %s (%s, %s)",
             profile["id"], profile["platform"], profile["viewport"])

    context = browser.new_context(
        viewport=profile["viewport"],
        user_agent=profile["user_agent"],
        locale=profile["locale"],
        timezone_id=profile["timezone"],
        color_scheme=random.choice(["light", "dark", "no-preference"]),
        java_script_enabled=True,
    )

    # Apply playwright-stealth
    try:
        from playwright_stealth import stealth_sync
        stealth_sync(context)
    except ImportError:
        pass

    # Inject full fingerprint (platform, GPU, memory, cores, webdriver, etc.)
    context.add_init_script(get_fingerprint_script(profile))

    # Block fingerprint detection scripts
    def _block(route):
        route.abort()

    for domain in FINGERPRINT_DOMAINS:
        try:
            context.route(f"**/*{domain}*", _block)
        except Exception:
            pass

    page = context.new_page()
    return context, page
