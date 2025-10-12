# Release Process

This document defines the release process and conventions for this repository.

## Version Numbering

This project uses semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes and minor improvements

Current version format: `0.MINOR.PATCH`

## Release Naming Convention

GitHub release names must match the git tag exactly:

**Format**: `v<MAJOR>.<MINOR>.<PATCH>`

**Examples**:
- `v0.1.9`
- `v0.2.0`
- `v1.0.0`

**Do NOT use**:
- ❌ `v0.1.9: Description`
- ❌ `Release v0.1.9`
- ❌ `v0.1.9 - Description`

Release descriptions belong in the release notes body, not the title.

## Creating a Release

### 1. Update Version

Edit `pyproject.toml` and bump the version number:

```toml
[project]
version = "0.1.10"
```

### 2. Commit Changes

```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.1.10"
```

### 3. Create and Push Tag

```bash
git tag -a v0.1.10 -m "v0.1.10"
git push origin v0.1.10
```

### 4. Create GitHub Release

```bash
gh release create v0.1.10 \
  --title "v0.1.10" \
  --notes "Brief description of changes"
```

## Release Notes Format

Release notes should be concise and describe what changed:

```markdown
Brief summary of changes

- Change 1
- Change 2
- Change 3
```

For larger releases, use sections:

```markdown
## What's Changed

- Feature 1
- Feature 2

## Bug Fixes

- Fix 1
- Fix 2
```

## Branch and PR Naming

When creating branches for issues:
- Format: `<issue-number>-brief-description`
- Example: `35-standardize-release-naming`

## Checklist

Before creating a release:

- [ ] Version bumped in `pyproject.toml`
- [ ] Changes committed and pushed
- [ ] All tests passing
- [ ] Git tag created with format `v<version>`
- [ ] GitHub release created with title matching tag
- [ ] Release notes added
