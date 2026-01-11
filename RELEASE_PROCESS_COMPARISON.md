# Release Process Comparison: nexus vs nexus-python

This document compares the release workflows between the main `nexus` repository and `nexus-python` repository.

## Summary

Both repositories follow **the same release pattern**: update version → commit → create tag → push tag → automated release. The workflows are nearly identical, with differences only in build tooling (Rust vs pure Python).

## Release Process Overview

### Both Repositories Follow This Pattern:

1. **Manual Steps:**
   - Update version in `pyproject.toml`
   - Update `CHANGELOG.md` with release notes
   - Commit changes and push to main
   - Create and push git tag (e.g., `v0.1.3`)

2. **Automated Steps (GitHub Actions):**
   - Build package distributions
   - Publish to PyPI
   - Create GitHub Release with changelog
   - Handle pre-releases (alpha, beta, rc)

## Detailed Comparison

| Feature | nexus | nexus-python | Notes |
|---------|-------|--------------|-------|
| **Trigger** | Tag push (`v*`) | Tag push (`v*`) + workflow_dispatch | nexus-python has extra manual trigger option |
| **Build System** | maturin (Rust + Python) | standard Python build | Different due to Rust extensions in nexus |
| **Build Jobs** | 3 jobs (wheels, sdist, publish) | 1 job (build-and-publish) | nexus needs multiple platforms for Rust |
| **Platforms** | Linux, macOS (x86_64, aarch64), Windows | Linux only (pure Python, platform-independent) | Rust requires platform-specific builds |
| **PyPI Publishing** | `pypa/gh-action-pypi-publish` | `pypa/gh-action-pypi-publish` | Same action |
| **GitHub Release** | `softprops/action-gh-release@v2` | `softprops/action-gh-release@v2` | Same action |
| **Changelog Extraction** | sed/awk parsing | sed/awk parsing | Same logic |
| **Version Verification** | None | Tag vs pyproject.toml match check | nexus-python has extra safety check |
| **Pre-release Detection** | `contains(github.ref, 'alpha/beta/rc')` | `contains(github.ref, 'alpha/beta/rc')` | Same logic |
| **Secrets Required** | `PYPI_API_TOKEN` | `PYPI_API_TOKEN` | Same requirement |
| **Permissions** | `contents: write`, `id-token: write` | `contents: write`, `id-token: write` | Same permissions |

## Workflow Files

### nexus: [`.github/workflows/release.yml`](https://github.com/nexi-lab/nexus/.github/workflows/release.yml)

```yaml
on:
  push:
    tags: ["v*"]

jobs:
  build-wheels:
    strategy:
      matrix:
        platform: [ubuntu-latest, macos-13, macos-14, windows-latest]
    # Uses maturin to build Rust-based wheels

  build-sdist:
    # Uses maturin to build source distribution

  publish:
    needs: [build-wheels, build-sdist]
    # Publishes to PyPI and creates GitHub release
```

**Build time:** ~10-15 minutes (multiple platforms, Rust compilation)

### nexus-python: [`.github/workflows/release.yml`](https://github.com/nexi-lab/nexus-python/.github/workflows/release.yml)

```yaml
on:
  push:
    tags: ["v*"]
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release (e.g., 0.1.0)'
        required: true

jobs:
  build-and-publish:
    # Single job: build, verify, publish, release
```

**Build time:** ~2-3 minutes (single platform, pure Python)

## Key Files

| File | nexus | nexus-python | Purpose |
|------|-------|--------------|---------|
| **Workflow** | `.github/workflows/release.yml` | `.github/workflows/release.yml` | Automated release pipeline |
| **Documentation** | `RELEASING.md` | `RELEASING.md` | Release process guide |
| **Changelog** | `CHANGELOG.md` | `CHANGELOG.md` | Release notes |
| **Version** | `pyproject.toml` (line 7) | `pyproject.toml` (line 7) | Version definition |
| **Build Config** | `pyproject.toml` ([tool.maturin]) | `pyproject.toml` ([build-system]) | Build system config |

## Release Commands

Both repositories use identical commands:

```bash
# Step 1: Update version and changelog
vim pyproject.toml  # Bump version
vim CHANGELOG.md    # Add release notes

# Step 2: Commit and push
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to X.Y.Z"
git push origin main

# Step 3: Create and push tag (triggers automated release)
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

**Important:** The tag push triggers the entire automated workflow. No manual PyPI upload is needed.

## nexus-python Bonus Features

### 1. Workflow Dispatch (Manual Release Trigger)

nexus-python allows manual release triggering without creating a tag:

```yaml
workflow_dispatch:
  inputs:
    version:
      description: 'Version to release (e.g., 0.1.0)'
      required: true
```

**Usage:**
1. Go to GitHub Actions → Release workflow
2. Click "Run workflow"
3. Enter version number
4. Click "Run workflow" button

This is useful for:
- Testing the release workflow
- Re-running a failed release
- Creating a release without pushing tags

### 2. Version Verification

nexus-python includes a safety check:

```bash
# Extracts version from pyproject.toml
PYPROJECT_VERSION=$(grep -E '^version\s*=' pyproject.toml | sed ...)

# Fails if tag doesn't match
if [ "v$PYPROJECT_VERSION" != "$GITHUB_REF_NAME" ]; then
  echo "Error: Tag $GITHUB_REF_NAME does not match pyproject.toml version"
  exit 1
fi
```

This prevents accidentally releasing the wrong version.

## Pre-Release Support

Both repositories support pre-releases with the same tag format:

- `v0.1.0-alpha.1` - Alpha release
- `v0.1.0-beta.1` - Beta release
- `v0.1.0-rc.1` - Release candidate

The workflow automatically marks these as pre-releases on GitHub.

## PyPI Package Names

- **nexus**: Published as `nexus-ai-fs`
- **nexus-python**: Published as `nexus-fs-python`

## Recommendations

### For nexus-python: ✅ No Changes Needed

The current setup is excellent for a pure Python package:
- ✅ Automated release on tag push
- ✅ Bonus manual trigger option
- ✅ Version verification safety check
- ✅ Changelog extraction
- ✅ Pre-release support
- ✅ Clear documentation

### Maintenance Checklist

When releasing a new version:

1. **Update CHANGELOG.md** - Add entry for new version (MUST DO)
2. **Update pyproject.toml** - Bump version number
3. **Test locally** - Ensure tests pass
4. **Create release PR** - For review (optional but recommended)
5. **Merge to main** - After approval
6. **Create tag** - `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
7. **Push tag** - `git push origin vX.Y.Z` (triggers automation)
8. **Verify release** - Check PyPI and GitHub releases

## Testing the Workflow

### Dry Run (Without Publishing)

To test the workflow without publishing:

1. Create a feature branch
2. Update version to something like `0.1.3-test.1`
3. Push tag `v0.1.3-test.1`
4. Workflow will run but can be cancelled before publish step

### Full Test (With Publishing)

Use a pre-release version:

```bash
# Update to pre-release version
vim pyproject.toml  # version = "0.1.4-alpha.1"
vim CHANGELOG.md    # Add [0.1.4-alpha.1] section

git add pyproject.toml CHANGELOG.md
git commit -m "Release v0.1.4-alpha.1 (test)"
git push origin main

git tag -a v0.1.4-alpha.1 -m "Release v0.1.4-alpha.1"
git push origin v0.1.4-alpha.1
```

This creates a real release marked as "pre-release" on GitHub.

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Tag doesn't match version" | Ensure tag `vX.Y.Z` matches `version = "X.Y.Z"` in pyproject.toml |
| "PYPI_API_TOKEN not found" | Add secret in repository settings → Secrets → Actions |
| "Package already exists" | Version already published; increment version |
| "Workflow not triggered" | Ensure tag follows `v*` format (e.g., `v0.1.3`, not `0.1.3`) |
| "Changelog extraction failed" | Ensure CHANGELOG.md has `## [X.Y.Z]` section |

### Manual Release (Emergency Fallback)

If GitHub Actions fails:

```bash
cd /path/to/nexus-python

# Build
python -m build

# Check
python -m twine check dist/*

# Upload to PyPI
python -m twine upload dist/*
# Username: __token__
# Password: pypi-your-api-token

# Create GitHub release manually
gh release create vX.Y.Z --title "Release vX.Y.Z" --notes "..." dist/*
```

## Conclusion

Both repositories have mature, automated release workflows. The nexus-python workflow is **simpler and faster** (pure Python), while nexus is **more complex** (multi-platform Rust builds). Both achieve the same goal: automated, reliable releases triggered by git tags.

**Key Takeaway:** The release processes are already aligned and follow industry best practices. No changes needed to nexus-python workflow.
