"""
Platform Discovery — automatically find and test new paste/publishing platforms.
"""
import logging

log = logging.getLogger("backlink")

# Master list of paste/publishing platforms to test
# Each has been researched for: no account needed, public URLs, accepts text content
PASTE_PLATFORMS = [
    # Tier 1: High DA (60+)
    {"name": "paste.debian.net", "url": "https://paste.debian.net/", "da": 70, "tested": True, "works": True},
    {"name": "paste.centos.org", "url": "https://paste.centos.org/", "da": 60, "tested": True, "works": True},
    {"name": "paste2.org", "url": "https://paste2.org/", "da": 55, "tested": True, "works": True},

    # Tier 2: Medium DA (30-59)
    {"name": "snippet.host", "url": "https://snippet.host/", "da": 40, "tested": True, "works": True},
    {"name": "bin.disroot.org", "url": "https://bin.disroot.org/", "da": 45, "tested": True, "works": False},
    {"name": "bpa.st", "url": "https://bpa.st/", "da": 30, "tested": True, "works": True},

    # Tier 3: Untested paste sites
    {"name": "paste.sh", "url": "https://paste.sh/", "da": 35, "tested": False, "works": None},
    {"name": "cl1p.net", "url": "https://cl1p.net/", "da": 30, "tested": False, "works": None},
    {"name": "paste.ofcode.org", "url": "https://paste.ofcode.org/", "da": 25, "tested": False, "works": None},
    {"name": "pastebin.fi", "url": "https://pastebin.fi/", "da": 28, "tested": False, "works": None},
    {"name": "paste.rohitab.com", "url": "https://paste.rohitab.com/", "da": 35, "tested": False, "works": None},
    {"name": "vpaste.net", "url": "https://vpaste.net/", "da": 22, "tested": False, "works": None},
    {"name": "paste.gg", "url": "https://paste.gg/", "da": 40, "tested": False, "works": None},
    {"name": "hastebin.com", "url": "https://www.toptal.com/developers/hastebin", "da": 88, "tested": False, "works": None},
    {"name": "justpaste.me", "url": "https://justpaste.me/", "da": 30, "tested": False, "works": None},
    {"name": "pasteio.com", "url": "https://pasteio.com/", "da": 25, "tested": False, "works": None},
    {"name": "paste.mozilla.org", "url": "https://paste.mozilla.org/", "da": 85, "tested": False, "works": None},
    {"name": "privatebin.info", "url": "https://privatebin.info/", "da": 50, "tested": False, "works": None},
    {"name": "0x0.st", "url": "https://0x0.st/", "da": 30, "tested": False, "works": None},
    {"name": "paste.lol", "url": "https://paste.lol/", "da": 20, "tested": False, "works": None},
]


def get_working_platforms():
    """Return platforms confirmed to work."""
    return [p for p in PASTE_PLATFORMS if p.get("works") is True]


def get_untested_platforms():
    """Return platforms not yet tested."""
    return [p for p in PASTE_PLATFORMS if p.get("tested") is False]


def get_platforms_by_da(min_da=0):
    """Return working platforms sorted by DA."""
    working = get_working_platforms()
    return sorted([p for p in working if p["da"] >= min_da], key=lambda x: -x["da"])
