from scfile.structures.textures import CubemapTexture, DefaultTexture, Texture

from .content import ImageContent, ModelContent, NbtContent, RegionContent, TexarrContent, TextureContent
from .decoder import FileDecoder
from .encoder import FileEncoder


ModelDecoder = type[FileDecoder[ModelContent]]
ModelEncoder = type[FileEncoder[ModelContent]]

TextureDecoder = type[FileDecoder[TextureContent[DefaultTexture]]]
TextureEncoder = type[FileEncoder[TextureContent[DefaultTexture]]]

CubemapDecoder = type[FileDecoder[TextureContent[CubemapTexture]]]
CubemapEncoder = type[FileEncoder[TextureContent[CubemapTexture]]]

AnyTextureDecoder = type[FileDecoder[TextureContent[Texture]]]
AnyTextureEncoder = type[FileEncoder[TextureContent[Texture]]]

ImageDecoder = type[FileDecoder[ImageContent]]
ImageEncoder = type[FileEncoder[ImageContent]]

TexarrDecoder = type[FileDecoder[TexarrContent]]
TexarrEncoder = type[FileEncoder[TexarrContent]]

NbtDecoder = type[FileDecoder[NbtContent]]
NbtEncoder = type[FileEncoder[NbtContent]]

RegionDecoder = type[FileDecoder[RegionContent]]
RegionEncoder = type[FileEncoder[RegionContent]]
