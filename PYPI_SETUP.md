# PyPI Publishing Setup

## Option 1: Trusted Publishing (Recommended)

### Steps to Configure Trusted Publishing on PyPI:

1. **Go to PyPI Project Settings:**
   - Visit https://pypi.org/manage/project/nexus-fs-python/settings/publishing/
   - Or navigate: PyPI → Your Account → Manage → nexus-fs-python → Publishing

2. **Add Trusted Publisher:**
   - Click "Add a new trusted publisher"
   - Select "GitHub Actions" as publisher type
   - Fill in:
     - **Owner:** `nexi-lab`
     - **Repository:** `nexus-python`
     - **Workflow filename:** `.github/workflows/release.yml`
     - **Environment:** (leave empty, or create a `pypi` environment in GitHub for extra security)
   - Click "Add"

3. **Update Workflow (if using environment):**
   - If you created a `pypi` environment in GitHub, update the workflow to use it:
     ```yaml
     jobs:
       build-and-publish:
         runs-on: ubuntu-latest
         environment: pypi  # Add this line
     ```

4. **Re-run the workflow:**
   - The workflow will now use OIDC authentication automatically
   - No API token needed!

## Option 2: Use API Token (Fallback)

If you prefer to use an API token instead:

1. **Create PyPI API Token:**
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Name: `nexus-python-release`
   - Scope: "Entire account" or project-specific
   - Copy the token (starts with `pypi-`)

2. **Add to GitHub Secrets:**
   - Go to: https://github.com/nexi-lab/nexus-python/settings/secrets/actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Your token (e.g., `pypi-AgEIcHJ...`)
   - Click "Add secret"

3. **Update Workflow:**
   - The workflow already has `password: ${{ secrets.PYPI_API_TOKEN }}`
   - But we need to explicitly disable trusted publishing:
   ```yaml
   - name: Publish to PyPI
     uses: pypa/gh-action-pypi-publish@release/v1
     with:
       password: ${{ secrets.PYPI_API_TOKEN }}
       # Explicitly disable trusted publishing
       trusted-publisher: false
   ```

## Current Workflow Configuration

The workflow is currently configured to:
- Use trusted publishing (OIDC) if available
- Fall back to `PYPI_API_TOKEN` if provided

The error indicates trusted publishing is not configured, so you need to either:
1. Set up trusted publishing on PyPI (Option 1 - recommended)
2. Or ensure `PYPI_API_TOKEN` secret exists and modify workflow to explicitly use it

