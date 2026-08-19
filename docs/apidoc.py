"""Generate the library API reference."""

import ast
import re
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory

from sphinx.ext.apidoc import main as apidoc

from scfile import formats
from scfile.enums import FileKind


ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parent / "scfile"
OUTPUT = ROOT / "source" / "api"
TEMPLATES = ROOT / "templates" / "apidoc"

TITLES = {
    "scfile": "API Reference",
    "scfile.convert": "🔄 Convert",
    "scfile.core": "🛠️ Core",
    "scfile.formats": "🧩 Formats",
    "scfile.io": "💾 IO",
    "scfile.structures": "🗃️ Structures",
}

FORMAT_ORDER = (
    "mcsa",
    "mcsb",
    "mcvd",
    "mcal",
    "efkmodel",
    "obj",
    "glb",
    "fbx",
    "ol",
    "dds",
    "mic",
    "png",
    "texarr",
    "zip",
    "mdat",
    "mca",
    "nbt",
    "json",
)

FORMAT_ICONS = {
    FileKind.MODEL: "🧊",
    FileKind.TEXTURE: "🧱",
    FileKind.IMAGE: "🖼️",
    FileKind.ARCHIVE: "🗃️",
    FileKind.DOCUMENT: "⚙️",
    FileKind.REGION: "🗺",
}

KIND_ORDER = (
    FileKind.MODEL,
    FileKind.TEXTURE,
    FileKind.IMAGE,
    FileKind.ARCHIVE,
    FileKind.REGION,
    FileKind.DOCUMENT,
)


def title(path: Path, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[:2] = value, "=" * 50
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def format_info() -> dict[str, tuple[FileKind, int]]:
    result = {format.value: (handler.content_type.kind, 0) for format, handler in formats.registry.decoders.items()}
    result.update(
        {
            format.value: (handler.content_type.kind, 1)
            for format, handler in formats.registry.encoders.items()
            if format.value not in result
        }
    )
    return result


def type_aliases(path: Path) -> list[tuple[str, str, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    aliases: list[tuple[str, str, str]] = []

    for index, node in enumerate(tree.body):
        if not isinstance(node, ast.TypeAlias):
            continue

        description = ""
        if index + 1 < len(tree.body):
            following = tree.body[index + 1]
            if isinstance(following, ast.Expr) and isinstance(following.value, ast.Constant):
                if isinstance(following.value.value, str):
                    description = following.value.value

        aliases.append((node.name.id, ast.unparse(node.value), description))

    return aliases


def document_types(reference: Path) -> None:
    for source in PACKAGE.rglob("*.py"):
        if "app" in source.relative_to(PACKAGE).parts:
            continue

        aliases = type_aliases(source)
        if not aliases:
            continue

        relative = source.relative_to(PACKAGE).with_suffix("")
        source_module = "scfile" if relative.name == "__init__" else f"scfile.{relative.as_posix().replace('/', '.')}"
        module = source_module
        path = reference / f"{module}.rst"
        if not path.is_file():
            module = module.rsplit(".", 1)[0]
            path = reference / f"{module}.rst"
            if not path.is_file():
                continue

        lines = path.read_text(encoding="utf-8").splitlines()
        marker = f".. automodule:: {source_module}"
        try:
            insert_at = lines.index(marker) + 1
        except ValueError:
            continue

        while insert_at < len(lines) and lines[insert_at].startswith("   :"):
            insert_at += 1

        documented: list[str] = [""]
        for name, value, description in aliases:
            documented.extend((f".. py:type:: {name}", f"   :module: {source_module}", "", f"   ``{value}``"))
            if description:
                documented.extend(("", f"   {description}"))
            documented.append("")
        lines[insert_at:insert_at] = documented
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


def style(reference: Path) -> None:
    for module, value in TITLES.items():
        path = reference / f"{module}.rst"
        if path.is_file():
            title(path, value)

    info = format_info()
    priority = {format: index for index, format in enumerate(FORMAT_ORDER)}
    kinds = {kind: index for index, kind in enumerate(KIND_ORDER)}

    for format, (kind, _) in info.items():
        path = reference / f"scfile.formats.{format}.rst"
        if path.is_file():
            title(path, f"{FORMAT_ICONS[kind]} {format.upper()}")

    path = reference / "scfile.formats.rst"
    lines = path.read_text(encoding="utf-8").splitlines()
    positions = [index for index, line in enumerate(lines) if line.startswith("   scfile.formats.")]

    def order(line: str) -> tuple[int, int, int, str]:
        format = line.rsplit(".", 1)[-1]
        kind, direction = info.get(format, (FileKind.NONE, 2))
        return kinds.get(kind, len(kinds)), direction, priority.get(format, len(priority)), format

    ordered = sorted((lines[index] for index in positions), key=order)
    for index, line in zip(positions, ordered):
        lines[index] = line

    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    for path in reference.glob("scfile*.rst"):
        content = re.sub(r"\n{3,}", "\n\n", path.read_text(encoding="utf-8"))
        path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    with TemporaryDirectory(dir=ROOT) as temporary:
        reference = Path(temporary)
        arguments = (
            "--force",
            "--no-toc",
            "--maxdepth",
            "2",
            "--templatedir",
            str(TEMPLATES),
            "--output-dir",
            str(reference),
            str(PACKAGE),
            str(PACKAGE / "app"),
        )

        if apidoc(arguments):
            raise SystemExit("API reference generation failed.")

        document_types(reference)
        style(reference)

        for path in OUTPUT.glob("scfile*.rst"):
            path.unlink()
        for path in reference.glob("scfile*.rst"):
            copy2(path, OUTPUT / path.name)


if __name__ == "__main__":
    main()
