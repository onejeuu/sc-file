from typing import Any

from scfile.structures.textures import CubemapTexture, DefaultTexture

from .content import ImageContent, ModelContent, NbtContent, RegionContent, TexarrContent, TextureContent
from .decoder import FileDecoder
from .encoder import FileEncoder


type ModelDecoder = type[FileDecoder[ModelContent, Any]]
type ModelEncoder = type[FileEncoder[ModelContent, Any]]

type TextureData = DefaultTexture | CubemapTexture

type TextureDecoder = type[FileDecoder[TextureContent[TextureData], Any]]
type TextureEncoder = type[FileEncoder[TextureContent[TextureData], Any]]

type CubemapDecoder = type[FileDecoder[TextureContent[CubemapTexture], Any]]
type CubemapEncoder = type[FileEncoder[TextureContent[CubemapTexture], Any]]

type AnyTextureDecoder = TextureDecoder
type AnyTextureEncoder = TextureEncoder

type ImageDecoder = type[FileDecoder[ImageContent, Any]]
type ImageEncoder = type[FileEncoder[ImageContent, Any]]

type TexarrDecoder = type[FileDecoder[TexarrContent, Any]]
type TexarrEncoder = type[FileEncoder[TexarrContent, Any]]

type NbtDecoder = type[FileDecoder[NbtContent, Any]]
type NbtEncoder = type[FileEncoder[NbtContent, Any]]

type RegionDecoder = type[FileDecoder[RegionContent, Any]]
type RegionEncoder = type[FileEncoder[RegionContent, Any]]
