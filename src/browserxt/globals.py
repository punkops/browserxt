import os
import platform
import subprocess
import sys


class _globals:
    """A class that represents global variables and properties used in the application."""

    USER = os.environ.get("USER") or os.environ.get("USERNAME")
    IS_POSIX = os.name == "posix"
    IS_WINDOWS = os.name == "nt"
    IS_LINUX = sys.platform == "linux"
    IS_MACOS = sys.platform == "darwin"
    IS_BSD = sys.platform in ["freebsd", "openbsd", "netbsd"]
    IS_UNIX = IS_LINUX or IS_BSD
    HOME = os.path.expanduser("~")
    IS_WSL = (
        (os.environ.get("SKIP_WSL_CHECK") != None) | (sys.platform != "linux")
        or (
            "microsoft" in open("/proc/version").read()
            and "WSL" in open("/proc/version").read()
        )
        if "WSL_DISTRO_NAME" in os.environ
        else (
            True
            if "WT_SESSION" in os.environ and "Windows Terminal" in platform.system()
            else False
        )
    )
    IGNORE_WINDOWS = IS_WSL and "IGNORE_WINDOWS" in os.environ
    _LOCAL: list[str] = (
        [
            os.environ.get("LOCALAPPDATA", ""),
            os.environ.get("PROGRAMFILES", ""),
        ]
        if IS_WINDOWS
        else (
            subprocess.run(
                [
                    "cmd.exe",
                    "/c",
                    "echo",
                    "%LOCALAPPDATA%_%PROGRAMFILES%",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            .stdout.strip()
            .split("_")
            if not IGNORE_WINDOWS and IS_WSL
            else ["", ""]
        )
    )
    _LOCAL_DATA = _LOCAL[0]
    _PROGRAM_FILES = _LOCAL[1]
    HOME_DRIVE = (
        _LOCAL_DATA.split("\\")[0] or HOME.split("\\")[0] if IS_WINDOWS else None
    )
    WINDOWS_DRIVE = _PROGRAM_FILES.split("\\")[0] or HOME_DRIVE

    @property
    def IS_NT(self) -> bool:
        return os.name == "nt" or (self.IS_WSL and not self.IGNORE_WINDOWS)

    @property
    def LOCAL_DATA(self) -> str:
        return self._LOCAL_DATA if self._LOCAL_DATA else ""

    @property
    def PROGRAM_FILES(self) -> str:
        return self._PROGRAM_FILES if self._PROGRAM_FILES else ""


GLOBALS = _globals()
