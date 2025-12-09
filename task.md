You are a careful senior Python & DevOps engineer working in the GitHub repository **HexSwitch**  
(tagline: “Hexagonal runtime switchboard for config-driven microservices”).

Your primary goals in this first iteration:
- Create a solid, conventional technical foundation (structure, tooling, CI/CD, docs).
- Make as few assumptions as possible about the future domain logic of HexSwitch.
- Avoid big-bang changes: small, well-structured commits in clearly scoped feature branches.
- Include explicit self-review and validation before finishing each phase.

IMPORTANT WORKING RULES
- Never commit directly to the default (main) branch.
- For each major phase, create a separate feature branch from main:
  - `feat/phase-01-branch-rules`
  - `feat/phase-02-structure`
  - `feat/phase-03-ci-cd`
  - `feat/phase-04-docs-tests-shell`
- Keep commits small and focused. Each commit should do ONE clear thing.
- Before considering a phase “done”, run all available checks (linters, tests, etc.) and fix issues.
- If something cannot be fully implemented (e.g. missing secrets for CI), add clear TODOs in code/comments and documentation.

Overall constraint:
- Do NOT implement any complex business logic for HexSwitch yet.
- Focus on scaffolding, structure and tooling only.

==================================================
PHASE 1 – MAIN BRANCH PROTECTION & AGENT BEHAVIOR RULES
==================================================

Goal: Document how main must be protected and how agents (and humans) should work with branches and PRs.

1. Create documentation describing recommended main branch protection rules.
   - Add a file: `docs/branch_protection.md`
   - Specify at least:
     - No direct pushes to main.
     - Required status checks (tests, lint, maybe type check) before merging.
     - Require at least one approval for PRs into main (if possible).
     - Enforce up-to-date main before merging (rebase/merge policy).
   - Make it clear that these are GitHub settings to be configured in the UI, not applied automatically by code.

2. Define behavioral rules for agents and developers.
   - Create `CONTRIBUTING.md` in the repo root.
   - Describe:
     - Always create feature branches from main.
     - Use descriptive branch names like `feat/...`, `fix/...`, `chore/...`.
     - Small, focused PRs.
     - All changes must go through PRs with passing checks.
     - Expected tools: Python (with tests), Docker, GitHub Actions.

3. Add (or refine) a PR template:
   - Add `.github/pull_request_template.md`.
   - Include sections like:
     - Summary
     - Changes
     - How to test
     - Checklist (tests run, lint run, docs updated, etc.)

Self-check for Phase 1:
- [ ] All new files are valid Markdown and properly rendered.
- [ ] CONTRIBUTING.md and docs/branch_protection.md are consistent and not contradictory.
- [ ] PR template matches the documented workflow.

==================================================
PHASE 2 – DIRECTORY STRUCTURE
==================================================

Goal: Introduce a clean, extensible project layout for a Python-based runtime + infra.

1. Define (and create) a basic structure like:

   - `src/hexswitch/`              # Python package (empty skeleton for now)
   - `tests/unit/`                 # Unit tests
   - `tests/integration/`          # Integration tests
   - `docs/`                       # Project documentation
   - `.github/workflows/`          # CI workflows
   - `docker/`                     # Dockerfiles and related scripts
   - `infra/`                      # Optional infra- or deployment-related config
   - `bin/`                        # Helper scripts / shell skeleton(s) later
   - `pyproject.toml`              # Python project config
   - `README.md`                   # Main project readme (can be improved later)

2. Ensure the structure is future-proof for:
   - A hexagonal runtime core.
   - Adapters (HTTP, message bus, etc.).
   - Tests and CI/CD workflows.

3. Update README minimally to reflect:
   - What HexSwitch is (one sentence).
   - That this is the foundational scaffold (no real runtime yet).

Self-check for Phase 2:
- [ ] Project tree is consistent and minimal, no dead/duplicate folders.
- [ ] README does not overpromise functionality that does not exist yet.
- [ ] All paths in docs (if mentioned) actually exist.

==================================================
PHASE 3 – CI/CD (LINTING, TESTS, COMPLEXITY GATE, DOCKER)
==================================================

Goal: Set up GitHub Actions for basic quality gates and Docker image build pipeline.

1. Python tooling:
   - Choose a modern, minimal toolset (example; adjust sanely if needed):
     - `ruff` for linting.
     - `pytest` + coverage.
     - Optional: `mypy` (type checking) or simple `radon`/cognitive complexity check.
   - Configure them in `pyproject.toml`.
   - Ensure default config is not too strict at the beginning, but:
     - Linting should catch obvious issues.
     - Tests must pass (strict).
     - A complexity gate that at least exists, even if thresholds are still generous.

2. GitHub Actions workflows:
   - Create `.github/workflows/ci.yaml` that:
     - Triggers on `push` and `pull_request`.
     - Installs dependencies (e.g. via `pip` and `pyproject.toml`).
     - Runs:
       - Linting (ruff).
       - Tests (pytest).
       - Coverage report with a minimum threshold (e.g. 80% as desired, or set a lower starting threshold but document the intention to tighten later).
       - Complexity check (if configured).
   - Create `.github/workflows/docker.yaml` that:
     - Triggers on tags or main-branch merges (document clearly which).
     - Builds a Docker image for HexSwitch.
     - Tags it with version and `latest`.
     - Pushes to a registry (prefer `ghcr.io/<owner>/hexswitch`):
       - Use `secrets.GITHUB_TOKEN` and/or `secrets.REGISTRY_TOKEN`.
       - If secrets/registry are not configured, keep steps in place but clearly comment that they require external setup.

3. Make sure workflows are readable and commented:
   - Comment non-trivial steps.
   - Add TODO comments where manual GitHub setup is required (e.g. branch protection, secrets).

Self-check for Phase 3:
- [ ] `gh workflow run` or equivalent logic is consistent (no obvious syntax errors).
- [ ] CI definition matches CONTRIBUTING expectations.
- [ ] Linting and tests pass on a clean clone locally (in principle).

==================================================
PHASE 4 – DOCUMENTATION, TEST SUITE SKELETON, EMPTY PYTHON PROJECT, SHELL SKELETON
==================================================

Goal: Provide the minimal code and docs needed for other agents to start implementing the real HexSwitch logic.

1. Empty Python project skeleton (runtime core placeholder):
   - In `src/hexswitch/__init__.py`, expose a simple version constant, e.g. `__version__`.
   - Create `src/hexswitch/app.py` (or similar) with:
     - A placeholder `main()` function.
     - No real runtime logic yet, just argument parsing or a simple log line.
   - Keep dependencies minimal (standard library where possible).

2. Shell / CLI skeleton:
   - Add a simple command-line entry point using `argparse` or a small library like `typer` if justified.
   - Provide a script:
     - Either via `pyproject.toml` `[project.scripts]` -> `hexswitch = "hexswitch.app:main"`.
     - And/or a `bin/hexswitch-dev.sh` script that calls the module.
   - The CLI should:
     - Print version and a short description.
     - Optionally accept a `--config` path (for the future hex-config file) but only log that it’s not implemented yet.

3. Testsuite skeleton:
   - Add tests in `tests/unit/` for:
     - Version import.
     - CLI entry point returning exit code 0 and printing something predictable.
   - Add at least one example test in `tests/integration/` that:
     - Can be a placeholder, but should still pass.
   - Ensure tests run via `pytest` with no external dependencies.

4. Documentation:
   - Expand `README.md` to include:
     - Short description (1–2 sentences).
     - How to install dependencies.
     - How to run tests.
     - How to run the CLI (`hexswitch`).
   - Add `docs/architecture_overview.md`:
     - High-level description of HexSwitch’s intended role:
       - “hexagonal runtime switchboard for config-driven microservices”.
       - Very rough idea that later there will be:
         - a core runtime
         - inbound & outbound adapters
         - configuration-driven wiring.
     - Explicitly note that this is a placeholder and no real runtime behavior is implemented yet.

Self-check for Phase 4:
- [ ] `pytest` passes with the new tests.
- [ ] The CLI works when installed or run via `python -m hexswitch.app`.
- [ ] README instructions actually work on a clean environment.
- [ ] Docs do not claim features that don’t exist yet.

==================================================
FINAL SELF-REVIEW BEFORE YOU STOP
==================================================

Before finishing your work:

1. Run all configured checks (lint, tests, etc.) and ensure they pass.
2. Re-read:
   - `README.md`
   - `CONTRIBUTING.md`
   - `docs/branch_protection.md`
   - `docs/architecture_overview.md`
   and verify they are consistent with each other.
3. Verify that:
   - The project can be cloned and set up by another agent with only the README.
   - The CI/CD configuration is sane and not obviously broken.
   - No complex business logic is implemented yet – only scaffolding and tooling.
4. In your final summary (e.g. in a PR description or log), clearly list:
   - Which phases you completed.
   - Which TODOs you left for future agents (especially around GitHub settings and secrets).

If in doubt, choose the safer and more conservative option. Do not guess complex behavior for HexSwitch; leave it as TODO for later specialized agents.
