---
name: go-init-project-embedded
description: Initializing a repository for an embedded TinyGo project with custom toolchain management, Makefile, build, lint, and test setup. ONLY callable manually by explicit user request.
user-invocable: true
disable-auto-invocation: true
---

# TinyGo Embedded Project Initialization

This skill initializes a clean, production-ready repository for an embedded TinyGo project with local toolchain management based on the architecture pattern used in `/home/ksharlaimov/dev/helvionics/eiger`.

> **Note:** This skill is configured for **manual invocation only**. Do not auto-trigger this skill unless explicitly requested by the user.

---

## Packaged Templates & Resources

Project assets are pre-packaged in the [resources/](resources/) directory:

- [resources/Makefile](resources/Makefile) — TinyGo compilation, lint, test, and toolchain fetching targets
- [resources/.gitignore](resources/.gitignore) — Ignore rules for `build/`, `toolchain/`, and agent metadata
- [resources/src/main.go](resources/src/main.go) — Entrypoint standard loop template
- [resources/src/main_test.go](resources/src/main_test.go) — Test file template

---

## Initialization Workflow

### 1. Initialize Go Module

If `go.mod` does not exist in target repository:
```bash
go mod init <module-path>
```

### 2. Copy Template Files

Copy packaged template files from `resources/` into target repository root:

1. Copy `.gitignore`:
   - Source: [resources/.gitignore](resources/.gitignore)
   - Target: `.gitignore`

2. Copy `Makefile`:
   - Source: [resources/Makefile](resources/Makefile)
   - Target: `Makefile`

3. Copy source files into `src/`:
   - Source: [resources/src/main.go](resources/src/main.go) -> Target: `src/main.go`
   - Source: [resources/src/main_test.go](resources/src/main_test.go) -> Target: `src/main_test.go`

### 3. Install Toolchain & Verify Build Setup

Run toolchain download:
```bash
make install-toolchain
```

Execute initial verification suite:
```bash
make test
make lint
make build
```
