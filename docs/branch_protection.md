# Branch Protection Rules

This document describes the recommended branch protection rules for the HexSwitch repository. These rules must be configured manually in the GitHub repository settings.

## Overview

The `main` branch is the default branch and should be protected to ensure code quality and maintainability. All changes to `main` must go through Pull Requests (PRs) that pass all required checks.

## Required Settings

### 1. No Direct Pushes to Main

- **Setting**: Block direct pushes to the `main` branch
- **Rationale**: Ensures all changes are reviewed and tested before being merged
- **Configuration**: In GitHub Settings → Branches → Branch protection rules → Add rule for `main` → Enable "Restrict pushes that create files"

### 2. Required Status Checks

Before a PR can be merged into `main`, the following status checks must pass:

- **Linting**: `ruff` linting must pass
- **Tests**: All `pytest` tests must pass
- **Coverage**: Code coverage must meet the minimum threshold (currently 80%)
- **Type Checking** (optional): `mypy` type checking (if configured)

**Configuration**: In branch protection rules → Enable "Require status checks to pass before merging" → Select the required checks from the list

### 3. Require Pull Request Reviews

- **Setting**: Require at least one approval before merging
- **Rationale**: Ensures code review and knowledge sharing
- **Configuration**: Enable "Require a pull request before merging" → Set "Required number of approvals" to at least 1

### 4. Require Branch to be Up to Date

- **Setting**: Require branches to be up to date with `main` before merging
- **Rationale**: Prevents merge conflicts and ensures compatibility
- **Configuration**: Enable "Require branches to be up to date before merging"

### 5. Additional Recommendations

- **Dismiss stale reviews**: Enable to require fresh reviews when new commits are pushed
- **Require conversation resolution**: Enable to ensure all PR comments are addressed
- **Do not allow bypassing**: Restrict administrators from bypassing these rules (recommended for strict enforcement)

## Implementation Notes

⚠️ **Important**: These rules are **not automatically applied** by code. They must be configured manually in the GitHub repository settings:

1. Go to Settings → Branches
2. Add or edit the branch protection rule for `main`
3. Configure each setting as described above
4. Save the rule

## Exceptions

In exceptional circumstances (e.g., emergency hotfixes), administrators may need to bypass these rules. However, this should be:
- Documented in the commit message
- Followed by a post-mortem or review
- Used only when absolutely necessary

## Related Documentation

- See [CONTRIBUTING.md](../CONTRIBUTING.md) for workflow guidelines
- See [.github/pull_request_template.md](../.github/pull_request_template.md) for PR requirements

