from typer import Argument, Option, Typer
from typer import main as typer_main

from browserxt.browser import Browser
from browserxt.utils import is_running_in_wsl

app = Typer()


@app.command(
    no_args_is_help=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def main(
    browser: list[str] = Option(
        None,
        "--browser",
        "-b",
        help="Specify the browser(s) to try use in preference order",
    ),
    wsl: bool = Option(
        False,
        "--wsl",
        help="Force use of WSL browsers (X11 required)",
        hidden=not is_running_in_wsl(),
    ),
    url: str = Argument(..., help="URL to open in the browser"),
    options: list[str] = Argument(
        default=None,
        help="Additional browser options, e.g. `--incognito` for Chrome or `--private-window` for Firefox",
    ),
) -> None:
    """Open a browser with specified positional arguments as options."""
    _browser = Browser(browser or [], options or [], wsl)
    _browser.open(url)


typer_click_object = typer_main.get_command(app)

if __name__ == "__main__":
    app()
