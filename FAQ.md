# Frequently Asked Questions (FAQ)

## Q: **How to encode files back into game formats?**

**Answer:** Encoding back is not supported. If you are interested in game files replacement, you can create your own fork. Such functionality only incites TOS violations and is of no practical benefit.

## Q: **After game update %filename% no longer decoded!**

**Answer:** Maybe file structure has changed, just wait for program update. In case of large changes it may take some time.

## Q: **What programs can I use to view dds textures and their thumbnails?**

**Answer:** Any programs with full support for all formats.

For Windows I can recommend [WTV](https://www.moddb.com/downloads/windows-texture-viewer-v089b) or [XnView](https://www.xnview.com), but do not vouch for its safety and perfect compatibility.

## Q: **Is it possible to convert dds textures to png?**

**Answer:** Yes, but not planned to add native support due code simplicity.

If necessary, just convert via [ImageMagick](https://imagemagick.org). \
Command example: `magick mogrify -format png *.dds`

## Q: **Why model have weird/cursed/black textures?**

**Answer:** Some models _(mostly new weapons)_ seem to have mixed up suffixes in filename. Try swapping `_diff` and `_spek` textures.

## Q: **Is it possible to get game map as model?**

**Answer:** Theoretically yes, but currently not supported.

If anyone wants to implement map cache decoder, welcome to [Pull Requests](https://github.com/onejeuu/sc-file/pulls).

## Q: **How to open other game file types? (xeon, t, mcws, ...)**

**Answer:** Unfortunately, these files encrypted using AES. They cant be decrypted without key.

If anyone has information about AES key for assets, it would be nice to know details in [dm](https://onejeuu.t.me).

## Q: **How safe is it in terms of game ban to use this program?**

**Answer:** Use only at your own risk.

Some basic recommendations:

- **DO NOT** leave anything in game directory. Any changes can and will be tracked, there are tools for this.
- Copy required files to separate directory and **ONLY THEN** perform manipulations.
