import click

from tools.commands.audit.__main__ import main as audit
from tools.commands.info.__main__ import main as info
from tools.commands.profile.__main__ import main as profile


@click.group(
    commands={
        "audit": audit,
        "info": info,
        "profile": profile,
    }
)
def main() -> None:
    """Development tools."""


if __name__ == "__main__":
    main()
