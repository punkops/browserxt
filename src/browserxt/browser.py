import os
import shutil
import subprocess

import wslPath  # type: ignore[import-untyped]

from browserxt.utils import is_running_in_wsl

BROWSERS = {
    "posix": {
        "chrome": ["google-chrome-stable", "google-chrome", "chrome"],
        "chromium": ["chromium", "chromium-browser"],
        "brave": ["brave", "brave-browser"],
        "edge": ["microsoft-edge-stable", "microsoft-edge", "edge"],
    },
    "nt": {
        "chrome": [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        ],
        "brave": [
            "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        ],
        "edge": [
            "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
            "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        ],
    },
}

BROWSER_LIST = ["chrome", "chromium", "brave", "edge"]


class ExtensibleBrowser:
    def __init__(self, name: str = "", options: list[str] = []) -> None:
        self.name = name
        self.set_options(options)

    def set_options(self, options: list[str]) -> None:
        self.options = options
        if "edge" in self.name:
            self.options = [arg.replace("incognito", "inprivate") for arg in options]

    def open(self, url: str) -> bool:
        cmdline = [self.name] + self.options + [url]
        try:
            if os.name == "nt":
                p = subprocess.Popen(
                    cmdline, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
                )
            else:
                p = subprocess.Popen(
                    cmdline,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                    close_fds=True,
                )
            return True
        except OSError:
            return False


class Browser:
    def __init__(
        self, prefered: list[str] = [], options: list[str] = [], wsl: bool = False
    ) -> None:
        self.is_posix = os.name == "posix"
        self.is_nt = os.name == "nt"
        self.prefered = prefered + BROWSER_LIST

        # if wsl is True, then it will only use the WSL browsers and skip the windows ones
        self.is_wsl = not wsl & is_running_in_wsl()
        self._browsers = {}  # type: dict[str, ExtensibleBrowser]
        self.options = options
        self.register_standards_browsers()

    def open(self, url: str, using: str = "") -> bool:
        browser = self.get(using)
        if browser is not None:
            return browser.open(url)
        return False

    def get(self, using: str = "") -> ExtensibleBrowser | None:
        if using != "":
            alternatives = [using]
        else:
            alternatives = self.prefered
        for browser in alternatives:
            if browser in self._browsers:
                instance = self._browsers.get(browser, None)
                if instance is not None:
                    return instance
        return None

    def register(self, name: str, instance: ExtensibleBrowser | None) -> None:
        self._browsers[name] = instance  # type: ignore[assignment]

    def register_standards_browsers(self) -> None:
        try:
            for browser in self.prefered:
                for path in BROWSERS[os.name].get(browser, []):
                    path = shutil.which(path)  # type: ignore[assignment]
                    if path:
                        self.register(browser, ExtensibleBrowser(path, self.options))
        except KeyError:
            raise NotImplementedError(
                f"Browser registration not implemented for this platform: {os.name}"
            )

        if self.is_wsl:
            self._browsers = {}
            for browser in self.prefered:
                for path in BROWSERS["nt"].get(browser, []):
                    path = shutil.which(wslPath.to_posix(path))
                    if path:
                        self.register(browser, ExtensibleBrowser(path, self.options))

        self.register_chromium()

    def register_chromium(self) -> None:
        if "chrome" not in self._browsers:
            if "chromium" in self._browsers:
                self.register("chrome", self.get("chromium"))
            elif "brave" in self._browsers:
                self.register("chrome", self.get("brave"))
                self.register("chromium", self.get("brave"))
            elif "edge" in self._browsers:
                self.register("chrome", self.get("edge"))
                self.register("chromium", self.get("edge"))
                self.register("brave", self.get("edge"))
