"""Update translations for authored documentation."""

import subprocess
import sys
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po, write_po


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
LOCALE = ROOT / "locale"
CHANGELOG = SOURCE / "v"

LANGUAGE = "ru"
INCLUDE_LINENO = False

NO_TRANSLATION = "No translation required."
NO_TRANSLATION_BORDER = "=" * 76

HEADER = f"""msgid ""
msgstr ""
"Language: {LANGUAGE}\\n"
"Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && "
"n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: 8bit\\n\""""


def documents() -> list[Path]:
    return [
        path
        for path in sorted(SOURCE.rglob("*.rst"))
        if not path.name.startswith("_")
        and not path.is_relative_to(CHANGELOG)
        and ".. automodule::" not in path.read_text(encoding="utf-8")
    ]


def unchanged_messages() -> dict[Path, set[str | tuple[str, ...]]]:
    result = {}

    for path in (LOCALE / LANGUAGE / "LC_MESSAGES").rglob("*.po"):
        with path.open(encoding="utf-8") as stream:
            catalog = read_po(stream)

        unchanged = set()
        for message in catalog:
            section = any(NO_TRANSLATION in comment for comment in message.user_comments)
            if section and message.id:
                unchanged.add(message.id)

        result[path] = unchanged

    return result


def clean_catalogs(unchanged: dict[Path, set[str | tuple[str, ...]]]) -> None:
    for path in (LOCALE / LANGUAGE / "LC_MESSAGES").rglob("*.po"):
        with path.open(encoding="utf-8") as stream:
            catalog = read_po(stream)

        translated = []
        untranslated = []

        for message in catalog:
            if not message.id:
                continue

            message.locations = []

            message.user_comments = [
                comment for comment in message.user_comments if comment not in (NO_TRANSLATION, NO_TRANSLATION_BORDER)
            ]

            if message.string == message.id or message.id in unchanged[path]:
                message.string = ""
                untranslated.append(message)
            else:
                translated.append(message)

        if untranslated:
            untranslated[0].user_comments.extend((NO_TRANSLATION_BORDER, NO_TRANSLATION, NO_TRANSLATION_BORDER))

        ordered = Catalog()
        ordered.mime_headers = []

        for message in (*translated, *untranslated):
            ordered[message.id] = message

        output = BytesIO()
        write_po(output, ordered, omit_header=True, include_lineno=INCLUDE_LINENO)
        messages = output.getvalue().decode().rstrip()

        path.write_text(f"{HEADER}\n\n{messages}\n", encoding="utf-8", newline="\n")


def main() -> None:
    unchanged = unchanged_messages()

    with TemporaryDirectory(dir=LOCALE) as directory:
        pot = Path(directory)

        subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-b",
                "gettext",
                "-E",
                str(SOURCE),
                str(pot),
                *(str(path) for path in documents()),
            ],
            check=True,
        )

        subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx_intl",
                "update",
                "-p",
                str(pot),
                "-d",
                str(LOCALE),
                "-l",
                LANGUAGE,
                "--no-obsolete",
                "-j",
                "1",
            ],
            check=True,
        )

        clean_catalogs(unchanged)


if __name__ == "__main__":
    main()
