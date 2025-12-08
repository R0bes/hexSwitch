# Contributing to HexSwitch

Thank you for your interest in contributing to HexSwitch! This document outlines the workflow and guidelines for contributing to this project.

## Workflow Overview

HexSwitch follows a branch-based workflow where all changes go through Pull Requests (PRs). This ensures code quality, enables code review, and maintains a clean project history.

## Branch Strategy

### Creating Feature Branches

- **Always create feature branches from `main`**
- Use descriptive branch names following the convention:
  - `feat/...` - New features
  - `fix/...` - Bug fixes
  - `chore/...` - Maintenance tasks (dependencies, tooling, etc.)
  - `docs/...` - Documentation updates
  - `refactor/...` - Code refactoring

### Examples

```bash
git checkout main
git pull origin main
git checkout -b feat/add-new-adapter
git checkout -b fix/memory-leak
git checkout -b chore/update-dependencies
```

## Pull Request Guidelines

### PR Requirements

1. **Small and Focused**: Each PR should address a single concern or feature
   - Avoid mixing unrelated changes
   - If a feature is large, break it into smaller PRs

2. **All Checks Must Pass**: Before merging, ensure:
   - All tests pass (`pytest`)
   - Linting passes (`ruff`)
   - Code coverage meets the threshold
   - Type checking passes (if configured)

3. **Up-to-Date**: Keep your branch up to date with `main`
   ```bash
   git checkout main
   git pull origin main
   git checkout your-branch
   git rebase main  # or git merge main
   ```

4. **Descriptive PR Description**: Use the PR template to provide:
   - Summary of changes
   - How to test
   - Checklist of completed items

### PR Process

1. Create a feature branch from `main`
2. Make your changes with small, focused commits
3. Push your branch to the remote repository
4. Create a Pull Request targeting `main`
5. Wait for CI checks to pass
6. Address any review feedback
7. Once approved and all checks pass, the PR can be merged

## Development Tools

This project uses the following tools:

- **Python**: Primary development language (Python 3.12+)
- **Testing**: `pytest` for unit and integration tests
- **Linting**: `ruff` for code quality checks
- **Docker**: Containerization for deployment
- **GitHub Actions**: CI/CD pipelines

### Local Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hexSwitch
   ```

2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run tests:
   ```bash
   pytest
   ```

4. Run linting:
   ```bash
   ruff check .
   ```

## Commit Guidelines

- **Small, focused commits**: Each commit should do one clear thing
- **Descriptive commit messages**: Use clear, imperative language
- **Follow conventional commits** (optional but recommended):
  - `feat: add new adapter`
  - `fix: resolve memory leak`
  - `chore: update dependencies`
  - `docs: update README`

## Code Review

- Be respectful and constructive in reviews
- Focus on code quality, not personal preferences
- Ask questions if something is unclear
- Approve when the PR meets the project standards

## Getting Help

If you have questions or need help:

1. Check the existing documentation
2. Review existing issues and PRs
3. Create an issue for discussion
4. Ask in PR comments

## Related Documentation

- [Branch Protection Rules](docs/branch_protection.md) - Details on branch protection settings
- [Architecture Overview](docs/architecture_overview.md) - High-level project architecture
- [README.md](README.md) - Project overview and setup instructions

