"""
50 unique browser profiles — each simulates a different real person on a different device.
Every profile is internally consistent (Mac UA + Mac platform, Windows UA + Windows platform, etc.)
Profiles are rotated to prevent bot detection from repeated submissions.
"""
import random
import json
import os
import hashlib
from datetime import datetime

PROFILES_STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "output", "profile_usage.json")

# 50 unique browser profiles — each represents a different "person"
PROFILES = [
    # ===== WINDOWS + CHROME (20 profiles) =====
    {
        "id": "win-chrome-1",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": {"width": 1920, "height": 1080},
        "platform": "Win32",
        "timezone": "America/New_York",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    },
    {
        "id": "win-chrome-2",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "viewport": {"width": 1366, "height": 768},
        "platform": "Win32",
        "timezone": "America/Chicago",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 16,
        "hardware_concurrency": 12,
        "webgl_vendor": "Google Inc. (AMD)",
        "webgl_renderer": "ANGLE (AMD, AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0, D3D11)",
    },
    {
        "id": "win-chrome-3",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "viewport": {"width": 1536, "height": 864},
        "platform": "Win32",
        "timezone": "America/Los_Angeles",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 4,
        "hardware_concurrency": 4,
        "webgl_vendor": "Google Inc. (Intel)",
        "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    },
    {
        "id": "win-chrome-4",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "viewport": {"width": 1440, "height": 900},
        "platform": "Win32",
        "timezone": "America/Denver",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 32,
        "hardware_concurrency": 16,
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    },
    {
        "id": "win-chrome-5",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "viewport": {"width": 1280, "height": 720},
        "platform": "Win32",
        "timezone": "America/Phoenix",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 6,
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)",
    },
    {
        "id": "win-chrome-6",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": {"width": 2560, "height": 1440},
        "platform": "Win32",
        "timezone": "Europe/London",
        "locale": "en-GB",
        "color_depth": 30,
        "device_memory": 16,
        "hardware_concurrency": 8,
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    },
    {
        "id": "win-chrome-7",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "viewport": {"width": 1600, "height": 900},
        "platform": "Win32",
        "timezone": "Europe/Berlin",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 4,
        "webgl_vendor": "Google Inc. (Intel)",
        "webgl_renderer": "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
    },
    {
        "id": "win-chrome-8",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "viewport": {"width": 1920, "height": 1200},
        "platform": "Win32",
        "timezone": "Asia/Kolkata",
        "locale": "en-IN",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1650 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    },
    {
        "id": "win-chrome-9",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": {"width": 1366, "height": 768},
        "platform": "Win32",
        "timezone": "Asia/Dubai",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 4,
        "hardware_concurrency": 4,
        "webgl_vendor": "Google Inc. (AMD)",
        "webgl_renderer": "ANGLE (AMD, AMD Radeon(TM) Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
    },
    {
        "id": "win-chrome-10",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "viewport": {"width": 1680, "height": 1050},
        "platform": "Win32",
        "timezone": "Australia/Sydney",
        "locale": "en-AU",
        "color_depth": 24,
        "device_memory": 16,
        "hardware_concurrency": 10,
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 2060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    },
    # ===== WINDOWS + FIREFOX (5 profiles) =====
    {
        "id": "win-firefox-1",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "viewport": {"width": 1920, "height": 1080},
        "platform": "Win32",
        "timezone": "America/New_York",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Mozilla",
        "webgl_renderer": "Mozilla",
    },
    {
        "id": "win-firefox-2",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "viewport": {"width": 1536, "height": 864},
        "platform": "Win32",
        "timezone": "America/Chicago",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 16,
        "hardware_concurrency": 12,
        "webgl_vendor": "Mozilla",
        "webgl_renderer": "Mozilla",
    },
    {
        "id": "win-firefox-3",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "viewport": {"width": 1366, "height": 768},
        "platform": "Win32",
        "timezone": "Europe/London",
        "locale": "en-GB",
        "color_depth": 24,
        "device_memory": 4,
        "hardware_concurrency": 4,
        "webgl_vendor": "Mozilla",
        "webgl_renderer": "Mozilla",
    },
    {
        "id": "win-firefox-4",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "viewport": {"width": 1440, "height": 900},
        "platform": "Win32",
        "timezone": "Asia/Kolkata",
        "locale": "en-IN",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 6,
        "webgl_vendor": "Mozilla",
        "webgl_renderer": "Mozilla",
    },
    {
        "id": "win-firefox-5",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "viewport": {"width": 1280, "height": 800},
        "platform": "Win32",
        "timezone": "America/Los_Angeles",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Mozilla",
        "webgl_renderer": "Mozilla",
    },
    # ===== MAC + CHROME (10 profiles) =====
    {
        "id": "mac-chrome-1",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": {"width": 1440, "height": 900},
        "platform": "MacIntel",
        "timezone": "America/New_York",
        "locale": "en-US",
        "color_depth": 30,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Google Inc. (Apple)",
        "webgl_renderer": "ANGLE (Apple, Apple M1, OpenGL 4.1)",
    },
    {
        "id": "mac-chrome-2",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "viewport": {"width": 2560, "height": 1600},
        "platform": "MacIntel",
        "timezone": "America/Los_Angeles",
        "locale": "en-US",
        "color_depth": 30,
        "device_memory": 16,
        "hardware_concurrency": 10,
        "webgl_vendor": "Google Inc. (Apple)",
        "webgl_renderer": "ANGLE (Apple, Apple M2 Pro, OpenGL 4.1)",
    },
    {
        "id": "mac-chrome-3",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "viewport": {"width": 1680, "height": 1050},
        "platform": "MacIntel",
        "timezone": "Europe/London",
        "locale": "en-GB",
        "color_depth": 30,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Google Inc. (Apple)",
        "webgl_renderer": "ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)",
    },
    {
        "id": "mac-chrome-4",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": {"width": 1920, "height": 1080},
        "platform": "MacIntel",
        "timezone": "America/Chicago",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 16,
        "hardware_concurrency": 12,
        "webgl_vendor": "Google Inc. (Apple)",
        "webgl_renderer": "ANGLE (Apple, Apple M3 Max, OpenGL 4.1)",
    },
    {
        "id": "mac-chrome-5",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "viewport": {"width": 1280, "height": 800},
        "platform": "MacIntel",
        "timezone": "Asia/Tokyo",
        "locale": "en-US",
        "color_depth": 30,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Google Inc. (Apple)",
        "webgl_renderer": "ANGLE (Apple, Apple M2, OpenGL 4.1)",
    },
    {
        "id": "mac-chrome-6",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "viewport": {"width": 1440, "height": 900},
        "platform": "MacIntel",
        "timezone": "Europe/Paris",
        "locale": "en-US",
        "color_depth": 30,
        "device_memory": 32,
        "hardware_concurrency": 12,
        "webgl_vendor": "Google Inc. (Apple)",
        "webgl_renderer": "ANGLE (Apple, Apple M3 Pro, OpenGL 4.1)",
    },
    {
        "id": "mac-chrome-7",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "viewport": {"width": 1366, "height": 768},
        "platform": "MacIntel",
        "timezone": "America/Denver",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 4,
        "webgl_vendor": "Google Inc. (Intel)",
        "webgl_renderer": "ANGLE (Intel, Intel(R) Iris(TM) Plus Graphics 640, OpenGL 4.1)",
    },
    {
        "id": "mac-chrome-8",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": {"width": 2560, "height": 1440},
        "platform": "MacIntel",
        "timezone": "Asia/Singapore",
        "locale": "en-SG",
        "color_depth": 30,
        "device_memory": 16,
        "hardware_concurrency": 10,
        "webgl_vendor": "Google Inc. (Apple)",
        "webgl_renderer": "ANGLE (Apple, Apple M2 Max, OpenGL 4.1)",
    },
    {
        "id": "mac-chrome-9",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "viewport": {"width": 1920, "height": 1200},
        "platform": "MacIntel",
        "timezone": "America/Toronto",
        "locale": "en-CA",
        "color_depth": 30,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Google Inc. (Apple)",
        "webgl_renderer": "ANGLE (Apple, Apple M1, OpenGL 4.1)",
    },
    {
        "id": "mac-chrome-10",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "viewport": {"width": 1440, "height": 900},
        "platform": "MacIntel",
        "timezone": "Asia/Kolkata",
        "locale": "en-IN",
        "color_depth": 30,
        "device_memory": 16,
        "hardware_concurrency": 8,
        "webgl_vendor": "Google Inc. (Apple)",
        "webgl_renderer": "ANGLE (Apple, Apple M2 Pro, OpenGL 4.1)",
    },
    # ===== MAC + SAFARI (5 profiles) =====
    {
        "id": "mac-safari-1",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        "viewport": {"width": 1440, "height": 900},
        "platform": "MacIntel",
        "timezone": "America/New_York",
        "locale": "en-US",
        "color_depth": 30,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Apple Inc.",
        "webgl_renderer": "Apple M1",
    },
    {
        "id": "mac-safari-2",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
        "viewport": {"width": 2560, "height": 1600},
        "platform": "MacIntel",
        "timezone": "America/Los_Angeles",
        "locale": "en-US",
        "color_depth": 30,
        "device_memory": 16,
        "hardware_concurrency": 10,
        "webgl_vendor": "Apple Inc.",
        "webgl_renderer": "Apple M2 Pro",
    },
    {
        "id": "mac-safari-3",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "viewport": {"width": 1680, "height": 1050},
        "platform": "MacIntel",
        "timezone": "Europe/London",
        "locale": "en-GB",
        "color_depth": 30,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Apple Inc.",
        "webgl_renderer": "Apple M1 Pro",
    },
    {
        "id": "mac-safari-4",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "viewport": {"width": 1920, "height": 1080},
        "platform": "MacIntel",
        "timezone": "America/Chicago",
        "locale": "en-US",
        "color_depth": 30,
        "device_memory": 32,
        "hardware_concurrency": 12,
        "webgl_vendor": "Apple Inc.",
        "webgl_renderer": "Apple M3 Max",
    },
    {
        "id": "mac-safari-5",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "viewport": {"width": 1280, "height": 800},
        "platform": "MacIntel",
        "timezone": "Asia/Kolkata",
        "locale": "en-IN",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Apple Inc.",
        "webgl_renderer": "Apple M2",
    },
    # ===== LINUX + CHROME (5 profiles) =====
    {
        "id": "linux-chrome-1",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "viewport": {"width": 1920, "height": 1080},
        "platform": "Linux x86_64",
        "timezone": "America/New_York",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 16,
        "hardware_concurrency": 8,
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 Ti, OpenGL 4.5)",
    },
    {
        "id": "linux-chrome-2",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "viewport": {"width": 2560, "height": 1440},
        "platform": "Linux x86_64",
        "timezone": "Europe/Berlin",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 32,
        "hardware_concurrency": 16,
        "webgl_vendor": "Google Inc. (AMD)",
        "webgl_renderer": "ANGLE (AMD, AMD Radeon RX 7900 XTX, OpenGL 4.6)",
    },
    {
        "id": "linux-chrome-3",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "viewport": {"width": 1366, "height": 768},
        "platform": "Linux x86_64",
        "timezone": "Asia/Kolkata",
        "locale": "en-IN",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 4,
        "webgl_vendor": "Google Inc. (Intel)",
        "webgl_renderer": "ANGLE (Intel, Mesa Intel(R) UHD Graphics 620, OpenGL 4.6)",
    },
    {
        "id": "linux-chrome-4",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "viewport": {"width": 1440, "height": 900},
        "platform": "Linux x86_64",
        "timezone": "America/Sao_Paulo",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 6,
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 2070, OpenGL 4.5)",
    },
    {
        "id": "linux-chrome-5",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "viewport": {"width": 1600, "height": 900},
        "platform": "Linux x86_64",
        "timezone": "Europe/Moscow",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 16,
        "hardware_concurrency": 8,
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti, OpenGL 4.5)",
    },
    # ===== LINUX + FIREFOX (5 profiles) =====
    {
        "id": "linux-firefox-1",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "viewport": {"width": 1920, "height": 1080},
        "platform": "Linux x86_64",
        "timezone": "America/New_York",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Mozilla",
        "webgl_renderer": "Mozilla",
    },
    {
        "id": "linux-firefox-2",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "viewport": {"width": 1366, "height": 768},
        "platform": "Linux x86_64",
        "timezone": "Europe/London",
        "locale": "en-GB",
        "color_depth": 24,
        "device_memory": 4,
        "hardware_concurrency": 4,
        "webgl_vendor": "Mozilla",
        "webgl_renderer": "Mozilla",
    },
    {
        "id": "linux-firefox-3",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "viewport": {"width": 1536, "height": 864},
        "platform": "Linux x86_64",
        "timezone": "Asia/Tokyo",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 16,
        "hardware_concurrency": 12,
        "webgl_vendor": "Mozilla",
        "webgl_renderer": "Mozilla",
    },
    {
        "id": "linux-firefox-4",
        "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "viewport": {"width": 1440, "height": 900},
        "platform": "Linux x86_64",
        "timezone": "America/Chicago",
        "locale": "en-US",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 6,
        "webgl_vendor": "Mozilla",
        "webgl_renderer": "Mozilla",
    },
    {
        "id": "linux-firefox-5",
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "viewport": {"width": 1280, "height": 1024},
        "platform": "Linux x86_64",
        "timezone": "Europe/Berlin",
        "locale": "de-DE",
        "color_depth": 24,
        "device_memory": 8,
        "hardware_concurrency": 8,
        "webgl_vendor": "Mozilla",
        "webgl_renderer": "Mozilla",
    },
]


def _load_usage():
    """Load profile usage history."""
    if os.path.exists(PROFILES_STATE_FILE):
        with open(PROFILES_STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_used": None, "site_profiles": {}, "usage_count": {}}


def _save_usage(state):
    """Save profile usage history."""
    os.makedirs(os.path.dirname(PROFILES_STATE_FILE), exist_ok=True)
    with open(PROFILES_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_profile(site_name: str = "") -> dict:
    """Get a random profile, ensuring:
    1. Never the same profile twice in a row
    2. Same site always gets a different profile than last time
    3. Least-used profiles are preferred (even distribution)
    """
    state = _load_usage()
    last_used = state.get("last_used")
    site_last = state.get("site_profiles", {}).get(site_name)
    usage = state.get("usage_count", {})

    # Filter out last-used and site-last profiles
    candidates = [p for p in PROFILES if p["id"] != last_used and p["id"] != site_last]
    if not candidates:
        candidates = [p for p in PROFILES if p["id"] != last_used]
    if not candidates:
        candidates = PROFILES

    # Prefer least-used profiles
    min_usage = min(usage.get(p["id"], 0) for p in candidates)
    least_used = [p for p in candidates if usage.get(p["id"], 0) == min_usage]

    profile = random.choice(least_used)

    # Update state
    state["last_used"] = profile["id"]
    if site_name:
        state["site_profiles"][site_name] = profile["id"]
    state["usage_count"][profile["id"]] = usage.get(profile["id"], 0) + 1
    _save_usage(state)

    return profile


def get_profile_count() -> int:
    """Return total number of available profiles."""
    return len(PROFILES)


def get_fingerprint_script(profile: dict) -> str:
    """Generate JavaScript to inject this profile's fingerprint into the page."""
    return f"""
        // Override platform
        Object.defineProperty(navigator, 'platform', {{get: () => '{profile["platform"]}'}});

        // Override hardware concurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {profile["hardware_concurrency"]}}});

        // Override device memory
        Object.defineProperty(navigator, 'deviceMemory', {{get: () => {profile["device_memory"]}}});

        // Override color depth
        Object.defineProperty(screen, 'colorDepth', {{get: () => {profile["color_depth"]}}});
        Object.defineProperty(screen, 'pixelDepth', {{get: () => {profile["color_depth"]}}});

        // Override WebGL
        const getParam = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{profile["webgl_vendor"]}';
            if (param === 37446) return '{profile["webgl_renderer"]}';
            return getParam.call(this, param);
        }};
        const getParam2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{profile["webgl_vendor"]}';
            if (param === 37446) return '{profile["webgl_renderer"]}';
            return getParam2.call(this, param);
        }};

        // Override languages
        Object.defineProperty(navigator, 'languages', {{get: () => ['{profile["locale"]}', '{profile["locale"].split("-")[0]}']}});
        Object.defineProperty(navigator, 'language', {{get: () => '{profile["locale"]}'}});

        // Override webdriver
        Object.defineProperty(navigator, 'webdriver', {{get: () => undefined}});

        // Chrome runtime
        window.chrome = {{runtime: {{}}}};
    """
