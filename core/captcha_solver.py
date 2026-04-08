"""
2Captcha integration for auto-solving reCAPTCHA v2 and hCaptcha.
API docs: https://2captcha.com/2captcha-api
"""
import re
import time
import logging
import requests

log = logging.getLogger("backlink")


class CaptchaSolver:
    def __init__(self, config: dict):
        cfg = config.get("captcha", {})
        self.api_key = cfg.get("api_key", "")
        self.enabled = cfg.get("enabled", False)
        self.timeout_s = cfg.get("timeout_s", 120)

    def is_enabled(self) -> bool:
        return self.enabled and bool(self.api_key)

    def detect_type(self, page) -> tuple:
        """Detect CAPTCHA type and extract sitekey from page.
        Returns (captcha_type, sitekey) or (None, None).
        """
        content = page.content()

        # reCAPTCHA v2 — look for data-sitekey attribute
        m = re.search(r'class="g-recaptcha"[^>]*data-sitekey="([^"]+)"', content)
        if not m:
            m = re.search(r'data-sitekey="([^"]+)"[^>]*class="g-recaptcha"', content)
        if not m:
            m = re.search(r'data-sitekey="([^"]+)"', content)

        if m:
            sitekey = m.group(1)
            # Check if invisible
            if 'data-size="invisible"' in content or "grecaptcha.execute" in content:
                return ("recaptcha_v2_invisible", sitekey)
            return ("recaptcha_v2", sitekey)

        # hCaptcha
        m = re.search(r'class="h-captcha"[^>]*data-sitekey="([^"]+)"', content)
        if not m:
            m = re.search(r'data-sitekey="([^"]+)"[^>]*class="h-captcha"', content)
        if m:
            return ("hcaptcha", m.group(1))

        return (None, None)

    def solve(self, page, url: str) -> bool:
        """Attempt to solve CAPTCHA on the page. Returns True if solved."""
        if not self.is_enabled():
            log.warning("[captcha] Solver disabled or no API key configured")
            return False

        captcha_type, sitekey = self.detect_type(page)
        if not captcha_type or not sitekey:
            log.warning("[captcha] Could not detect CAPTCHA type or extract sitekey")
            return False

        log.info("[captcha] Detected %s (sitekey: %s...)", captcha_type, sitekey[:12])

        request_id = self._submit_task(captcha_type, sitekey, url)
        if not request_id:
            return False

        token = self._poll_result(request_id)
        if not token:
            return False

        return self._inject_token(page, captcha_type, token)

    def _submit_task(self, captcha_type: str, sitekey: str, url: str) -> str | None:
        params = {
            "key": self.api_key,
            "pageurl": url,
            "json": 1,
        }

        if captcha_type.startswith("recaptcha"):
            params["method"] = "userrecaptcha"
            params["googlekey"] = sitekey
            if captcha_type == "recaptcha_v2_invisible":
                params["invisible"] = 1
        elif captcha_type == "hcaptcha":
            params["method"] = "hcaptcha"
            params["sitekey"] = sitekey

        try:
            resp = requests.post("https://2captcha.com/in.php", data=params, timeout=30)
            data = resp.json()
            if data.get("status") == 1:
                request_id = data.get("request")
                log.info("[captcha] Task submitted (id: %s)", request_id)
                return request_id
            else:
                log.error("[captcha] Submit failed: %s", data.get("request", "unknown error"))
                return None
        except Exception as e:
            log.error("[captcha] Submit error: %s", e)
            return None

    def _poll_result(self, request_id: str) -> str | None:
        log.info("[captcha] Waiting 15s before first poll...")
        time.sleep(15)

        elapsed = 15
        while elapsed < self.timeout_s:
            try:
                resp = requests.get("https://2captcha.com/res.php", params={
                    "key": self.api_key,
                    "action": "get",
                    "id": request_id,
                    "json": 1,
                }, timeout=30)
                data = resp.json()

                if data.get("status") == 1:
                    token = data.get("request")
                    log.info("[captcha] Solved successfully (token: %s...)", token[:20])
                    return token
                elif data.get("request") == "CAPCHA_NOT_READY":
                    log.debug("[captcha] Not ready yet, polling again in 5s...")
                else:
                    log.error("[captcha] Poll error: %s", data.get("request"))
                    return None
            except Exception as e:
                log.error("[captcha] Poll exception: %s", e)

            time.sleep(5)
            elapsed += 5

        log.error("[captcha] Timed out after %ds", self.timeout_s)
        return None

    def _inject_token(self, page, captcha_type: str, token: str) -> bool:
        try:
            if captcha_type.startswith("recaptcha"):
                # Set the response textarea
                page.evaluate(f"""
                    var el = document.getElementById('g-recaptcha-response');
                    if (el) {{ el.style.display = 'block'; el.value = '{token}'; }}
                    var els = document.querySelectorAll('[name="g-recaptcha-response"]');
                    els.forEach(function(e) {{ e.value = '{token}'; }});
                """)

                # Trigger callback for invisible reCAPTCHA
                if captcha_type == "recaptcha_v2_invisible":
                    page.evaluate(f"""
                        try {{
                            if (typeof ___grecaptcha_cfg !== 'undefined') {{
                                Object.entries(___grecaptcha_cfg.clients).forEach(function(entry) {{
                                    var client = entry[1];
                                    Object.keys(client).forEach(function(k) {{
                                        var v = client[k];
                                        if (v && typeof v === 'object') {{
                                            Object.keys(v).forEach(function(k2) {{
                                                var v2 = v[k2];
                                                if (v2 && v2.callback) {{
                                                    v2.callback('{token}');
                                                }}
                                            }});
                                        }}
                                    }});
                                }});
                            }}
                        }} catch(e) {{}}
                    """)

            elif captcha_type == "hcaptcha":
                page.evaluate(f"""
                    var el = document.querySelector('[name="h-captcha-response"]');
                    if (el) {{ el.value = '{token}'; }}
                    var el2 = document.querySelector('[name="g-recaptcha-response"]');
                    if (el2) {{ el2.value = '{token}'; }}
                """)

            log.info("[captcha] Token injected into page")
            return True

        except Exception as e:
            log.error("[captcha] Token injection failed: %s", e)
            return False


def solve_captcha_if_present(page, url: str, config: dict) -> bool:
    """Convenience function for strategies to call."""
    solver = CaptchaSolver(config)
    if not solver.is_enabled():
        return False
    return solver.solve(page, url)
