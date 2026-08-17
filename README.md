# agent-lens

macOS CLI and daemon for code diagnostics and linting. Pass it files, get LSP diagnostics and linter output back. Use it from a shell, a git hook, CI, or an agent loop.

If you need a full editor experience for agents, see [aifed](https://github.com/ImitationGameLabs/aifed).

**Requirements:** macOS 15, Swift 6.

## Install

```sh
swift build -c release
cp .build/release/alensd /usr/local/bin/
cp .build/release/alens  /usr/local/bin/
```

## Usage

Start one daemon per project root:

```sh
alens start
# or: alens start --dir /path/to/project
```

The daemon exits after 2 hours idle. Override with `--idle` (`30s`, `5m`, `2h`, `1d`). Logs go to the system log unless you pass `--log-file`.

Then pass files. Directories are rejected; the CLI does not expand them.

```sh
alens diagnose Sources/App/main.swift
alens lint $(git diff --name-only -- '*.swift')
alens check path/to/file.ts
alens status
alens stop
```

Human-readable output by default. Add `--json` for the raw response. `diagnose` and `check` accept `--timeout` (default 5 seconds). Every command accepts `--dir` to talk to a daemon rooted somewhere other than the current directory.

## Commands

| Command | What it does |
|---|---|
| `start` | Launch the daemon for this root |
| `stop` | Shut the daemon down |
| `status` | Server readiness and uptime |
| `diagnose` | LSP diagnostics per file |
| `lint` | Linter stdout per file |
| `check` | Diagnose and lint in one round-trip |

## Languages

Files are routed by extension. Language servers start on first use. Servers and linters must be on `PATH`.

| Language | Extensions | Server | Linter |
|---|---|---|---|
| Swift | `.swift` | `sourcekit-lsp` | `swiftlint` |
| TypeScript / JavaScript | `.ts` `.tsx` `.js` `.jsx` `.mjs` `.cjs` | `typescript-language-server` | `eslint` |
| Python | `.py` `.pyi` | `pyright-langserver` | `ruff` |
| Go | `.go` | `gopls` | `golangci-lint` |
| Rust | `.rs` | `rust-analyzer` | none |

Unrecognized extensions come back as `unsupported` for diagnose and as empty lint output.

## Configuration

Optional `.alens.json` at the project root. Language servers and linters share this file.

### Language servers

Without an `lspServers` key, the daemon uses the built-in defaults above.

If `lspServers` is present, only those servers start. An empty object starts none.

```json
{
  "lspServers": {
    "swift": {
      "command": "sourcekit-lsp",
      "args": [],
      "env": { "SOURCEKIT_LOGGING": "0" }
    }
  }
}
```

### Linters

Override defaults with the `linters` key.

```json
{
  "linters": {
    "swift": {
      "command": "swiftlint",
      "args": ["lint", "--reporter", "json", "$FILE"],
      "fileField": "file"
    }
  }
}
```

`$FILE` expands to every path in the batch (one process per language). `fileField` is the dotted key used to split results back per file. `resultsKey` names a nested results array when the linter wraps output (for example `"Issues"` for golangci-lint).

## How it works

`alensd` is the stateful process. It holds warm LSP sessions, runs linters, and watches the project so servers stay current. `alens` is a stateless client: it sends a command over a Unix socket at `/tmp/alensd-<hash>.sock` (hash of the project root) and prints the result. Multiple roots can run at once.

License: Apache 2.0.
