# Contributing

On large PRs open an issue first. A quick discussion upfront avoids wasted effort on both sides.

**Target branch:** `dev` or a dedicated feature branch.

## 🚫 Out of scope

**The following will not be accepted, regardless of implementation quality:**

- **Graphical user interfaces.** This project is a core library. Any GUI belongs to a separate tool that depends on this package, not within the package itself. If you need one, fork the project or build your own tool on top of it.

- **Reverse conversion back to game formats.** The project is intentionally unidirectional. This is an explicit design choice, not a missing feature.

---

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
