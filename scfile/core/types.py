from scfile.structures.textures import CubemapTexture, DefaultTexture

from .content import ImageContent, ModelContent, NbtContent, RegionContent, TexarrContent, TextureContent
from .decoder import FileDecoder
from .encoder import FileEncoder


ModelDecoder = type[FileDecoder[ModelContent]]
ModelEncoder = type[FileEncoder[ModelContent]]

TextureData = DefaultTexture | CubemapTexture

TextureDecoder = type[FileDecoder[TextureContent[TextureData]]]
TextureEncoder = type[FileEncoder[TextureContent[TextureData]]]

CubemapDecoder = type[FileDecoder[TextureContent[CubemapTexture]]]
CubemapEncoder = type[FileEncoder[TextureContent[CubemapTexture]]]

AnyTextureDecoder = TextureDecoder
AnyTextureEncoder = TextureEncoder

ImageDecoder = type[FileDecoder[ImageContent]]
ImageEncoder = type[FileEncoder[ImageContent]]

TexarrDecoder = type[FileDecoder[TexarrContent]]
TexarrEncoder = type[FileEncoder[TexarrContent]]

NbtDecoder = type[FileDecoder[NbtContent]]
NbtEncoder = type[FileEncoder[NbtContent]]

RegionDecoder = type[FileDecoder[RegionContent]]
RegionEncoder = type[FileEncoder[RegionContent]]
