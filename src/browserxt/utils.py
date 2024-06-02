# mypy: disable-error-code = attr-defined
import os
import json
import shutil
import subprocess
import configparser
from browserxt.globals import GLOBALS
from browserxt.constants import (
    DEFAULT_SORTING,
    DESKTOP_DIRS,
    NT_BROWSERS,
    POSIX_BROWSERS,
)


def sort_tryoder(tryorder: list[str]) -> list[str]:
    return sorted(
        tryorder.copy(),
        key=lambda x: (
            DEFAULT_SORTING.index(x) if x in DEFAULT_SORTING else len(DEFAULT_SORTING)
        ),
    )


def get_nt_default_browser() -> str | None:
    if GLOBALS.IS_WSL:
        try:
            result = subprocess.run(
                [
                    "cmd.exe",
                    "/c",
                    "reg",
                    "query",
                    "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice",
                    "/v",
                    "Progid",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if "Progid" in output:
                    return output.split()[-1]
        except FileNotFoundError:
            pass
        return None
    elif GLOBALS.IS_WINDOWS:
        import winreg

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice",
            ) as key:
                prog_id = str(winreg.QueryValueEx(key, "Progid")[0])
                return prog_id
        except FileNotFoundError:
            pass
        except Exception:
            pass
    return None


def _posix_default_browser() -> str | None:
    # if system is macOS
    if GLOBALS.IS_MACOS:
        # Check macOS defaults
        try:
            result = subprocess.run(
                [
                    "defaults",
                    "read",
                    "com.apple.LaunchServices/com.apple.launchservices.secure",
                    "LSHandlers",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                return output
        except FileNotFoundError:
            pass
        return None

    # if system is linux or BSD
    if GLOBALS.IS_UNIX:
        # Check xdg-settings
        try:
            result = subprocess.run(
                ["xdg-settings", "get", "default-web-browser"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                default_browser = result.stdout.strip()
        except FileNotFoundError:
            pass

        # Check GNOME settings
        try:
            settings = subprocess.run(
                [
                    "gsettings",
                    "get",
                    "org.gnome.desktop.default-applications.web",
                    "schemes",
                ],
                capture_output=True,
                text=True,
            )
            if settings.returncode == 0:
                default_browser = settings.stdout.strip().strip("'")
                if default_browser:
                    return default_browser
        except FileNotFoundError:
            pass

        try:
            settings = subprocess.run(
                [
                    "gsettings",
                    "get",
                    "org.gnome.system.default-applications.browser",
                    "exec",
                ],
                capture_output=True,
                text=True,
            )
            if settings.returncode == 0:
                default_browser = settings.stdout.strip().strip("'")
                if default_browser:
                    return default_browser
        except FileNotFoundError:
            pass

        # Check KDE settings
        try:
            settings = subprocess.run(
                [
                    "kreadconfig5",
                    "--file",
                    "kdeglobals",
                    "--group",
                    "General",
                    "--key",
                    "Browser",
                ],
                capture_output=True,
                text=True,
            )
            if settings.returncode == 0:
                default_browser = settings.stdout.strip().strip("'")
                if default_browser:
                    return default_browser
        except FileNotFoundError:
            pass

        # Check XFCE settings
        try:
            settings = subprocess.run(
                [
                    "xfconf-query",
                    "-c",
                    "xfce4-session",
                    "-p",
                    "/sessions/Failsafe/Client0_Command",
                ],
                capture_output=True,
                text=True,
            )
            if settings.returncode == 0:
                default_browser = settings.stdout.strip().strip("'")
                if default_browser:
                    return default_browser
        except FileNotFoundError:
            pass

        # Check LXDE settings
        try:
            lxde_config = os.path.expanduser("~/.config/lxsession/LXDE/autostart")
            if os.path.exists(lxde_config):
                with open(lxde_config, "r") as file:
                    for line in file:
                        if line.startswith("@"):
                            return line.strip("@").split()[0]
        except Exception:
            pass

        # Check Cinnamon settings
        try:
            settings = subprocess.run(
                [
                    "gsettings",
                    "get",
                    "org.cinnamon.desktop.default-applications.browser",
                    "exec",
                ],
                capture_output=True,
                text=True,
            )
            if settings.returncode == 0:
                default_browser = settings.stdout.strip().strip("'")
                if default_browser:
                    return default_browser
        except FileNotFoundError:
            pass

        # Check MATE settings
        try:
            settings = subprocess.run(
                ["gsettings", "get", "org.mate.applications-browser", "exec"],
                capture_output=True,
                text=True,
            )
            if settings.returncode == 0:
                default_browser = settings.stdout.strip().strip("'")
                if default_browser:
                    return default_browser
        except FileNotFoundError:
            pass

        # Check i3 settings
        try:
            i3_config = os.path.expanduser("~/.config/i3/config")
            if os.path.exists(i3_config):
                with open(i3_config, "r") as file:
                    for line in file:
                        if "browser" in line:
                            return line.split()[-1].strip()
        except Exception:
            pass

        # Check Sway settings
        try:
            sway_config = os.path.expanduser("~/.config/sway/config")
            if os.path.exists(sway_config):
                with open(sway_config, "r") as file:
                    for line in file:
                        if "browser" in line:
                            return line.split()[-1].strip()
        except Exception:
            pass

        # Check XMonad settings
        try:
            xmonad_config = os.path.expanduser("~/.xmonad/xmonad.hs")
            if os.path.exists(xmonad_config):
                with open(xmonad_config, "r") as file:
                    for line in file:
                        if "browser" in line:
                            return line.split()[-1].strip()
        except Exception:
            pass

    return None


def _binary_path_from_desktop_entry(browser: str | None) -> str | None:
    if browser:
        # If the browser is not a .desktop file, return it as is
        if not browser.endswith(".desktop"):
            return browser

        for directory in DESKTOP_DIRS:
            desktop_file_path = os.path.join(directory, browser)
            if os.path.exists(desktop_file_path):
                config = configparser.ConfigParser(interpolation=None)
                config.read(desktop_file_path)

                # The desktop file format has sections like [Desktop Entry]
                if "Desktop Entry" in config and "Exec" in config["Desktop Entry"]:
                    exec_command = config["Desktop Entry"]["Exec"]

                    # Extract the binary path from the exec command
                    binary_path = exec_command.split()[0]

                    # Resolve to full path if binary is in PATH
                    binary_full_path = shutil.which(binary_path)
                    if binary_full_path:
                        return binary_full_path
                    else:
                        return binary_path
    return None


def _posix_browser_name(path: str | None) -> str:
    if path:
        for name, browser in POSIX_BROWSERS.items():
            for binary in browser.get("paths", []):
                if binary in path or path in binary:
                    return name
    return ""


def get_posix_default_browser() -> str | None:
    return _posix_browser_name(
        _binary_path_from_desktop_entry(_posix_default_browser())
    )


def get_default_browser() -> str | None:
    return get_nt_default_browser() if GLOBALS.IS_NT else get_posix_default_browser()


def get_default_from_env_vars() -> str:
    browser = os.getenv("BROWSER") or os.getenv("DEFAULT_BROWSER")
    if browser:
        return browser
    return ""


# Function to check if a browser is installed and map its name
def detect_standard_browsers() -> tuple[str, dict[str, dict[str, str]]]:
    installed_browsers: dict[str, dict[str, str]] = {}
    browsers = NT_BROWSERS.items()
    if not GLOBALS.IS_NT:
        browsers = POSIX_BROWSERS.items()
    for name, browser in browsers:
        for binary in browser.get("paths", []):
            if GLOBALS.IS_WSL:
                binary = nt_to_wsl_path(binary)
            path = shutil.which(binary)
            if path:
                installed_browsers[name] = {}
                installed_browsers[name]["path"] = path
                installed_browsers[name]["family"] = str(browser.get("family", ""))
                break  # Stop at the first detected binary for a browser

    default_browser = get_default_from_env_vars()
    if default_browser in installed_browsers:
        return default_browser, installed_browsers

    default_browser = get_default_browser() or ""
    return default_browser, installed_browsers


def nt_to_wsl_path(nt_path: str) -> str:
    # Replace backslashes with forward slashes
    wsl_path = nt_path.replace("\\", "/")

    # Replace drive letter (e.g., C:) with /mnt/c
    if ":" in wsl_path:
        drive, path = wsl_path.split(":", 1)
        wsl_path = f"/mnt/{drive.lower()}{path}"

    return wsl_path
