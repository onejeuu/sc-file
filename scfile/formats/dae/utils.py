from xml.etree.ElementTree import Element, SubElement

import numpy as np


def array_text(data: np.ndarray) -> str:
    values = data.ravel().tolist()

    match data.dtype.kind:
        case "f":
            template = "%.9g "

        case "i" | "u":
            template = "%d "

        case _:
            return " ".join(map(str, values))

    return ((template * len(values)) % tuple(values)).rstrip()


def create_source(
    parent: Element,
    id: str,
    name: str,
    data: np.ndarray,
    tag: str = "float_array",
    count: int | None = None,
) -> Element:
    count = data.size if count is None else count
    source = SubElement(parent, "source", id=f"{id}-{name}")
    array = SubElement(source, tag, id=f"{id}-{name}-array", count=str(count))
    array.text = array_text(data)
    return source


def add_accessor(
    source: Element,
    id: str,
    name: str,
    count: int,
    components: list[str],
    datatype: str,
    stride: int | None = None,
) -> None:
    array_id = f"#{id}-{name}-array"
    stride = stride or len(components)

    common = SubElement(source, "technique_common")
    accessor = SubElement(common, "accessor", source=array_id, count=str(count), stride=str(stride))

    for component in components:
        accessor.append(Element("param", name=component, type=datatype))
