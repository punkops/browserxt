import sys
from typer import Argument, Option, Typer
from typer import main as typer_main

from browserxt.browser import Browser
from browserxt.utils import detect_standard_browsers

from browserxt.globals import GLOBALS

app = Typer()


@app.command(
    no_args_is_help=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def main(
    browser_list: list[str] = Option(
        None,
        "--browser",
        "-b",
        show_choices=True,
        help="Specify the browser(s) to try use in preference order",
    ),
    use_wsl: bool = Option(
        False,
        "--wsl",
        help="Force use of WSL browsers (X11 required)",
        hidden=not GLOBALS.IS_WSL,
    ),
    _debug: bool = Option(
        False, "--debug", help="Print debug information", hidden=True
    ),
    ignore_default: bool = Option(
        False, "--ignore-default", help="Ignore the default browser"
    ),
    temp_profile: bool = Option(
        False,
        "--tmp",
        help="Create a new secure temporary browser profile, similar to incognito mode but with a new profile each time",
    ),
    profile: str = Option(
        "",
        "-p",
        "--profile",
        help="Use a specific browser profile with this name, a new profile with this name will be created if it does not exist",
    ),
    profile_path: str = Option(
        "",
        "--profile-path",
        help="Use an existing browser profile path, if unset, a new profile will be created",
    ),
    url: str = Argument(..., help="URL to open in the browser"),
    options: list[str] = Argument(
        default=None,
        help="Additional browser options, e.g. `--incognito` for Chrome or `--private-window` for Firefox",
    ),
) -> None:
    """Open a browser with specified positional arguments as options."""
    GLOBALS.IGNORE_WINDOWS = use_wsl
    if _debug:
        default, browsers = detect_standard_browsers()
        if GLOBALS.IS_NT:
            print(
                f"------------- Windows{('(WSL)' if GLOBALS.IS_WSL else '')} --------------"
            )
            print("Current User:", GLOBALS.USER)
            print("Home:", GLOBALS.HOME)
            print("Local Data:", GLOBALS.LOCAL_DATA)
            print("Program Files:", GLOBALS.PROGRAM_FILES)
            print("Windows Drive:", GLOBALS.WINDOWS_DRIVE)
            print("Default Browser:", default)
            print("Browsers:", list(browsers.keys()))
        else:
            print(f"------------- Posix({sys.platform}) --------------")
            print("Current User:", GLOBALS.USER)
            print("Home:", GLOBALS.HOME)
            print("Default Browser:", default)
            print("Browsers:", list(browsers.keys()))
    else:
        _browser = Browser(
            browser_list or [],
            options or [],
            ignore_default,
            profile,
            profile_path,
            True,
            temp_profile,
        )
        if not _browser.open(url):
            raise Exception("No browser detected")


typer_click_object = typer_main.get_command(app)

if __name__ == "__main__":
    app()
