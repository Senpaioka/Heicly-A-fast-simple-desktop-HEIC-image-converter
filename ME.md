# Developer & Release Guide for Heicly

This document serves as a reference guide for committing changes, testing locally, and releasing new versions of **Heicly**.

---

## 1. Local Development Workflow

Before committing changes, make sure your environment is up to date and all tests pass.

### Install / Sync Dependencies
```bash
uv sync
```

### Run Tests
Always run the test suite before committing to ensure no regressions:
```bash
uv run pytest
```

### Test Local Build (Optional)
To verify that PyInstaller packages the `.exe` properly on your machine:
```bash
uv run python build_installer.py
```
*The compiled binary will be at `dist/Heicly.exe`.*

---

## 2. Standard Commit Workflow

When making normal development updates (fixes, features, docs):

```bash
# 1. Stage changes
git add .

# 2. Commit with descriptive message
git commit -m "feat: description of your changes"

# 3. Push to GitHub
git push origin main
```

---

## 3. How to Publish a New Release

To release a new version (e.g., `v2.0.5`) with automatically compiled `Heicly.exe` for end users:

### Step 1: Update Version in `pyproject.toml`
Open `pyproject.toml` and update the version field:
```toml
[project]
name = "heicly"
version = "2.0.5"
```

### Step 2: Commit, Tag, and Push
Run the following commands in your terminal:

```bash
# 1. Stage modified files
git add .

# 2. Commit version update
git commit -m "release: version 2.0.5"

# 3. Create a git version tag
git tag v2.0.5

# 4. Push commit AND tag to GitHub
git push origin main --tags
```

---

## 4. What Happens Automatically on GitHub

Once you push a tag (e.g. `v2.0.5`) or push to `main`:

1. **GitHub Actions** triggers the `Build & Release Heicly` workflow automatically.
2. It sets up Python, installs dependencies, and runs `pytest`.
3. It compiles `Heicly.exe` on a `windows-latest` runner.
4. It creates a GitHub Release named **Heicly Release v2.0.5**.
5. It attaches `Heicly.exe` and `Heicly-Windows-x64.zip` to the release page for end-user download.

---

## 5. One-Time Setup Check on GitHub

Ensure your GitHub repository permissions allow GitHub Actions to create releases:

1. Go to your repository on **GitHub.com**.
2. Click **Settings** -> **Actions** -> **General**.
3. Under **Workflow permissions**, select **Read and write permissions**.
4. Click **Save**.
