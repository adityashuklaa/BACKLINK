"""
Intelligent submission result detector with self-diagnosis.
Analyzes the page state after submission to determine TRUE outcome,
not just keyword matching. Returns actionable feedback for retry logic.
"""
import logging
import re

log = logging.getLogger("backlink")


class SubmissionResult:
    """Structured result with diagnosis and retry advice."""
    def __init__(self, status, notes, retry=False, retry_reason=""):
        self.status = status        # "success" | "failed" | "pending"
        self.notes = notes          # Human-readable description
        self.retry = retry          # Should the bot retry with different approach?
        self.retry_reason = retry_reason  # What to change on retry

    def __repr__(self):
        return f"<{self.status}: {self.notes[:60]}>"


def analyze_page(page, before_url: str, site_name: str = "") -> SubmissionResult:
    """Deep analysis of page state after form submission.

    Checks in priority order:
    1. Did the URL change? (redirect = strong signal)
    2. Is there an error message visible?
    3. Did a login/signup wall appear? (need real credentials)
    4. Is there a CAPTCHA blocking?
    5. Is there a success confirmation?
    6. Did the form disappear? (submitted but no confirmation text)
    7. Is the form still there with values cleared? (submitted + reset)
    8. Is the form still there with values intact? (nothing happened)
    """
    try:
        current_url = page.url
        content = page.content()
        content_lower = content.lower()
        visible_text = page.evaluate("document.body ? document.body.innerText : ''").lower()

        # --- CHECK 0: PAGE DEAD / 404 / ERROR PAGE ---
        # This MUST run first — catches fake successes where page is actually broken
        dead_signals = [
            "page not found", "404", "doesn't exist", "does not exist",
            "no longer available", "has been removed", "page is missing",
            "we can't find", "we couldn't find", "not available",
            "this page isn't available", "nothing here", "page has moved",
            "go back home", "return to homepage",
        ]
        for signal in dead_signals:
            if signal in visible_text:
                return SubmissionResult(
                    "failed", f"Page is dead/404 — contains '{signal}'",
                    retry=False, retry_reason="page_dead"
                )

        # Check if page is mostly empty (Cloudflare challenge or blank page)
        if len(visible_text.strip()) < 50:
            return SubmissionResult(
                "failed", "Page is blank or blocked (less than 50 chars of content)",
                retry=True, retry_reason="page_blank"
            )

        # --- CHECK 1: URL REDIRECT ---
        url_changed = current_url != before_url
        if url_changed:
            new_path = current_url.lower()
            # Redirected to login = form requires auth
            if any(x in new_path for x in ["/login", "/signin", "/sign-in", "/auth"]):
                return SubmissionResult(
                    "failed", f"Redirected to login page — real account needed on {site_name}",
                    retry=False, retry_reason="needs_real_account"
                )
            # Redirected to 404/error page
            if any(x in new_path for x in ["/404", "/error", "/not-found"]):
                return SubmissionResult(
                    "failed", f"Redirected to error page: {current_url[:100]}",
                    retry=False, retry_reason="page_dead"
                )
            # Redirected to search page (Yellow Pages does this) = NOT success
            if any(x in new_path for x in ["/search", "/results", "/find"]):
                return SubmissionResult(
                    "failed", f"Redirected to search page, not confirmation: {current_url[:100]}",
                    retry=False, retry_reason="redirect_to_search"
                )
            # Redirected to success/confirm/dashboard
            if any(x in new_path for x in ["success", "thank", "confirm", "welcome", "dashboard", "verify-email"]):
                return SubmissionResult("success", f"Redirected to confirmation: {current_url[:100]}")
            # Any other redirect — check the page content before declaring success
            # Don't blindly assume redirect = success

        # --- CHECK 2: ERROR MESSAGES ---
        error_patterns = [
            (r"(?:this |the )?field is required", "required_fields_empty"),
            (r"invalid (?:email|phone|url|input)", "invalid_input"),
            (r"(?:email|username) (?:already |is )(?:taken|exists|registered|in use)", "already_registered"),
            (r"password (?:is )?(?:too short|incorrect|wrong|invalid)", "auth_failed"),
            (r"(?:please |must )(?:login|sign in|log in|create an account)", "needs_login"),
            (r"access denied|forbidden|403|unauthorized|401", "access_denied"),
            (r"rate limit|too many requests|slow down|try again later", "rate_limited"),
            (r"something went wrong|error occurred|unexpected error", "server_error"),
            (r"bot detected|suspicious activity|automated", "bot_detected"),
        ]

        for pattern, reason in error_patterns:
            if re.search(pattern, visible_text):
                retry = reason in ("rate_limited", "server_error", "required_fields_empty")
                return SubmissionResult(
                    "failed", f"Error detected: {reason}",
                    retry=retry, retry_reason=reason
                )

        # --- CHECK 3: LOGIN WALL ---
        login_selectors = [
            "input[type='password']",
            "form[action*='login']", "form[action*='signin']",
            "a:has-text('Sign up')", "a:has-text('Create account')",
        ]
        login_count = 0
        for sel in login_selectors:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    login_count += 1
            except Exception:
                pass
        if login_count >= 2:
            return SubmissionResult(
                "failed", f"Login/signup wall — {site_name} requires a real account",
                retry=False, retry_reason="needs_real_account"
            )

        # --- CHECK 4: CAPTCHA ---
        if any(x in content_lower for x in ["recaptcha", "g-recaptcha", "hcaptcha", "captcha"]):
            return SubmissionResult(
                "pending", "CAPTCHA present — enable 2Captcha or solve manually",
                retry=True, retry_reason="captcha_blocking"
            )

        # --- CHECK 5: SUCCESS SIGNALS ---
        success_phrases = [
            "thank you", "thanks for", "successfully submitted",
            "submission received", "we've received your",
            "listing created", "profile updated", "account created",
            "verification email sent", "check your email", "confirm your email",
            "registration complete", "you're all set", "congratulations",
            "added successfully", "saved successfully", "changes saved",
            "your comment is awaiting moderation", "comment submitted",
            "pending review", "under review", "application received",
            "business added", "company added", "bookmarked", "published",
        ]
        for phrase in success_phrases:
            if phrase in visible_text:
                return SubmissionResult("success", f"Confirmed: '{phrase}' found on page")

        # Success CSS elements
        for sel in ["[class*='success']", ".alert-success", "[class*='confirmation']", "[id*='success']"]:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    text = (el.text_content() or "")[:100]
                    return SubmissionResult("success", f"Success element visible: {text}")
            except Exception:
                pass

        # --- CHECK 6: FORM DISAPPEARED ---
        form_visible = False
        for sel in ["form input[type='submit']", "form button[type='submit']", "form input[type='text']"]:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    form_visible = True
                    break
            except Exception:
                pass

        if not form_visible:
            # Form gone — but is the page actually a confirmation, or just broken/empty?
            if len(visible_text.strip()) < 100:
                return SubmissionResult(
                    "failed", "Form gone but page is nearly empty — likely blocked or error",
                    retry=True, retry_reason="page_blank"
                )
            # Check for actual confirmation content
            has_positive = any(w in visible_text for w in [
                "thank", "success", "submit", "receiv", "confirm", "verif",
                "welcome", "dashboard", "account", "profile", "listing",
                "saved", "added", "created", "complete",
            ])
            if has_positive:
                return SubmissionResult("success", "Form gone + confirmation content detected")
            # Form gone but no confirmation — uncertain
            return SubmissionResult(
                "pending", "Form gone but no confirmation text found — verify manually",
                retry=False, retry_reason="uncertain"
            )

        # --- CHECK 7: FORM STILL THERE, VALUES CLEARED ---
        try:
            inputs = page.query_selector_all("form input[type='text'], form input[type='email']")
            filled_count = 0
            for inp in inputs[:5]:
                val = inp.get_attribute("value") or ""
                if len(val) > 2:
                    filled_count += 1
            if filled_count == 0 and len(inputs) > 0:
                # Fields cleared — but verify page has confirmation content
                has_confirm = any(w in visible_text for w in ["thank", "success", "receiv", "confirm", "submit"])
                if has_confirm:
                    return SubmissionResult("success", "Form cleared + confirmation text found")
                return SubmissionResult("pending", "Form fields cleared but no confirmation — verify manually")
        except Exception:
            pass

        # --- CHECK 8: FORM STILL THERE WITH DATA ---
        # Nothing happened — the submit didn't go through
        return SubmissionResult(
            "pending", "Form still present with data — submission status unclear",
            retry=True, retry_reason="submit_may_not_have_fired"
        )

    except Exception as e:
        log.debug("[detect] Analysis error: %s", e)
        return SubmissionResult("pending", f"Could not analyze page: {str(e)[:80]}")


def should_retry(result: SubmissionResult, attempt: int, max_attempts: int = 2) -> bool:
    """Decide if a retry is worthwhile based on the result and attempt count."""
    if not result.retry:
        return False
    if attempt >= max_attempts:
        return False
    if result.retry_reason in ("needs_real_account", "needs_login", "already_registered"):
        return False  # No point retrying without real creds
    return True
