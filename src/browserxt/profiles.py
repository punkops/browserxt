import os

from browserxt.utils import nt_to_wsl_path
from browserxt.globals import GLOBALS


def get_profiles_path(
    name: str,
    type: str,
    user_data_path: str = "",
    create: bool = True,
) -> str:
    path = user_data_path
    if GLOBALS.IS_NT:
        if path == "":
            path = f"{GLOBALS.LOCAL_DATA}\\browserxt\\{type}\\{name}"
        if GLOBALS.IS_WSL and create:
            os.makedirs(nt_to_wsl_path(path), exist_ok=True)
            return path
    else:
        if path == "":
            path = f"{GLOBALS.HOME}/.cache/browserxt/{type}/{name}"
            path = path

    if create:
        os.makedirs(path, exist_ok=True)

    return path


def get_chromium_profile_options(
    name: str,
    user_data_path: str = "",
    create: bool = True,
) -> list[str]:
    path = get_profiles_path(name, "chromium", user_data_path, create)

    options = [
        f"--user-data-dir={path}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-networking",
        "--disable-client-side-phishing-detection",
        "--disable-default-apps",
        "--disable-hang-monitor",
        "--disable-popup-blocking",
        "--disable-prompt-on-repost",
        "--disable-sync",
        "--disable-web-resources",
        "--disable-infobars",
        "--disable-session-crashed-bubble",
        "--disable-notifications",
        "--disable-search-engine-choice-screen",
        "--disable-save-password-bubble",
        "--disable-translate",
        "--metrics-recording-only",
        "--safebrowsing-disable-auto-update",
        "--log-level=0",
    ]

    return options


def get_firefox_profile_options(
    name: str,
    user_data_path: str = "",
    create: bool = True,
) -> list[str]:
    path = get_profiles_path(name, "firefox", user_data_path, create)

    options = [
        "--profile",
        path,
        "-P",
        name,
        "--new-tab",
    ]

    return options
