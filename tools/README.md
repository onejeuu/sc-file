# Development Tools

Commands for validating and profiling `scfile` during development.

## Usage

```bash
uv run -m tools --help
uv run -m tools audit --help
uv run -m tools info --help
uv run -m tools profile --help
```

## Audit

Decodes game assets to verify supported formats against real data.

```bash
uv run -m tools audit "C:/EXBO/runtime/stalcraft/modassets/assets"
uv run -m tools audit "C:/assets" -F mcsb -F ol
```

Persistent settings can be stored in `configs/audit.toml`. Copy `configs/audit.example.toml` as a starting point.

```toml
path = "C:/EXBO/runtime/stalcraft/modassets/assets"
formats = ["mcsb", "ol"]
workers = 4
animation = true
reports = "reports/audit"
stats = true
exclude = ["path/to/file.mcsb"]
```

Command-line arguments override the config. When `formats` is omitted, every registered decoder is checked. Errors are written to `errors.jsonl`; optional statistics are written to CSV files. Known report files are replaced on each run.

## Info

Shows a compact summary of one decoded file.

```bash
uv run -m tools info "C:/assets/model.mcsb"
```

Models are decoded with skeletons and animations. If decoding fails, the command shows the stream offset and the corresponding parser method, source statement, and module location.

## Profile

Profiles decoding or conversion of one source file.

```bash
uv run -m tools profile
uv run -m tools profile -T glb
uv run -m tools profile -T full
uv run -m tools profile "C:/assets/model.mcsb" -T obj -N 10
```

Without arguments, the reference model in `assets/profile` is decoded. Without `--target`, only decoding is measured. Each operation writes a separate `.prof` file to `reports/profile`.

Timing runs are measured without `cProfile`; profile data is collected in a separate run.
