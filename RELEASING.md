# Releasing nexus-client to PyPI

## Automated Release via GitHub Actions

The repository includes a GitHub Actions workflow that automatically builds and publishes to PyPI when you push a version tag.

### Prerequisites

1. **PyPI API Token**: Create a PyPI API token at https://pypi.org/manage/account/token/
   - Go to your PyPI account settings
   - Create a new API token (scope: "Entire account" or project-specific)
   - Copy the token (starts with `pypi-`)

2. **Add Secret to GitHub**:
   - Go to your repository settings: Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token (e.g., `pypi-AgEIcHJ...`)
   - Click "Add secret"

### Release Process

#### Option 1: Release via Git Tag (Recommended)

1. **Update version in `pyproject.toml`**:
   ```toml
   version = "0.1.0"  # Update to new version
   ```

2. **Update `CHANGELOG.md`**:
   ```markdown
   ## [0.1.0] - 2025-01-XX
   
   ### Added
   - New features...
   ```

3. **Commit and push changes**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 0.1.0"
   git push origin main
   ```

4. **Create and push a version tag**:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

5. **GitHub Actions will automatically**:
   - Build the package (wheel + source distribution)
   - Validate the package
   - Publish to PyPI
   - Create a GitHub Release with release notes

#### Option 2: Manual Release via Workflow Dispatch

1. Go to the Actions tab in GitHub
2. Select "Release" workflow
3. Click "Run workflow"
4. Enter the version number (e.g., `0.1.0`)
5. Click "Run workflow"

### Version Tag Format

Tags must follow the format: `v<version>`
- ✅ Valid: `v0.1.0`, `v1.2.3`, `v0.1.0-alpha.1`
- ❌ Invalid: `0.1.0`, `version-0.1.0`

The tag version must match the version in `pyproject.toml` (without the `v` prefix).

### Release Notes

Release notes are automatically extracted from `CHANGELOG.md`:
- Look for a section matching `## [<version>]`
- If found, that section is used as the release notes
- If not found, a default message is used

### Verification

After release, verify:
1. Package is on PyPI: https://pypi.org/project/nexus-client/
2. Installation works: `pip install nexus-client`
3. GitHub Release created: Check the Releases tab

### Troubleshooting

- **"Tag doesn't match version"**: Ensure the tag (e.g., `v0.1.0`) matches `version = "0.1.0"` in `pyproject.toml`
- **"PYPI_API_TOKEN not found"**: Add the secret in repository settings
- **"Package already exists"**: Version already published. Increment version and try again.

### Manual Release (Alternative)

If you need to release manually:

```bash
# Build
python -m build

# Check
python -m twine check dist/*

# Upload to PyPI
python -m twine upload dist/*
# Username: __token__
# Password: pypi-your-api-token
```
