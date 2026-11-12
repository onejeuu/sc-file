import os
import traceback
from collections.abc import Iterator
from concurrent.futures import FIRST_COMPLETED, Future, ProcessPoolExecutor, wait
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from scfile import exceptions
from scfile.app.enums import TaskKind
from scfile.app.events import TaskError, TaskEvent, TaskItem, TaskItemFailure, TaskStarted
from scfile.app.mapcache import options_for_path
from scfile.convert import mapcache
from scfile.core import Resources
from scfile.formats.mca import mappings
from scfile.options import Options

from .base import Task, TaskContext


type MapCacheRegion = tuple[mapcache.Region, list[Path]]
_MERGE_FUNCTION = mapcache.merge


def _merge_process(
    region: MapCacheRegion,
    output: Path,
    options: Options,
) -> mapcache.MergeResult:
    resources = Resources({mappings.RESOURCE_KEY: mappings.build(options.mca_mappings)})
    return mapcache.merge(region[0], region[1], output, options, resources=resources)


@dataclass(frozen=True, slots=True)
class MapCacheTask(Task):
    kind: ClassVar[TaskKind] = TaskKind.MAPCACHE

    source: Path
    output: Path | None
    options: Options
    workers: int | None = None

    def _merge(
        self,
        region: MapCacheRegion,
        context: TaskContext,
        options: Options | None = None,
        resources: Resources | None = None,
    ) -> TaskItem | TaskItemFailure | None:
        key, paths = region
        output = self.output or self.source.with_name(f"{self.source.name}_mca")
        source = f"({key.x}, {key.z})"

        try:
            filename, chunks = mapcache.merge(
                key,
                paths,
                output,
                options if options is not None else self.options,
                context.cancelled.is_set,
                resources,
            )
            return TaskItem(
                output=output / filename,
                detail=f"Merged {chunks} chunks",
            )

        except exceptions.MergeInterrupted:
            return None

        except exceptions.ScFileException as error:
            return TaskItemFailure(error.location or source, error)

        except OSError as error:
            return TaskItemFailure(str(error.filename or source), error)

        except Exception as error:
            return TaskItemFailure(source, error, traceback.format_exc())

    def run(
        self,
        context: TaskContext,
    ) -> Iterator[TaskEvent]:
        output = (self.output or self.source.with_name(f"{self.source.name}_mca")).resolve()
        options = options_for_path(self.options, self.source)

        result = mapcache.scan(self.source, context.cancelled.is_set)
        mapping = mapcache.group(result.paths)
        yield TaskStarted(self.kind, len(mapping), output)

        for error in result.errors:
            yield TaskError(error, source=error.filename)

        if not result.paths:
            if not result.errors:
                yield TaskError(exceptions.RegionError("No MDAT files found.", location=str(self.source)))
            return

        if not mapping:
            yield TaskError(exceptions.RegionError("No valid regions found.", location=str(self.source)))
            return

        resources = Resources({mappings.RESOURCE_KEY: mappings.build(options.mca_mappings)})
        output.mkdir(parents=True, exist_ok=True)

        regions = list(mapping.items())
        if len(regions) == 1 or mapcache.merge is not _MERGE_FUNCTION:
            for region in regions:
                if context.stopped:
                    break

                result = self._merge(region, context, options, resources)
                if result is not None:
                    yield result

            return

        workers = min(self.workers or os.cpu_count() or 4, len(regions))
        with ProcessPoolExecutor(max_workers=workers) as executor:
            pending: dict[Future[mapcache.MergeResult], MapCacheRegion] = {
                executor.submit(_merge_process, region, output, options): region for region in regions
            }

            while pending and not context.stopped:
                done, _ = wait(pending, return_when=FIRST_COMPLETED)

                for future in done:
                    region = pending.pop(future)
                    try:
                        result = future.result()
                        yield TaskItem(
                            output=output / result.filename,
                            detail=f"Merged {result.chunks} chunks",
                        )

                    except exceptions.MergeInterrupted:
                        continue

                    except exceptions.ScFileException as error:
                        yield TaskItemFailure(error.location or f"({region[0].x}, {region[0].z})", error)

                    except OSError as error:
                        yield TaskItemFailure(str(error.filename or region[0]), error)

                    except Exception as error:
                        yield TaskItemFailure(
                            f"({region[0].x}, {region[0].z})",
                            error,
                            traceback.format_exc(),
                        )

            if context.stopped:
                for future in pending:
                    future.cancel()
