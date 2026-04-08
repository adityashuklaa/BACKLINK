"""
Email verification auto-click.
Connects to Gmail via IMAP, finds verification emails, clicks confirm links.
"""
import imaplib
import email
import re
import logging
from datetime import datetime, timedelta
from email.header import decode_header
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from core.http_client import get_session

log = logging.getLogger("backlink")

VERIFY_SUBJECT_KEYWORDS = ["verify", "confirm", "activate", "welcome", "validate"]
VERIFY_LINK_KEYWORDS = ["verify", "confirm", "activate", "validation", "click-here", "email-verify", "token=", "code="]
VERIFY_BUTTON_TEXTS = ["verify", "confirm", "activate", "click here", "complete registration", "validate"]


class EmailVerifier:
    def __init__(self, config: dict):
        cfg = config.get("email_verification", {})
        self.imap_server = cfg.get("imap_server", "imap.gmail.com")
        self.imap_port = cfg.get("imap_port", 993)
        self.email_addr = cfg.get("email", "")
        self.app_password = cfg.get("app_password", "")
        self.enabled = cfg.get("enabled", False)
        self.search_last_hours = cfg.get("search_last_hours", 24)
        self.config = config

    def is_enabled(self) -> bool:
        return self.enabled and bool(self.app_password) and bool(self.email_addr)

    def connect(self):
        log.info("[email-verify] Connecting to %s:%s...", self.imap_server, self.imap_port)
        mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        mail.login(self.email_addr, self.app_password)
        mail.select("INBOX")
        log.info("[email-verify] Connected successfully")
        return mail

    def search_verification_emails(self, mail) -> list:
        all_ids = set()
        for keyword in VERIFY_SUBJECT_KEYWORDS:
            try:
                _, data = mail.search(None, f'(UNSEEN SUBJECT "{keyword}")')
                ids = data[0].split()
                all_ids.update(ids)
            except Exception as e:
                log.debug("[email-verify] Search for '%s' failed: %s", keyword, e)

        results = []
        for eid in all_ids:
            try:
                _, msg_data = mail.fetch(eid, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                subject = self._decode_header(msg.get("Subject", ""))
                from_addr = self._decode_header(msg.get("From", ""))
                from_domain = self._extract_domain(from_addr)
                date_str = msg.get("Date", "")

                html_body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/html":
                            payload = part.get_payload(decode=True)
                            charset = part.get_content_charset() or "utf-8"
                            html_body = payload.decode(charset, errors="replace")
                            break
                else:
                    if msg.get_content_type() == "text/html":
                        payload = msg.get_payload(decode=True)
                        charset = msg.get_content_charset() or "utf-8"
                        html_body = payload.decode(charset, errors="replace")

                results.append({
                    "email_id": eid,
                    "from": from_addr,
                    "from_domain": from_domain,
                    "subject": subject,
                    "html_body": html_body,
                    "date": date_str,
                })
            except Exception as e:
                log.warning("[email-verify] Failed to parse email %s: %s", eid, e)

        log.info("[email-verify] Found %d verification emails", len(results))
        return results

    def extract_verification_links(self, html_body: str) -> list:
        if not html_body:
            return []
        soup = BeautifulSoup(html_body, "lxml")
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text().lower().strip()

            # Check if href contains verification keywords
            href_lower = href.lower()
            is_verify_link = any(kw in href_lower for kw in VERIFY_LINK_KEYWORDS)

            # Check if button text contains verification keywords
            is_verify_text = any(kw in text for kw in VERIFY_BUTTON_TEXTS)

            if is_verify_link or is_verify_text:
                if href.startswith("http"):
                    links.append(href)

        # Deduplicate
        return list(dict.fromkeys(links))

    def visit_link(self, url: str) -> bool:
        session = get_session(self.config)
        try:
            resp = session.get(url, allow_redirects=True, timeout=30)
            if resp.status_code == 200:
                log.info("[email-verify] Clicked link successfully: %s", url[:80])
                return True
            else:
                log.warning("[email-verify] Link returned status %d: %s", resp.status_code, url[:80])
                # Try with Playwright for JS-heavy pages
                return self._visit_with_browser(url)
        except Exception as e:
            log.warning("[email-verify] requests failed (%s), trying Playwright...", e)
            return self._visit_with_browser(url)

    def _visit_with_browser(self, url: str) -> bool:
        try:
            from core.browser import get_browser, new_page
            pw, browser, _ = get_browser(self.config)
            try:
                context, page = new_page(browser, self.config)
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle", timeout=15000)
                content = page.content().lower()
                success = any(w in content for w in ["verified", "confirmed", "success", "thank you", "activated"])
                context.close()
                if success:
                    log.info("[email-verify] Browser verification succeeded: %s", url[:80])
                else:
                    log.info("[email-verify] Browser visited link (no clear success indicator): %s", url[:80])
                return True
            finally:
                browser.close()
                pw.stop()
        except Exception as e:
            log.error("[email-verify] Browser verification failed: %s", e)
            return False

    def mark_email_read(self, mail, email_id):
        try:
            mail.store(email_id, "+FLAGS", "\\Seen")
        except Exception as e:
            log.warning("[email-verify] Failed to mark email as read: %s", e)

    def run(self, config: dict, csv_logger) -> dict:
        stats = {"emails_found": 0, "links_clicked": 0, "sites_verified": 0, "errors": 0}

        if not self.is_enabled():
            log.warning("[email-verify] Not enabled or missing credentials")
            return stats

        pending = csv_logger.get_pending_sites()
        if not pending:
            log.info("[email-verify] No pending sites to verify")
            return stats

        pending_domains = {}
        for site in pending:
            url = site.get("url_submitted", "")
            domain = self._extract_domain(url)
            if domain:
                pending_domains[domain] = site.get("site_name", "")

        log.info("[email-verify] %d pending sites, checking inbox...", len(pending))

        try:
            mail = self.connect()
        except Exception as e:
            log.error("[email-verify] IMAP connection failed: %s", e)
            stats["errors"] += 1
            return stats

        try:
            emails = self.search_verification_emails(mail)
            stats["emails_found"] = len(emails)

            for em in emails:
                links = self.extract_verification_links(em["html_body"])
                if not links:
                    continue

                for link in links:
                    success = self.visit_link(link)
                    if success:
                        stats["links_clicked"] += 1

                        # Try to match to a pending site by from_domain
                        matched_site = None
                        from_domain = em.get("from_domain", "")
                        for pd, site_name in pending_domains.items():
                            if pd in from_domain or from_domain in pd:
                                matched_site = site_name
                                break

                        # Also try matching link domain to pending URL domains
                        if not matched_site:
                            link_domain = self._extract_domain(link)
                            for pd, site_name in pending_domains.items():
                                if pd in link_domain or link_domain in pd:
                                    matched_site = site_name
                                    break

                        if matched_site:
                            csv_logger.update_status(matched_site, "verified",
                                                     f"Email verified via {em['from_domain']}")
                            stats["sites_verified"] += 1
                            log.info("[email-verify] Verified: %s", matched_site)

                self.mark_email_read(mail, em["email_id"])

        except Exception as e:
            log.error("[email-verify] Error during verification: %s", e)
            stats["errors"] += 1
        finally:
            try:
                mail.close()
                mail.logout()
            except Exception:
                pass

        log.info("[email-verify] Done: %s", stats)
        return stats

    @staticmethod
    def _decode_header(value: str) -> str:
        if not value:
            return ""
        parts = decode_header(value)
        decoded = []
        for part, charset in parts:
            if isinstance(part, bytes):
                decoded.append(part.decode(charset or "utf-8", errors="replace"))
            else:
                decoded.append(part)
        return " ".join(decoded)

    @staticmethod
    def _extract_domain(text: str) -> str:
        # Extract domain from email address or URL
        email_match = re.search(r"@([\w.-]+)", text)
        if email_match:
            return email_match.group(1).lower()
        try:
            parsed = urlparse(text)
            if parsed.hostname:
                return parsed.hostname.lower().replace("www.", "")
        except Exception:
            pass
        return ""
