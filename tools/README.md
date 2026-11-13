# Development Tools

A command-line toolkit for developing and maintaining `scfile`.

## Usage

```bash
uv run -m tools --help
uv run -m tools audit --help
uv run -m tools info --help
uv run -m tools profile --help
uv run -m tools mapcache --help
```

## Audit

Parses game assets to detect errors in supported decoders.

```bash
uv run -m tools audit "C:/EXBO/runtime/stalcraft/modassets/assets"
uv run -m tools audit "C:/assets" -F mcsb -F ol
uv run -m tools audit -R arms
```

Persistent settings can be stored in `configs/audit/config.toml`.
You can copy `configs/audit/config.example.toml` as a starting point.

```toml
path = "C:/EXBO/runtime/stalcraft/modassets/assets"
formats = ["mcsb", "ol"]
relations = ["arms"]
workers = 4
animation = true
mdat_extended = false
stats = true
exclude = ["path/to/file.mcsb"]
```

Command-line arguments override the config.
Without command-line selectors, configured formats and relations are checked.
`animation` controls model skeleton and clip parsing for standalone files.
`mdat_extended` enables full MDAT chunk records and object parsing.
Command-line format and relation selectors replace the configured selection.
Found errors and warnings are written to separate JSONL reports.
With statistics enabled, CSV files are written.
Report files are replaced on each run.
Animation relations are read from generated metadata snapshots in `assets/audit`.

## Info

Shows a compact summary of one decoded file.

```bash
uv run -m tools info "C:/assets/model.mcsb"
uv run -m tools info "C:/assets/model" -F mcsb
```

Use `-F`/`--format` when source has no suffix or its format must be overridden.
Models are decoded with skeletons and animations.
On failure, the command provides parser diagnostics.

## Profile

Profiles decoding or conversion of one source file.

```bash
uv run -m tools profile
uv run -m tools profile -T glb
uv run -m tools profile -T full
uv run -m tools profile "C:/assets/model.mcsb" -T obj -N 10
```

Without arguments, the reference model in `assets/profile` is decoded.
Without `-T`/`--target`, only decoding is measured.
Use `-T full` to profile conversion to every output format supported by the source.
Each operation writes a separate `.prof` file to `reports/profile`.

Timing runs are measured without `cProfile`.
Profile data is collected in a separate run.

## Map Cache

Reads MDAT region files. Set `--mdat-version` to choose the format version.
Without it, the tool uses the newest supported version.

```bash
uv run -m tools mapcache --help
uv run -m tools mapcache region "C:/assets/reg.0.0.mdat"
uv run -m tools mapcache chunk "C:/assets/reg.0.0.mdat" --index 0
uv run -m tools mapcache census "C:/assets/map_cache" -o reports/mapcache
uv run -m tools mapcache find "C:/assets/map_cache" --block-id 123
```

Commands: `region`, `chunk`, `block`, `records`, `objects`, `dump`, `census`,
`compare`, `map`, and `find`. Commands that support JSON output accept
`--json`.

## Mappings

Builds the local Mapping Editor for STALCRAFT and Minecraft Java 1.12.2.

```bash
uv run -m tools mappings
uv run -m tools mappings --run
uv run -m tools mappings --force
uv run -m tools mappings --force --run
```

The configured source paths can be overridden for one run with
`--stalcraft-texarr`, `--minecraft-jar`, and `--minecraft-resourcepack`.

Copy `configs/mappings/config.example.toml` to `configs/mappings/config.toml`
and set the paths to `blockMap.texarr` and the Minecraft 1.12.2 client JAR.
Relative paths are resolved from the repository root.

`--force` rebuilds both indexes. `--run` opens the editor after building.
