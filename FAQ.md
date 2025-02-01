# Frequently Asked Questions (FAQ)

## General

### Q: **How to encode files back into game formats?**

**Answer:** Reverse encoding is intentionally unsupported. While this functionality is technically possible, releasing it publicly could lead to unwanted consequences.

1. **Risk of format changes**: If an easy way to modify game files becomes available, it might encourage game developers to complicate or even encrypt game assets.

2. **Potential cheating issues**: An open reverse encoding feature could significantly simplify creating hacks. This might attract negative attention from game developers and lead to the tool being seen as a cheat making utility, which I aim to avoid.

My goal is to support research and creativity, not spark a tech arms race or create tools that could harm the game community. If you need help with small tasks in game content creation, you can [contact me directly](https://onejeuu.t.me).

### Q: **After game update %any_filename% no longer decodes!**

**Answer:** Format structure may have been updated. Please wait for a program update. In case of large changes, it might take some time to adapt.

### Q: **How safe is it in terms of game ban to use this program?**

**Answer:** Use at your own risk.

Some basic recommendations:

- **DO NOT** leave anything in the game assets directory. Any changes can and will be tracked, as there are tools for this.
- Copy the required files to a separate directory and **ONLY THEN** perform manipulations.

## Textures and Models

### Q: **What programs can I use to view DDS textures and their thumbnails?**

**Answer:** Any programs with full support for all DDS formats.

On Windows, recommended programs are:

- [XnView](https://www.xnview.com)
- [WTV](https://www.moddb.com/downloads/windows-texture-viewer-v089b)

Note: I cannot vouch for their safety or perfect compatibility.

### Q: **Is it possible to convert DDS textures to PNG?**

**Answer:** Yes, but native support is not planned for the sake of code simplicity.

If needed, convert DDS to PNG using [ImageMagick](https://imagemagick.org). \
Command example:

```cmd
magick mogrify -format png *.dds
```

### Q: **Why model have weird/cursed/black textures?**

**Answer:**

- Make sure texture node alpha mode is set to `Channel Packed` ([screenshot](https://i.ibb.co/mCsHk6R4/alphapvp.png)).

- Some models, especially newer weapons, seem to have mixed-up suffixes in filenames. Make sure that the `_diff` texture is actually a Diffuse Map and the `_spek` texture is a Specular Map.

## Other Features

### Q: **Is it possible to get the game map as a model?**

**Answer:** Theoretically, yes, but this is currently not supported.

If anyone wants to implement a map cache decoder, feel free to contribute to [Pull Requests](https://github.com/onejeuu/sc-file/pulls).

### Q: **How to open other game file types? (xeon, t, mcws, ...)**

**Answer:** These files are encrypted using [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) and cannot be decrypted without the key.

If anyone has information about key for assets, it would be nice to know details in [DM](https://onejeuu.t.me).
