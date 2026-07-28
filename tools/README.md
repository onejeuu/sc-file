# Development Tools

A command-line toolkit for developing and maintaining `scfile`.

## Usage

```bash
uv run -m tools --help
uv run -m tools audit --help
uv run -m tools info --help
uv run -m tools profile --help
```

## Audit

Parses game assets to detect errors in supported decoders.

```bash
uv run -m tools audit "C:/EXBO/runtime/stalcraft/modassets/assets"
uv run -m tools audit "C:/assets" -F mcsb -F ol
```

Persistent settings can be stored in `configs/audit.toml`.
You can copy `configs/audit.example.toml` as a starting point.

```toml
path = "C:/EXBO/runtime/stalcraft/modassets/assets"
formats = ["mcsb", "ol"]
workers = 4
animation = true
reports = "reports/audit"
stats = true
exclude = ["path/to/file.mcsb"]
```

Command-line arguments override the config.
When `formats` is omitted, every registered decoder is checked.
Full asset roots also validate arms, face, and body animation compatibility.
Found errors are written to `errors.jsonl`.
With statistics enabled, CSV files are written.
Report files are replaced on each run.

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
