# Publishing to PyPI

## ✅ Build Complete

The package has been built successfully:
- `nexus_client-0.1.0-py3-none-any.whl` (68KB)
- `nexus_client-0.1.0.tar.gz` (70KB)

Both packages passed `twine check` validation.

## Publishing Steps

### Option 1: Test on TestPyPI First (Recommended)

1. **Create a TestPyPI account** (if you don't have one):
   - Go to https://test.pypi.org/account/register/
   - Create an account and verify your email

2. **Upload to TestPyPI**:
   ```bash
   python3 -m twine upload --repository testpypi dist/*
   ```
   - Username: `__token__`
   - Password: Your TestPyPI API token (create at https://test.pypi.org/manage/account/token/)

3. **Test installation from TestPyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ nexus-client
   ```

### Option 2: Publish to Production PyPI

1. **Create a PyPI account** (if you don't have one):
   - Go to https://pypi.org/account/register/
   - Create an account and verify your email

2. **Create an API token**:
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token (scope: "Entire account" or project-specific)
   - Copy the token (starts with `pypi-`)

3. **Publish to PyPI**:
   ```bash
   python3 -m twine upload dist/*
   ```
   - Username: `__token__`
   - Password: Your PyPI API token (e.g., `pypi-AgEIcHJ...`)

   Or set environment variables:
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-your-api-token-here
   python3 -m twine upload dist/*
   ```

4. **Verify publication**:
   - Check https://pypi.org/project/nexus-client/
   - Test installation: `pip install nexus-client`

## Quick Publish Script

You can also use the provided script:
```bash
./publish_to_pypi.sh
```

## Important Notes

1. **Version Number**: Current version is `0.1.0`. To publish updates:
   - Update `version = "0.1.0"` in `pyproject.toml`
   - Rebuild: `python3 -m build`
   - Republish: `python3 -m twine upload dist/*`

2. **Package Name**: The package name is `nexus-client` (with hyphen), but imports use `nexus_client` (with underscore).

3. **License**: Fixed to use SPDX format (`license = "Apache-2.0"` instead of table format).

4. **After Publishing**:
   - Package will be available at: https://pypi.org/project/nexus-client/
   - Installation: `pip install nexus-client` or `pip install nexus-client[langgraph]`
   - It may take a few minutes for the package to be indexed and searchable

## Troubleshooting

- **"Package already exists"**: Version 0.1.0 is already published. Increment version in `pyproject.toml`.
- **Authentication errors**: Make sure you're using `__token__` as username and the full token (including `pypi-` prefix) as password.
- **Upload errors**: Check your internet connection and PyPI status.

