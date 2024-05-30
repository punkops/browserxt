import os


def get_windows_username() -> str:
    return (
        os.popen("powershell.exe '$env:UserName'").read().strip()
        if is_running_in_wsl() and os.name != "nt"
        else ""
    )


def is_running_in_wsl() -> bool:
    try:
        with open("/proc/version") as f:
            version_info = f.read()
            if "microsoft" in version_info and "WSL" in version_info:
                return True
    except FileNotFoundError:
        pass
    return False
