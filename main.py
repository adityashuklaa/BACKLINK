#!/usr/bin/env python3
"""Backlink automation CLI for dialphone.com."""

import argparse
import logging
import sys

import colorlog
from tqdm import tqdm

from core.config_loader import load_config
from core.csv_logger import CSVLogger
from core.rate_limiter import strategy_pause

STRATEGY_MAP = {
    "directories": "strategies.directory_submissions",
    "social": "strategies.social_bookmarking",
    "profiles": "strategies.profile_forum_links",
    "outreach": "strategies.guest_post_outreach",
    "comments": "strategies.blog_comment_links",
}

STRATEGY_ORDER = ["directories", "social", "profiles", "outreach", "comments"]


def setup_logging():
    """Configure colorlog for colored console output."""
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
    )
    logger = logging.getLogger("backlink")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def import_strategy(module_path):
    """Dynamically import a strategy module and return it."""
    import importlib

    return importlib.import_module(module_path)


def run_strategy(name, config, csv_logger, log, dry_run=False, headed=False):
    """Run a single strategy by name."""
    module_path = STRATEGY_MAP[name]
    log.info("Starting strategy: %s", name)
    try:
        module = import_strategy(module_path)
        module.run(config, csv_logger, dry_run=dry_run, headed=headed)
        log.info("Completed strategy: %s", name)
    except Exception as exc:
        log.error("Strategy '%s' failed: %s", name, exc, exc_info=True)


def main():
    parser = argparse.ArgumentParser(
        description="Backlink automation tool for dialphone.com",
    )
    parser.add_argument(
        "--strategy",
        choices=["directories", "social", "profiles", "outreach", "comments", "verify", "all"],
        required=True,
        help="Which backlink strategy to run",
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to configuration file (default: config.json)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in headed mode (overrides config headless setting)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without submitting anything",
    )
    args = parser.parse_args()

    log = setup_logging()
    log.info("Loading config from %s", args.config)

    try:
        config = load_config(args.config)
    except Exception as exc:
        log.error("Failed to load config: %s", exc)
        sys.exit(1)

    # Apply CLI overrides
    if args.headed:
        config["browser"]["headless"] = False
        log.info("Headed mode enabled — browser will be visible")

    if args.dry_run:
        config["dry_run"] = True
        log.info("Dry-run mode enabled — no submissions will be made")

    csv_path = config.get("output", {}).get("csv_path", "output/backlinks_log.csv")
    csv_logger = CSVLogger(csv_path)

    dry_run = args.dry_run or config.get("dry_run", False)
    headed = args.headed

    def _run_email_verify(reason=""):
        ev_cfg = config.get("email_verification", {})
        if ev_cfg.get("enabled"):
            log.info("Running email verification%s...", f" ({reason})" if reason else "")
            from core.email_verifier import EmailVerifier
            verifier = EmailVerifier(config)
            stats = verifier.run(config, csv_logger)
            log.info("Verification results: %s", stats)
        else:
            log.debug("Email verification not enabled, skipping")

    if args.strategy == "verify":
        _run_email_verify()
    elif args.strategy == "all":
        log.info("Running all strategies in recommended order")
        strategies = STRATEGY_ORDER
        for name in tqdm(strategies, desc="Strategies", unit="strategy"):
            run_strategy(name, config, csv_logger, log, dry_run=dry_run, headed=headed)
            if name != strategies[-1]:
                log.info(
                    "Pausing %ds before next strategy...",
                    config["rate_limit"]["strategy_pause_s"],
                )
                strategy_pause(config)
        # Auto-run email verification after all strategies
        if config.get("email_verification", {}).get("auto_run_after_strategies", True):
            _run_email_verify("post-run")
    else:
        run_strategy(args.strategy, config, csv_logger, log, dry_run=dry_run, headed=headed)
        # Auto-verify after directory/profile strategies
        if args.strategy in ("directories", "profiles"):
            if config.get("email_verification", {}).get("auto_run_after_strategies", True):
                _run_email_verify(f"after {args.strategy}")

    log.info("Done. Results logged to %s", csv_path)


if __name__ == "__main__":
    main()
