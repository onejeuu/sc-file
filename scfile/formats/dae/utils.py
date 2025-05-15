from typing import Optional
from xml.etree.ElementTree import Element, SubElement

import numpy as np


def create_source(
    parent: Element,
    id: str,
    name: str,
    data: np.ndarray,
    tag: str = "float_array",
    count: Optional[int] = None,
) -> Element:
    count = count or len(data)
    source = SubElement(parent, "source", id=f"{id}-{name}")
    array = SubElement(source, tag, id=f"{id}-{name}-array", count=str(count))
    array.text = " ".join(map(str, data.flatten()))
    return source


def add_accessor(
    source: Element,
    id: str,
    name: str,
    count: int,
    components: list[str],
    datatype: str,
    stride: Optional[int] = None,
) -> None:
    array_id = f"#{id}-{name}-array"
    stride = stride or len(components)

    common = SubElement(source, "technique_common")
    accessor = SubElement(common, "accessor", source=array_id, count=str(count), stride=str(stride))

    for component in components:
        accessor.append(Element("param", name=component, type=datatype))
