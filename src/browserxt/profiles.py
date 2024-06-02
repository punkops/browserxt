import os
import subprocess

from browserxt.utils import is_running_in_wsl, nt_to_wsl_path


DEFAULT_USER_DATA_DIR = {
    "posix": os.path.expandvars("$HOME/.cache/browserxt"),
    "nt": (
        subprocess.run(
            [
                "cmd.exe",
                "/c",
                "echo",
                "%LOCALAPPDATA%\\browserxt",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if os.name == "nt" or is_running_in_wsl()
        else ""
    ),
}


def get_profiles_path(
    name: str,
    type: str,
    user_data_path: str = "",
    create: bool = True,
    use_wsl: bool = False,
) -> tuple[str, str]:

    path = user_data_path
    full_path = path
    if os.name == "nt" or (is_running_in_wsl() and not use_wsl):
        if path == "":
            path = f"{DEFAULT_USER_DATA_DIR['nt']}\\{type}"
        full_path = f"{path}\\{name}"
        if is_running_in_wsl() and not use_wsl and create:
            os.makedirs(nt_to_wsl_path(full_path), exist_ok=True)
            return full_path, path
    else:
        if path == "":
            path = f"{DEFAULT_USER_DATA_DIR['posix']}/{type}"
            path = path
        full_path = f"{path}/{name}"

    if create:
        os.makedirs(full_path, exist_ok=True)

    return full_path, path


def get_chromium_profile_options(
    name: str,
    user_data_path: str = "",
    use_wsl: bool = False,
) -> list[str]:
    _, path = get_profiles_path(
        name, "chromium", user_data_path, create=True, use_wsl=use_wsl
    )

    options = [
        f"--user-data-dir={path}",
        f"--profile-directory={name}",
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
    use_wsl: bool = False,
) -> list[str]:
    full_path, _ = get_profiles_path(
        name, "firefox", user_data_path, create=True, use_wsl=use_wsl
    )

    options = [
        "--profile",
        full_path,
        "-P",
        name,
        "--new-tab",
    ]

    return options
