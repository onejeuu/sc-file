from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar

from scfile import exceptions
from scfile.app.enums import TaskKind
from scfile.app.events import TaskEvent, TaskItem, TaskStarted
from scfile.convert import mapmerge
from scfile.convert.mapmerge import Tiles
from scfile.options import Options

from .base import Task, TaskContext


class MapImageFormat(StrEnum):
    JPEG = "JPEG"
    PNG = "PNG"

    @classmethod
    def parse(cls, output: Path) -> "MapImageFormat | None":
        match output.suffix.lower():
            case ".jpg" | ".jpeg":
                return cls.JPEG
            case ".png":
                return cls.PNG

    @property
    def suffix(self) -> str:
        match self:
            case self.JPEG:
                return ".jpg"
            case self.PNG:
                return ".png"

    def save(self, value: int | None = None) -> dict[str, Any]:
        match self:
            case self.JPEG:
                return {"format": self.value, "quality": mapmerge.JPEG_QUALITY if value is None else value}
            case self.PNG:
                compression = mapmerge.PNG_COMPRESSION if value is None else value
                return {"format": self.value, "compress_level": compression}

    def estimate(self, pixels: int, value: int) -> tuple[int, int]:
        """Estimate encoded byte range from current game maps."""

        match self:
            case self.JPEG:
                scale = (10 / (102 - value)) ** 0.8
                return round(pixels * scale * 0.10), round(pixels * scale * 0.20)
            case self.PNG:
                if value == 0:
                    size = pixels * 3
                    return size, size
                scale = 1 + 0.6 / value**2.5
                return round(pixels * scale * 0.5), round(pixels * scale)


@dataclass(frozen=True, slots=True)
class MapMergeTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.MAPMERGE

    tiles: Tiles
    output: Path
    options: Options
    save: mapmerge.SaveOptions

    def run(self, context: TaskContext) -> Iterator[TaskEvent]:
        yield TaskStarted(self.kind, len(self.tiles) + 1, self.output)

        try:
            result = mapmerge.render(
                self.tiles,
                self.output,
                options=self.options,
                save=self.save,
                cancelled=context.cancelled.is_set,
                progress=lambda path: context.advance(str(path)),
            )

        except exceptions.MergeInterrupted:
            return

        source = next(iter(self.tiles.values()))
        yield TaskItem(str(source), result.output, f"Merged {result.tiles} tiles")
