import os
import sys
import platform
import subprocess


class _globals:
    """
    A class that represents global variables and properties used in the application.
    """

    IS_POSIX = os.name == "posix"
    IS_REAL_NT = os.name == "nt"
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
    _LOCAL = (
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
        if not IGNORE_WINDOWS
        else ["", ""]
    )
    _LOCAL_DATA = _LOCAL[0]
    _PROGRAM_FILES = _LOCAL[1]
    HOME_DRIVE = (
        _LOCAL_DATA.split("\\")[0] or HOME.split("\\")[0] if IS_REAL_NT else None
    )
    WINDOWS_DRIVE = _PROGRAM_FILES.split("\\")[0] or HOME_DRIVE

    @property
    def IS_NT(self) -> bool:
        return os.name == "nt" or (self.IS_WSL and not self.IGNORE_WINDOWS)

    @property
    def LOCAL_DATA(self) -> str:
        return (
            os.path.expanduser("~\\AppData\\Local")
            if self.IS_REAL_NT
            else self._LOCAL_DATA if self.IS_NT else self.HOME
        )


GLOBALS = _globals()
