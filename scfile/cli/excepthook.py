import sys
import traceback
from typing import Any

import click
from rich import print

from scfile.consts import CLI

from .enums import Prefix


def excepthook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: Any):
    if isinstance(exc_value, click.ClickException):
        print(Prefix.CLIERROR, exc_value)

    else:
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print("\n", Prefix.EXCEPTION, exc_type.__name__, "-", exc_value)
        click.pause(CLI.PAUSE_TEXT)

    sys.exit(1)
