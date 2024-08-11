# Frequently Asked Questions (FAQ)

1. **How to encode files back into game formats?**

   Encoding back is not supported. If you are interested in game files replacement, you can create your own fork.

   Such functionality only incites TOS violations and is of no practical benefit.

1. **File is no longer decoded after game update.**

   Maybe file structure has changed, just wait for program update. In case of large changes it may take some time.

1. **Is support for model skeletons and animations present?**

   Currently, only skeleton, only for MilkShape3D supported.

   Pull Requests is welcome. At this point I don't know enough about how it works. An approximate structure is described in [this template](https://github.com/onejeuu/sc-file/blob/master/templates/MCSA.bt#L215).

1. **Why model have weird/cursed/black textures?**

   Some models _(mostly new weapons)_ seem to have mixed up suffixes in filename. Try swapping diff and spek textures in texture shading.

1. **What programs can I use to view dds textures and their thumbnails?**

   Any programs with full support for all formats.

   For Windows I can recommend [WTV](https://www.moddb.com/downloads/windows-texture-viewer-v089b), but I do not vouch for its safety and perfect compatibility.

   Also [XnView](https://www.xnview.com/), but it has problems with rendering of normal textures thumbnails.

1. **Is it possible to convert dds textures to png?**

   Yes, but not planned to add native support due code simplicity.

   If necessary, just convert original dds to png via [ImageMagick](https://imagemagick.org). \
   Command example: `magick mogrify -format png *.dds`

1. **Is it possible to get game map as model?**

   Theoretically yes, but currently not supported.

   If anyone wants to implement map cache decoder, welcome to PR.

1. **How to open other game file types? (xeon, t, mcws, ...)**

   Unfortunately, these files encrypted using AES. It's impossible to read them without knowing key.

   If anyone has information about decrypting them, it would be nice to know details in DM.

1. **How safe is it in terms of game ban to use this program?**

   Use only at your own risk.

   Some basic recommendations:

   - **DO NOT** leave anything in game directory. Any changes can and will be tracked, there are tools for this.
   - Copy required files to separate directory and **ONLY THEN** perform manipulations.
