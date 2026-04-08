import time
import random

def delay(config: dict):
    min_s = config.get("rate_limit", {}).get("min_delay_s", 3)
    max_s = config.get("rate_limit", {}).get("max_delay_s", 8)
    time.sleep(random.uniform(min_s, max_s))

def strategy_pause(config: dict):
    pause_s = config.get("rate_limit", {}).get("strategy_pause_s", 60)
    time.sleep(pause_s)

def email_delay(config: dict):
    delay_s = config.get("rate_limit", {}).get("email_delay_s", 30)
    time.sleep(delay_s)

def inter_field_delay(config: dict):
    min_s = config.get("rate_limit", {}).get("inter_field_min_s", 0.3)
    max_s = config.get("rate_limit", {}).get("inter_field_max_s", 1.5)
    time.sleep(random.uniform(min_s, max_s))

def reading_pause(config: dict):
    min_s = config.get("rate_limit", {}).get("reading_pause_min_s", 2)
    max_s = config.get("rate_limit", {}).get("reading_pause_max_s", 5)
    time.sleep(random.uniform(min_s, max_s))
