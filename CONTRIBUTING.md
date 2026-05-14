# Contributing

On large PRs open an issue first. A quick discussion upfront avoids wasted effort on both sides.

**Target branch:** `develop` (for general improvements) or a dedicated `feat/` branch.

## 🚫 Out of scope

**Reverse conversion back to game formats will not be accepted, regardless of implementation quality**. The project is intentionally unidirectional. This is an explicit design choice, not a missing feature.

## 📋 Code standards

Code is read far more often than it is written. Each component should have a single, clear responsibility and perform it well. Simplicity is preferred over cleverness. Performance is a default consideration.

```bash
$ python
>>> import this
```

- Understand your code
- Formatted with `ruff`
- Type annotations on all function parameters
- No debug leftovers, jokes, or Easter eggs
- Autotests are optional but welcome
