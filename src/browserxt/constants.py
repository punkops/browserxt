from browserxt.globals import GLOBALS

NT_BROWSERS = (
    {
        "chrome": {
            "family": "chromium",
            "paths": [
                f"{GLOBALS.PROGRAM_FILES}\\Google\\Chrome\\Application\\chrome.exe",
                f"{GLOBALS.PROGRAM_FILES} (x86)\\Google\\Chrome\\Application\\chrome.exe",
                f"{GLOBALS.LOCAL_DATA}\\Google\\Chrome\\Application\\chrome.exe",
            ],
        },
        "firefox": {
            "family": "firefox",
            "paths": [
                f"{GLOBALS.PROGRAM_FILES}\\Mozilla Firefox\\firefox.exe",
                f"{GLOBALS.PROGRAM_FILES} (x86)\\Mozilla Firefox\\firefox.exe",
                f"{GLOBALS.LOCAL_DATA}\\Mozilla Firefox\\firefox.exe",
            ],
        },
        "edge": {
            "family": "chromium",
            "paths": [
                f"{GLOBALS.PROGRAM_FILES}\\Microsoft\\Edge\\Application\\msedge.exe",
                f"{GLOBALS.PROGRAM_FILES} (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                f"{GLOBALS.LOCAL_DATA}\\Microsoft\\Edge\\Application\\msedge.exe",
            ],
        },
        "brave": {
            "family": "chromium",
            "paths": [
                f"{GLOBALS.PROGRAM_FILES}\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                f"{GLOBALS.PROGRAM_FILES} (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
                f"{GLOBALS.LOCAL_DATA}\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
            ],
        },
        "opera": {
            "family": "chromium",
            "paths": [
                f"{GLOBALS.PROGRAM_FILES}\\Opera\\opera.exe",
                f"{GLOBALS.PROGRAM_FILES} (x86)\\Opera\\opera.exe",
                f"{GLOBALS.LOCAL_DATA}\\Programs\\Opera\\opera.exe",
            ],
        },
        "vivaldi": {
            "family": "chromium",
            "paths": [
                f"{GLOBALS.PROGRAM_FILES}\\Vivaldi\\Application\\vivaldi.exe",
                f"{GLOBALS.PROGRAM_FILES} (x86)\\Vivaldi\\Application\\vivaldi.exe",
                f"{GLOBALS.LOCAL_DATA}\\Vivaldi\\Application\\vivaldi.exe",
            ],
        },
    }
    if GLOBALS.LOCAL_DATA and GLOBALS.PROGRAM_FILES
    else {}
)

# Browsers and their possible binary paths on POSIX systems
POSIX_BROWSERS = {
    "chrome": {
        "paths": [
            "google-chrome",
            "google-chrome-stable",
            "chrome",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ],
        "family": "chromium",
    },
    "firefox": {
        "paths": [
            "firefox",
            "firefox-bin",
            "/Applications/Firefox.app/Contents/MacOS/firefox",
        ],
        "family": "firefox",
    },
    "chromium": {
        "paths": [
            "chromium",
            "chromium-browser",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ],
        "family": "chromium",
    },
    "opera": {
        "paths": ["opera", "/Applications/Opera.app/Contents/MacOS/Opera"],
        "family": "chromium",
    },
    "brave": {
        "paths": [
            "brave",
            "brave-browser",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        ],
        "family": "chromium",
    },
    "edge": {
        "paths": [
            "microsoft-edge",
            "microsoft-edge-stable",
            "edge",
            "msedge",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ],
        "family": "chromium",
    },
    "safari": {
        "paths": ["safari", "/Applications/Safari.app/Contents/MacOS/Safari"],
        "family": "safari",
    },
    "vivaldi": {
        "paths": ["vivaldi", "/Applications/Vivaldi.app/Contents/MacOS/Vivaldi"],
        "family": "chromium",
    },
}

# Default order for browsers to check, chosen according to popularity (kind of)
DEFAULT_SORTING = [
    "default",
    "chrome",
    "chromium",
    "firefox",
    "brave",
    "opera",
    "vivaldi",
    "edge",
    "safari",
    "unknown",
]

# Common directories for .desktop files
DESKTOP_DIRS = [
    "/usr/share/applications/",
    "/usr/local/share/applications/",
    f"{GLOBALS.HOME}/.local/share/applications/",
    f"/etc/profiles/per-user/{GLOBALS.USER}/share/applications/",
    "/run/current-system/sw/share/applications/",
    f"{GLOBALS.HOME}/.nix-profile/share/applications/",
]
