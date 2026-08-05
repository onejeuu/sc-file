from typing import Any

from scfile.structures.textures import CubemapTexture, DefaultTexture

from .content import DocumentContent, ImageContent, ModelContent, RegionContent, TexarrContent, TextureContent
from .decoder import Decoder
from .encoder import Encoder


type ModelDecoder = type[Decoder[ModelContent, Any]]
type ModelEncoder = type[Encoder[ModelContent, Any]]

type TextureData = DefaultTexture | CubemapTexture

type TextureDecoder = type[Decoder[TextureContent[TextureData], Any]]
type TextureEncoder = type[Encoder[TextureContent[TextureData], Any]]

type CubemapDecoder = type[Decoder[TextureContent[CubemapTexture], Any]]
type CubemapEncoder = type[Encoder[TextureContent[CubemapTexture], Any]]

type ImageDecoder = type[Decoder[ImageContent, Any]]
type ImageEncoder = type[Encoder[ImageContent, Any]]

type TexarrDecoder = type[Decoder[TexarrContent, Any]]
type TexarrEncoder = type[Encoder[TexarrContent, Any]]

type DocumentDecoder = type[Decoder[DocumentContent, Any]]
type DocumentEncoder = type[Encoder[DocumentContent, Any]]

type RegionDecoder = type[Decoder[RegionContent, Any]]
type RegionEncoder = type[Encoder[RegionContent, Any]]
