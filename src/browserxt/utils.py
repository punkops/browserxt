import os
import sys
import json
import shutil
import platform
import subprocess
import configparser

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


def get_posix_default_browser() -> str | None:
    # Check xdg-settings (Linux)
    try:
        result = subprocess.run(
            ["xdg-settings", "get", "default-web-browser"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass

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
            # Implement parsing to find the default browser if necessary
            return output
    except FileNotFoundError:
        pass

    # Check GNOME settings
    try:
        result = subprocess.run(
            [
                "gsettings",
                "get",
                "org.gnome.system.default-applications.browser",
                "exec",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip().strip("'")
    except FileNotFoundError:
        pass

    # Check KDE settings
    try:
        result = subprocess.run(
            ["xdg-mime", "query", "default", "x-scheme-handler/http"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass

    # Check XFCE settings
    try:
        result = subprocess.run(
            [
                "xfconf-query",
                "--channel",
                "xfce4-session",
                "--property",
                "/sessions/Failsafe/Client0_Command",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
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
    except Exception as e:
        pass

    # Check Cinnamon settings
    try:
        result = subprocess.run(
            [
                "gsettings",
                "get",
                "org.cinnamon.desktop.default-applications.browser",
                "exec",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip().strip("'")
    except FileNotFoundError:
        pass

    # Check MATE settings
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.mate.applications-browser", "exec"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip().strip("'")
    except FileNotFoundError:
        pass

    # Method 10: Check i3 settings
    try:
        i3_config = os.path.expanduser("~/.config/i3/config")
        if os.path.exists(i3_config):
            with open(i3_config, "r") as file:
                for line in file:
                    if "browser" in line:
                        return line.split()[-1].strip()
    except Exception as e:
        pass

    # Method 11: Check Sway settings
    try:
        sway_config = os.path.expanduser("~/.config/sway/config")
        if os.path.exists(sway_config):
            with open(sway_config, "r") as file:
                for line in file:
                    if "browser" in line:
                        return line.split()[-1].strip()
    except Exception as e:
        pass

    # Method 12: Check XMonad settings
    try:
        xmonad_config = os.path.expanduser("~/.xmonad/xmonad.hs")
        if os.path.exists(xmonad_config):
            with open(xmonad_config, "r") as file:
                for line in file:
                    if "browser" in line:
                        return line.split()[-1].strip()
    except Exception as e:
        pass

    return None


def get_binary_path_from_desktop_entry(browser: str | None) -> str | None:
    if not browser:
        return None
    # If the browser is not a .desktop file, return it as is
    if not browser.endswith(".desktop"):
        return browser

    # Common directories for .desktop files
    desktop_dirs = [
        "/usr/share/applications/",
        "/usr/local/share/applications/",
        os.path.expanduser("~/.local/share/applications/"),
        "/etc/profiles/per-user/$USER/share/applications/",
        "/run/current-system/sw/share/applications/",
        os.path.expanduser("~/.nix-profile/share/applications/"),
    ]

    for directory in desktop_dirs:
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


def get_posix_browser_name(path: str | None) -> str:
    if not path:
        return ""
    for name, browser in POSIX_BROWSERS.items():
        for binary in browser.get("paths", []):
            if binary in path:
                return name
    return ""


def get_default_from_env_vars() -> str:
    browser = os.getenv("BROWSER") or os.getenv("DEFAULT_BROWSER")
    if browser:
        return browser
    return ""


# Function to check if a browser is installed and map its name
def detect_posix() -> tuple[str, dict[str, dict[str, str]]]:
    installed_browsers: dict[str, dict[str, str]] = {}
    for name, browser in POSIX_BROWSERS.items():
        for binary in browser.get("paths", []):
            path = shutil.which(binary)
            if path:
                installed_browsers[name] = {}
                installed_browsers[name]["path"] = path
                installed_browsers[name]["family"] = str(browser.get("family", ""))
                break  # Stop at the first detected binary for a browser

    default_browser = get_default_from_env_vars()
    if default_browser in installed_browsers:
        return default_browser, installed_browsers

    default_browser = get_posix_browser_name(
        get_binary_path_from_desktop_entry(get_posix_default_browser())
    )
    return default_browser, installed_browsers


def detect_nt() -> tuple[str, dict[str, dict[str, str]]]:
    # Path to the PowerShell script
    powershell_script_path = os.path.join(
        os.path.dirname(__file__), "scripts/detect_browsers.ps1"
    )
    try:
        # Run the PowerShell script
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                powershell_script_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        # Load the JSON output into a Python dictionary
        json_output = json.loads(result.stdout)

        default_browser = get_default_from_env_vars()
        if default_browser in json_output.get("browsers", {}):
            return default_browser, json_output.get("browsers", {})

        return json_output.get("default", ""), json_output.get("browsers", {})
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the PowerShell script: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON output: {e}")

    return "", {}


def get_windows_username() -> str | None:
    return (
        os.popen("powershell.exe '$env:UserName'").read().strip()
        if is_running_in_wsl() and os.name != "nt"
        else None
    )


def is_running_in_wsl() -> bool:
    if (os.environ.get("SKIP_WSL_CHECK") != None) | (sys.platform != "linux"):
        return False
    try:
        with open("/proc/version") as f:
            version_info = f.read()
            if "microsoft" in version_info and "WSL" in version_info:
                return True
    except FileNotFoundError:
        pass

    if "WSL_DISTRO_NAME" in os.environ:
        return True

    if "WT_SESSION" in os.environ and "Windows Terminal" in platform.system():
        return True

    return False


def nt_to_wsl_path(nt_path: str) -> str:
    # Replace backslashes with forward slashes
    wsl_path = nt_path.replace("\\", "/")

    # Replace drive letter (e.g., C:) with /mnt/c
    if ":" in wsl_path:
        drive, path = wsl_path.split(":", 1)
        wsl_path = f"/mnt/{drive.lower()}{path}"

    return wsl_path
