# Integrate container-manager as Workspace Member

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fully integrate the `container-manager` module into the `uv` workspace so it is tracked by git, resolved by the root lock file, and consistently configured alongside the other three modules.

**Architecture:** Remove the nested `.git` inside `container-manager/` so the parent repo can track its files. Fix the one config gap (`pythonpath` missing from pytest options). Add it to the root workspace member list and regenerate the lock.

**Tech Stack:** Python 3.12+, uv workspace, hatchling, pytest

---

## What Was Found

Four issues require fixes. Nothing else in `container-manager` needs to change.

| # | Issue | Where |
|---|-------|--------|
| 1 | Nested `.git` inside `container-manager/` — parent git can't track the files | `container-manager/.git` |
| 2 | `container-manager` not listed in workspace members | root `pyproject.toml` line 2 |
| 3 | `pythonpath = ["src"]` missing from pytest options — test imports will fail | `container-manager/pyproject.toml` line 28-32 |
| 4 | Standalone `uv.lock` inside `container-manager/` is now obsolete | `container-manager/uv.lock` |

Everything else is already correct:
- `pyproject.toml` project config, build-system, tool settings all match workspace standards
- No external dependencies (consistent with all other modules)
- `container-manager/.gitignore` already covers the `uv.lock` so it won't be accidentally tracked
- The `[dependency-groups]` format (vs `[project.optional-dependencies]` in other modules) is valid; the workspace root already provides all dev tools

---

## Task 1: Remove the nested `.git` directory

**Files:**
- Delete: `container-manager/.git/` (entire directory)

**Context:**
When a directory inside a git repo contains its own `.git/`, git treats it as a "nested repository" and refuses to track its contents individually. That's why the parent repo shows `?? container-manager/` as a single untracked blob instead of listing all the files inside. Removing the nested `.git` lets the parent repo see and stage each file normally.

This will lose the 4-commit history that existed in `container-manager/.git`. The code itself is preserved — only the git history log is discarded. This is acceptable given the module is not yet published or used externally.

**Step 1: Verify the nested `.git` history (so you know what's being discarded)**

```bash
git -C container-manager log --oneline
```

Expected output (4 commits):
```
d3e77a1 :broom: Remove Python cache files
50489ae :construction: Update .gitignore to exclude Python cache files
94aeb5d :broom: Added gitignore
e27958a :sparkles: Init project
```

**Step 2: Remove the nested `.git`**

```bash
rm -rf container-manager/.git
```

Expected: no output, no error.

**Step 3: Verify parent git now sees the files**

```bash
git status --short
```

Expected: many `?? container-manager/...` lines listing individual files (not just `?? container-manager/`).

---

## Task 2: Fix pytest config — add `pythonpath = ["src"]`

**Files:**
- Modify: `container-manager/pyproject.toml` lines 27–32

**Context:**
Every other module (`logging`, `pipeline`, `package-manager`) has `pythonpath = ["src"]` in `[tool.pytest.ini_options]`. Without it, when pytest runs from `container-manager/`, Python's import system won't find `container_manager` package (which lives at `src/container_manager/`). Tests will fail with `ModuleNotFoundError`.

**Step 1: Open `container-manager/pyproject.toml` and locate the pytest section**

Current (lines 27–32):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers"
```

**Step 2: Add `pythonpath = ["src"]`**

Replace those lines with:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers"
```

**Step 3: No test to run yet** — we'll verify in Task 5 after the workspace is fully set up.

---

## Task 3: Add `container-manager` to workspace members

**Files:**
- Modify: `pyproject.toml` (root) line 2

**Context:**
The root `pyproject.toml` is the workspace definition file. Adding `"container-manager"` to its `members` list tells `uv` to include it in the workspace — meaning `uv sync` will install it, it appears in `uv.lock`, and `uv run` from anywhere in the workspace can import it.

**Step 1: Open root `pyproject.toml`**

Current:
```toml
[tool.uv.workspace]
members = ["logging", "pipeline", "package-manager"]
```

**Step 2: Add `container-manager`**

```toml
[tool.uv.workspace]
members = ["logging", "pipeline", "package-manager", "container-manager"]
```

---

## Task 4: Remove the standalone `container-manager/uv.lock`

**Files:**
- Delete: `container-manager/uv.lock`

**Context:**
When `container-manager` was a standalone project, it had its own `uv.lock` to track its resolved dependencies. In a workspace, the **root** `uv.lock` is the single source of truth for all member dependency resolution. The standalone lock is now obsolete and confusing. Note: `container-manager/.gitignore` already has `uv.lock` listed, so even if we left it, it wouldn't be tracked in git. But deleting it is cleaner.

**Step 1: Delete the file**

```bash
rm container-manager/uv.lock
```

Expected: no output, no error.

---

## Task 5: Regenerate the workspace lock and verify tests

**Files:**
- Regenerated: `uv.lock` (root — done automatically by `uv sync`)

**Context:**
`uv sync` reads the root `pyproject.toml`, discovers the updated members list, resolves all dependencies (including the new `container-manager` member), installs everything into the workspace `.venv`, and rewrites `uv.lock` to reflect the new manifest. After sync, we verify `container-manager` tests pass within the workspace context.

**Step 1: Run sync from the workspace root**

```bash
uv sync
```

Expected: uv processes 4 workspace members, installs `container-manager` into the shared `.venv`, updates `uv.lock`. Should complete without errors.

**Step 2: Verify `container-manager` appears in the lock manifest**

```bash
head -15 uv.lock
```

Expected — `container-manager` now listed in `[manifest]`:
```
[manifest]
members = [
    "container-manager",
    "dotfiles-package-manager",
    "rich-logging",
    "task-pipeline",
]
```

**Step 3: Run container-manager tests from workspace root**

```bash
uv run pytest container-manager/tests/ -v
```

Expected: all tests pass (green). No `ModuleNotFoundError`.

**Step 4: Run all workspace tests to confirm no regressions**

```bash
uv run pytest logging/tests/ pipeline/tests/ package-manager/tests/ container-manager/tests/ -v
```

Expected: all pass.

---

## Task 6: Commit everything to git

**Context:**
Now that the nested `.git` is gone, all `container-manager` files are individually visible to the parent git. Stage everything and commit.

**Step 1: Check what git sees**

```bash
git status --short
```

Expected: `container-manager/` files listed as untracked (`??`), plus modified `pyproject.toml` and `uv.lock`.

**Step 2: Stage all changes**

```bash
git add container-manager/ pyproject.toml uv.lock docs/
```

**Step 3: Verify staged files look right**

```bash
git diff --cached --stat
```

Expected: `container-manager/` source files, tests, docs, `pyproject.toml` (root), `uv.lock` (root).

**Step 4: Commit**

```bash
git commit -m "$(cat <<'EOF'
feat: integrate container-manager as uv workspace member

- Remove nested .git (container-manager was previously a standalone repo)
- Add container-manager to workspace members in root pyproject.toml
- Fix pytest pythonpath config so tests can import the package
- Remove standalone uv.lock (superseded by workspace root lock)
- Regenerate uv.lock to include container-manager in manifest

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

**Step 5: Verify commit**

```bash
git log --oneline -3
git status
```

Expected: clean working tree, new commit at top.
