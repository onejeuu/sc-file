from typing import Any

from .content import ArchiveContent, DocumentContent, ImageContent, ModelContent, RegionContent, TextureContent
from .decoder import Decoder
from .encoder import Encoder


type ModelDecoder = type[Decoder[ModelContent, Any]]
type ModelEncoder = type[Encoder[ModelContent, Any]]

type TextureDecoder = type[Decoder[TextureContent, Any]]
type TextureEncoder = type[Encoder[TextureContent, Any]]

type ImageDecoder = type[Decoder[ImageContent, Any]]
type ImageEncoder = type[Encoder[ImageContent, Any]]

type ArchiveDecoder = type[Decoder[ArchiveContent, Any]]
type ArchiveEncoder = type[Encoder[ArchiveContent, Any]]

type DocumentDecoder = type[Decoder[DocumentContent, Any]]
type DocumentEncoder = type[Encoder[DocumentContent, Any]]

type RegionDecoder = type[Decoder[RegionContent, Any]]
type RegionEncoder = type[Encoder[RegionContent, Any]]
