from dataclasses import dataclass, field

from .binary import Reader
from .models import XYZ, Note, Slice


@dataclass(frozen=True)
class RecordHeader:
    type: int
    position: XYZ


@dataclass(frozen=True)
class RecordPayload:
    flags: int
    covers: tuple[int, ...]
    color_short: tuple[int, ...]
    color_exponent: int | None
    overlay: tuple[int, ...]
    rot: int | None
    packcovers: int | None
    ctm_data: tuple[int, ...]
    data: int
    data_ext: int | None


@dataclass(frozen=True)
class Record:
    index: int
    raw: Slice
    header: RecordHeader
    payload: RecordPayload


@dataclass
class Records:
    raw: Slice
    count: int | None = None
    items: list[Record] = field(default_factory=list)
    consumed: int = 0
    stopped: RecordHeader | None = None
    notes: list[Note] = field(default_factory=list)

    @property
    def tail(self) -> Slice:
        return Slice(
            self.raw.offset + self.consumed, len(self.raw.data) - self.consumed, self.raw.data[self.consumed :]
        )


def read(raw: Slice) -> Records:
    result = Records(raw)
    reader = Reader(raw.data)

    try:
        result.count = reader.number(">i")
        result.consumed = reader.offset
        if result.count < 0:
            result.notes.append(Note("terrain", raw.offset, "Negative records count"))
            return result

        for index in range(result.count):
            start = reader.offset
            kind, x, y, z = reader.unpack(">b3i")
            header = RecordHeader(kind, (x, y, z))

            if kind not in (0, 1):
                result.stopped = header
                result.notes.append(
                    Note("terrain", raw.offset + start, f"Unknown record type {kind}; boundary unavailable")
                )
                break

            flags = reader.number(">B")
            if flags & 0x80:
                result.stopped = header
                result.notes.append(Note("terrain", raw.offset + start, "Record uses an unknown flag bit"))
                break

            payload = RecordPayload(
                flags=flags,
                covers=reader.numbers("h", 7 if flags & 0x08 else 1),
                color_short=reader.numbers("h", 7) if flags & 0x02 else (),
                color_exponent=reader.number(">h") if flags & 0x04 else None,
                overlay=reader.numbers("b", 7) if flags & 0x01 else (),
                rot=reader.number(">h") if flags & 0x10 else None,
                packcovers=reader.number(">b") if flags & 0x20 else None,
                ctm_data=reader.numbers("b", 6) if flags & 0x40 else (),
                data=reader.number(">i"),
                data_ext=reader.number(">i") if kind == 1 else None,
            )
            record_raw = Slice(raw.offset + start, reader.offset - start, raw.data[start : reader.offset])
            result.items.append(Record(index, record_raw, header, payload))
            result.consumed = reader.offset

    except EOFError as error:
        result.notes.append(Note("terrain", raw.offset + reader.offset, str(error)))

    if result.tail.data and not result.notes:
        result.notes.append(Note("terrain", result.tail.offset, "Bytes remain after declared records"))

    return result
