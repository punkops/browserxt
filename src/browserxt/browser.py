import os
import subprocess

from browserxt.utils import is_running_in_wsl, nt_to_wsl_path, detect_nt, detect_posix


class ExtensibleBrowser:
    def __init__(self, name: str, path: str, options: list[str] = []) -> None:
        self.name = name
        self.path = path
        self.set_options(options)

    def set_options(self, options: list[str]) -> None:
        self.options = options
        if self.name == "edge":
            self.options = [arg.replace("incognito", "inprivate") for arg in options]

    def open(self, url: str) -> bool:
        cmdline = [self.path] + self.options + [url]
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
        self.options = options
        self._platform = os.name
        self._wsl = wsl
        self._prefered = prefered
        self._tryorder: list[str] = []
        self._browsers: dict[str, ExtensibleBrowser] = {}
        self.detect_browsers()

    def detect_browsers(self) -> None:
        if self._platform == "nt" or (is_running_in_wsl() and not self._wsl):
            default, browsers = detect_nt()
            for name, path in browsers.items():
                if is_running_in_wsl():
                    path = nt_to_wsl_path(path)
                self.register(name, ExtensibleBrowser(name, path, self.options))
            default_instance = self._browsers.get(default, None)
            if default_instance:
                self.register("default", default_instance)
        else:
            default, browsers = detect_posix()
            for name, path in browsers.items():
                self.register(name, ExtensibleBrowser(name, path, self.options))
            default_instance = self._browsers.get(default, None)
            if default_instance:
                self.register("default", default_instance)

    def open(self, url: str, using: str = "") -> bool:
        browser = self.get(using)
        if browser:
            return browser.open(url)
        return False

    def get(self, using: str = "") -> ExtensibleBrowser | None:
        if using != "":
            if using in self._browsers:
                return self._browsers.get(using, None)

        for browser in self._prefered + self._tryorder:
            if browser in self._browsers:
                return self._browsers.get(browser, None)

        return None

    def register(self, name: str, instance: ExtensibleBrowser) -> None:
        self._browsers[name] = instance
        if name == "default":
            self._tryorder.insert(0, name)
        else:
            self._tryorder.append(name)
