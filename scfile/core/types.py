from typing import Any

from scfile.structures.textures import CubemapTexture, DefaultTexture

from .content import ImageContent, ModelContent, NbtContent, RegionContent, TexarrContent, TextureContent
from .decoder import FileDecoder
from .encoder import FileEncoder


ModelDecoder = type[FileDecoder[ModelContent, Any]]
ModelEncoder = type[FileEncoder[ModelContent, Any]]

TextureData = DefaultTexture | CubemapTexture

TextureDecoder = type[FileDecoder[TextureContent[TextureData], Any]]
TextureEncoder = type[FileEncoder[TextureContent[TextureData], Any]]

CubemapDecoder = type[FileDecoder[TextureContent[CubemapTexture], Any]]
CubemapEncoder = type[FileEncoder[TextureContent[CubemapTexture], Any]]

AnyTextureDecoder = TextureDecoder
AnyTextureEncoder = TextureEncoder

ImageDecoder = type[FileDecoder[ImageContent, Any]]
ImageEncoder = type[FileEncoder[ImageContent, Any]]

TexarrDecoder = type[FileDecoder[TexarrContent, Any]]
TexarrEncoder = type[FileEncoder[TexarrContent, Any]]

NbtDecoder = type[FileDecoder[NbtContent, Any]]
NbtEncoder = type[FileEncoder[NbtContent, Any]]

RegionDecoder = type[FileDecoder[RegionContent, Any]]
RegionEncoder = type[FileEncoder[RegionContent, Any]]
