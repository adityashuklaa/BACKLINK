"""
Human-like browser interaction — typing, clicking, scrolling, overlay dismissal.
Makes the bot indistinguishable from a real user.
"""
import math
import random
import time
import logging

log = logging.getLogger("backlink")


def _bezier_point(t, p0, p1, p2):
    """Quadratic bezier curve point at parameter t."""
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def _bezier_move(page, from_x, from_y, to_x, to_y):
    """Move mouse along a curved bezier path (not straight line)."""
    # Random control point offset for natural curve
    mid_x = (from_x + to_x) / 2 + random.randint(-100, 100)
    mid_y = (from_y + to_y) / 2 + random.randint(-80, 80)

    steps = random.randint(10, 18)
    for i in range(steps + 1):
        t = i / steps
        x = _bezier_point(t, from_x, mid_x, to_x)
        y = _bezier_point(t, from_y, mid_y, to_y)
        page.mouse.move(x, y)
        time.sleep(random.uniform(0.008, 0.025))


def human_type(page, selector, text, wpm=40):
    """Type text character-by-character like a real human.
    Includes occasional typos, pauses, and natural rhythm.
    """
    try:
        el = page.query_selector(selector)
        if not el:
            # Try waiting briefly
            try:
                page.wait_for_selector(selector, timeout=3000)
                el = page.query_selector(selector)
            except Exception:
                pass
        if not el:
            log.debug("[human] Element not found: %s", selector)
            return False

        # Scroll element into view smoothly
        page.evaluate("(el) => el.scrollIntoView({behavior: 'smooth', block: 'center'})", el)
        time.sleep(random.uniform(0.3, 0.6))

        # Move mouse to element and click
        box = el.bounding_box()
        if box:
            target_x = box["x"] + box["width"] / 2 + random.uniform(-3, 3)
            target_y = box["y"] + box["height"] / 2 + random.uniform(-2, 2)
            # Get current mouse position (approximate from viewport center)
            vp = page.viewport_size
            cur_x = vp["width"] / 2 if vp else 640
            cur_y = vp["height"] / 2 if vp else 400
            _bezier_move(page, cur_x, cur_y, target_x, target_y)
            time.sleep(random.uniform(0.1, 0.2))

        # Click to focus
        el.click()
        time.sleep(random.uniform(0.1, 0.3))

        # Clear existing content
        page.keyboard.press("Control+a")
        time.sleep(random.uniform(0.05, 0.15))
        page.keyboard.press("Delete")
        time.sleep(random.uniform(0.1, 0.3))

        # Type character by character
        chars_typed = 0
        words = text.split(" ")
        for word_idx, word in enumerate(words):
            if word_idx > 0:
                page.keyboard.type(" ", delay=random.randint(30, 80))
                chars_typed += 1

            # 5% chance of typo per word
            typo_pos = -1
            if random.random() < 0.05 and len(word) > 2:
                typo_pos = random.randint(1, len(word) - 1)

            for i, char in enumerate(word):
                if i == typo_pos:
                    # Type wrong char, pause, backspace, type correct
                    wrong = chr(ord(char) + random.choice([-1, 1]))
                    if wrong.isalpha():
                        page.keyboard.type(wrong, delay=random.randint(40, 120))
                        time.sleep(random.uniform(0.15, 0.35))
                        page.keyboard.press("Backspace")
                        time.sleep(random.uniform(0.08, 0.2))

                delay_ms = random.randint(50, 150)
                # Occasional longer pause (simulating thinking)
                if random.random() < 0.03:
                    delay_ms = random.randint(200, 500)

                page.keyboard.type(char, delay=delay_ms)
                chars_typed += 1

        log.debug("[human] Typed %d chars into %s", chars_typed, selector)
        return True

    except Exception as e:
        log.warning("[human] human_type failed for %s: %s", selector, e)
        return False


def human_click(page, selector_or_element):
    """Click an element with natural mouse movement and hover."""
    try:
        if isinstance(selector_or_element, str):
            # Try multiple selectors if comma-separated
            selectors = [s.strip() for s in selector_or_element.split(",")]
            el = None
            for sel in selectors:
                el = page.query_selector(sel)
                if el:
                    break
            if not el:
                # Wait briefly
                try:
                    page.wait_for_selector(selectors[0], timeout=3000)
                    el = page.query_selector(selectors[0])
                except Exception:
                    pass
            if not el:
                log.debug("[human] Click target not found: %s", selector_or_element)
                return False
        else:
            el = selector_or_element

        # Scroll into view
        page.evaluate("(el) => el.scrollIntoView({behavior: 'smooth', block: 'center'})", el)
        time.sleep(random.uniform(0.2, 0.5))

        box = el.bounding_box()
        if not box:
            el.click()
            return True

        # Target with slight random offset (humans don't hit dead center)
        target_x = box["x"] + box["width"] / 2 + random.uniform(-4, 4)
        target_y = box["y"] + box["height"] / 2 + random.uniform(-3, 3)

        # Get approximate current position
        vp = page.viewport_size
        cur_x = vp["width"] / 2 if vp else 640
        cur_y = vp["height"] / 2 if vp else 400

        # Bezier curve movement
        _bezier_move(page, cur_x, cur_y, target_x, target_y)

        # Hover pause
        time.sleep(random.uniform(0.1, 0.3))

        # Click
        page.mouse.click(target_x, target_y)
        time.sleep(random.uniform(0.1, 0.2))

        log.debug("[human] Clicked element")
        return True

    except Exception as e:
        log.warning("[human] human_click failed: %s", e)
        return False


def human_scroll(page, direction="down", pixels=300):
    """Smooth scroll using mouse wheel with natural speed variation."""
    try:
        multiplier = 1 if direction == "down" else -1
        remaining = abs(pixels)

        while remaining > 0:
            chunk = min(remaining, random.randint(50, 100))
            page.mouse.wheel(0, chunk * multiplier)
            remaining -= chunk
            time.sleep(random.uniform(0.05, 0.15))

    except Exception as e:
        log.debug("[human] Scroll failed: %s", e)


def human_wait(min_s=0.5, max_s=2.0):
    """Random pause simulating reading or thinking."""
    time.sleep(random.uniform(min_s, max_s))


def dismiss_overlays(page):
    """Find and close cookie banners, consent popups, newsletter modals."""
    selectors = [
        "#onetrust-accept-btn-handler",
        "[id*='cookie'] button",
        "[class*='cookie'] button",
        "[id*='consent'] button",
        ".cc-dismiss", ".cc-accept",
        "[aria-label*='accept']", "[aria-label*='Accept']",
        "[aria-label*='cookie']", "[aria-label*='Cookie']",
        'button:has-text("Accept")', 'button:has-text("Accept All")',
        'button:has-text("Accept all")',
        'button:has-text("Got it")', 'button:has-text("OK")',
        'button:has-text("I agree")', 'button:has-text("Agree")',
        '[class*="modal"] [class*="close"]',
        '[class*="popup"] [class*="close"]',
        'button:has-text("Close")', '[aria-label="Close"]',
        'button:has-text("No thanks")', 'button:has-text("Maybe later")',
        '[id*="dismiss"]', '[class*="dismiss"]',
        '[data-testid*="close"]', '[data-testid*="accept"]',
    ]

    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click(timeout=500)
                time.sleep(random.uniform(0.2, 0.5))
                return
        except Exception:
            pass


def random_mouse_movement(page):
    """Move mouse to 2-4 random positions simulating page scanning."""
    try:
        vp = page.viewport_size
        if not vp:
            return
        w, h = vp["width"], vp["height"]

        # Start from a reasonable position
        cur_x = w / 2
        cur_y = h / 3

        moves = random.randint(2, 4)
        for _ in range(moves):
            # Random target within viewport (avoiding edges)
            target_x = random.uniform(w * 0.1, w * 0.9)
            target_y = random.uniform(h * 0.1, h * 0.85)

            _bezier_move(page, cur_x, cur_y, target_x, target_y)
            time.sleep(random.uniform(0.2, 0.5))

            cur_x, cur_y = target_x, target_y

    except Exception as e:
        log.debug("[human] Mouse movement failed: %s", e)
