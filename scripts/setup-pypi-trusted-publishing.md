# PyPI Trusted Publishing Setup Guide

This guide walks you through setting up PyPI Trusted Publishing for secure, tokenless automated releases.

## Overview

Trusted Publishing uses OpenID Connect (OIDC) tokens instead of stored API tokens, providing:
- **Enhanced Security**: No long-lived secrets stored in GitHub
- **Automatic Tokens**: Short-lived (15-minute) tokens generated per release
- **Repository-Scoped**: Permissions limited to specific repositories
- **No Secret Management**: No need to manage PYPI_API_TOKEN secrets

## Prerequisites

1. **PyPI Account**: You must have a PyPI account with project ownership
2. **GitHub Repository**: The repository must be public or have GitHub Actions enabled
3. **Project on PyPI**: The package must already exist on PyPI (can be a placeholder)

## Step 1: Create PyPI Project (if not exists)

If your package doesn't exist on PyPI yet:

1. Go to [PyPI](https://pypi.org/)
2. Sign in to your account
3. Go to "Account Settings" → "Add project"
4. Enter project name: `harvard-library-mcp`
5. Click "Add project"

## Step 2: Configure Trusted Publisher

### Method 1: Using PyPI Web Interface

1. **Navigate to Project Settings**:
   - Go to your project on PyPI: https://pypi.org/project/harvard-library-mcp/
   - Click "Publishing" in the left sidebar
   - Click "Add a trusted publisher"

2. **Fill in the GitHub Actions Information**:
   ```
   Owner: kltang
   Repository name: harvard-library-mcp
   Workflow name: .github/workflows/release.yml
   Environment: (leave blank for default)
   ```

3. **Verify and Save**:
   - Review the configuration
   - Click "Add publisher"

### Method 2: Using PyPI API (Advanced)

```bash
# Get your PyPI API token from Account Settings
export PYPI_API_TOKEN="your-token-here"

# Create trusted publisher configuration
curl -X POST https://upload.pypi.org/legacy/ \
  -H "Authorization: Bearer $PYPI_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "publisher": {
      "name": "github",
      "owner": "kltang",
      "repository": "harvard-library-mcp",
      "workflow_filename": ".github/workflows/release.yml"
    }
  }'
```

## Step 3: Verify Configuration

### Check Trusted Publisher Status

1. Go to your PyPI project page
2. Click "Publishing"
3. Verify your trusted publisher appears in the list

### Test with a Dry Run

1. Go to your GitHub repository
2. Navigate to "Actions" tab
3. Select "Release to PyPI" workflow
4. Click "Run workflow"
5. Set:
   - **version**: `0.1.0-test` (or any test version)
   - **dry_run**: `true`
   - **create_github_release**: `false`

6. Verify the workflow runs successfully through the build and test steps

## Step 4: Configure Repository Permissions

Ensure your GitHub repository has the correct permissions:

1. Go to **Repository Settings** → **Actions** → **General**
2. Under "Workflow permissions", select:
   - **Read and write permissions**
   - **Allow GitHub Actions to create and approve pull requests**
   - **Allow GitHub Actions to run workflows from forked pull requests** (if needed)

3. Save the settings

## Step 5: Remove Legacy API Tokens (if any)

If you previously used PYPI_API_TOKEN:

1. Go to **Repository Settings** → **Secrets and variables** → **Actions**
2. Delete any existing `PYPI_API_TOKEN` secret
3. Verify no other PyPI-related secrets exist

## Workflow Configuration Details

The release workflow uses these key settings:

```yaml
permissions:
  contents: write
  id-token: write  # IMPORTANT: required for OIDC tokens

environment:
  name: pypi
  url: https://pypi.org/p/harvard-library-mcp
```

## Troubleshooting

### Common Issues

1. **"Workflow not found" error**:
   - Verify the workflow file path is exactly `.github/workflows/release.yml`
   - Ensure the file exists and is committed to the main branch

2. **"No OIDC token" error**:
   - Ensure `id-token: write` permission is set
   - Check that repository permissions allow workflow OIDC tokens

3. **"Publisher not found" error**:
   - Verify the trusted publisher configuration on PyPI
   - Check that owner and repository names match exactly

4. **"Environment not found" error**:
   - The workflow references a `pypi` environment that may not exist
   - You can create this environment in GitHub repository settings or remove the environment reference

### Debug Steps

1. **Check Workflow Logs**:
   - Look for OIDC token acquisition in the logs
   - Verify the PyPI publish step is reached

2. **Verify PyPI Configuration**:
   - Go to PyPI project → Publishing
   - Check that your trusted publisher is listed and active

3. **Test Token Generation**:
   ```bash
   # Add this debug step to your workflow to verify OIDC token
   - name: Debug OIDC token
     run: |
       echo "OIDC token audience: ${{ env.ACTIONS_ID_TOKEN_REQUEST_TOKEN }}"
       echo "OIDC token URL: ${{ env.ACTIONS_ID_TOKEN_REQUEST_URL }}"
   ```

## Security Considerations

### Best Practices

1. **Minimal Permissions**: Only grant necessary permissions
2. **Environment Protection**: Use GitHub environments for additional protection
3. **Workflow Review**: Require review for workflow dispatch
4. **Branch Protection**: Restrict who can modify the release workflow

### Environment Protection Rules

Configure protection rules for the `pypi` environment:

1. Go to **Repository Settings** → **Environments**
2. Create `pypi` environment (if not exists)
3. Set protection rules:
   - **Required reviewers**: Add yourself or trusted maintainers
   - **Wait timer**: 1-5 minutes for manual review
   - **Prevent self-review**: Enabled

## Verification Checklist

Before your first production release:

- [ ] PyPI project exists and you are an owner
- [ ] Trusted publisher configured correctly
- [ ] Repository permissions set correctly
- [ ] Release workflow committed to main branch
- [ ] Dry run test completed successfully
- [ ] No legacy API tokens remaining
- [ ] Environment protection rules configured (optional)

## First Production Release

Once Trusted Publishing is configured:

1. **Update Version**: Update version in `pyproject.toml` and `__init__.py`
2. **Run Release Workflow**:
   - Go to Actions → Release to PyPI
   - Click "Run workflow"
   - Set version and confirm
3. **Monitor**: Watch the workflow progress
4. **Verify**: Check PyPI project page for new version
5. **Test**: Install the new version: `pip install harvard-library-mcp==X.Y.Z`

## Support

- **PyPI Documentation**: [Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- **GitHub Documentation**: [OIDC Tokens](https://docs.github.com/actions/security-guides/using-oidc-tokens)
- **Issues**: [GitHub Issues](https://github.com/kltang/harvard-library-mcp/issues)