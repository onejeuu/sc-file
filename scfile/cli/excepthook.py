import sys
import traceback
from typing import Any

import click
from rich import print

from scfile.enums import EchoPrefix as PREFIX


def excepthook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: Any,
):
    if isinstance(exc_value, click.ClickException):
        print(PREFIX.CLICK, exc_value)
    else:
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print()
        print(PREFIX.EXCEPTION, f"{exc_type.__name__} - {exc_value}.")

    sys.exit(1)
