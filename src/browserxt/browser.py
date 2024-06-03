import os
import tempfile
import subprocess

from browserxt.utils import nt_to_wsl_path, sort_tryoder, detect_standard_browsers

from browserxt.profiles import (
    get_chromium_profile_options,
    get_firefox_profile_options,
)

from browserxt.globals import GLOBALS


class ExtensibleBrowser:
    def __init__(
        self,
        name: str,
        path: str,
        options: list[str] = [],
        profile: str = "",
        user_data_path: str = "",
        create: bool = True,
        family: str = "unknown",
    ) -> None:
        self.name = name
        self.family = family
        self.path = path
        self.set_options(options.copy())
        if profile != "":
            self.set_profile_options(profile, user_data_path, create)

    def set_options(self, options: list[str]) -> None:
        self.options = options

    # Dummy method to be overridden by subclasses
    def set_profile_options(
        self,
        name: str,
        user_data_path: str = "",
        create: bool = True,
    ) -> None:
        pass

    def is_running_in_wsl(self) -> bool:
        return GLOBALS.IS_WSL and not self.path.startswith("/mnt")

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


class ChromiumBrowser(ExtensibleBrowser):
    def __init__(
        self,
        name: str,
        path: str,
        options: list[str] = [],
        profile: str = "",
        user_data_path: str = "",
        create: bool = True,
        family: str = "chromium",
    ) -> None:
        super().__init__(name, path, options, profile, user_data_path, create, family)

    def set_profile_options(
        self,
        name: str,
        user_data_path: str = "",
        create: bool = True,
    ) -> None:
        self.options += get_chromium_profile_options(name, user_data_path, create)

    def set_options(self, options: list[str]) -> None:
        super().set_options(options)
        if self.name == "edge":
            self.options = [arg.replace("incognito", "inprivate") for arg in options]


class FirefoxBrowser(ExtensibleBrowser):
    def __init__(
        self,
        name: str,
        path: str,
        options: list[str] = [],
        profile: str = "",
        user_data_path: str = "",
        create: bool = True,
        family: str = "firefox",
    ) -> None:
        super().__init__(name, path, options, profile, user_data_path, create, family)

    def set_profile_options(
        self,
        name: str,
        user_data_path: str = "",
        create: bool = True,
    ) -> None:
        self.options += get_firefox_profile_options(name, user_data_path, create)


class UnknownBrowser(ExtensibleBrowser):
    def __init__(self, name: str, path: str, options: list[str] = []) -> None:
        super().__init__(name, path, options, family="unknown")


def get_browser_class(
    family: str,
) -> type[ExtensibleBrowser]:
    if family == "firefox":
        return FirefoxBrowser
    elif family == "chromium":
        return ChromiumBrowser
    return UnknownBrowser


class Browser:
    def __init__(
        self,
        prefered: list[str] = [],
        options: list[str] = [],
        ignore_default: bool = False,
        profile: str = "",
        user_data_path: str = "",
        create: bool = True,
        tmp_profile: bool = False,
    ) -> None:
        self.options = options.copy()
        self._platform = os.name
        self._ignore_default = ignore_default
        self._prefered = prefered.copy()
        self._tryorder: list[str] = []
        self._browsers: dict[str, ExtensibleBrowser] = {}
        self._profile = profile
        self._user_data_path = user_data_path
        self._create = create
        if tmp_profile:
            _base: str = ""
            _temp: str = ""
            if GLOBALS.IS_NT and GLOBALS.IS_WSL:
                _temp = tempfile.mkdtemp(
                    dir=nt_to_wsl_path(f"{GLOBALS.LOCAL_DATA}\\Temp")
                )
                _base = os.path.basename(_temp)
                _temp = f"{GLOBALS.LOCAL_DATA}\\Temp\\{_base}"
            else:
                _temp = tempfile.mkdtemp()
                _base = os.path.basename(_temp)
            self._profile = _base
            self._user_data_path = _temp
            self._create = False
        self.detect_browsers()
        self._tryorder = sort_tryoder(self._tryorder)

    def detect_browsers(self) -> None:
        default, browsers = detect_standard_browsers()
        for name, browser in browsers.items():
            path = browser.get("path", "")
            family = browser.get("family", "")
            self.register(
                name,
                get_browser_class(family)(
                    name=name,
                    path=path,
                    options=self.options,
                    profile=self._profile,
                    user_data_path=self._user_data_path,
                    create=self._create,
                ),
            )
        default_instance = self._browsers.get(default, None)
        if default_instance and not self._ignore_default:
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
