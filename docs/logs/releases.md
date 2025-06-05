# ByteCore Agent Release Log

## [Unreleased]

### Added
- SkillKit module scaffold (in progress)
- GitHub Actions for Black formatting checks (pending)

## [unversioned] - 2025-06-05

### Added
- **PR #1**: Agent roster documentation (`AGENTS.md`) - Establishes canonical reference for all system actors, roles, and responsibilities
- Black code formatter configuration (`pyproject.toml`) - Standardizes Python code style across the project
- Workflow and delegation protocol documentation (`/docs/workflow.md`) - Defines operational procedures for team collaboration
- Operational memory structure (`claude.md`) - Tracks tasks, directives, and system state for Claude's execution
- Release changelog (`/docs/logs/releases.md`) - Project history and version tracking
- GitHub Actions CI/CD pipeline (`.github/workflows/python.yml`) - Automated code quality checks
- Unit tests for SkillKit modules - Tests for skill discovery and GitHub agent functionality
- CLI extensions - Added `--task` and `--params` options for direct skill execution
- pytest.ini configuration - Registers asyncio marker and loads pytest-asyncio automatically

### Changed
- Default branch changed from `main` to `master` to resolve Codex Git reference errors
- All Python files reformatted to Black code style standards (11 files modified)
- Updated `claude.md` from ByteCore Agent configuration to Claude operational memory
- Enhanced CLI with skill execution capabilities
- Extended documentation with new CLI usage examples

### Fixed
- Codex "git ref master does not exist" error - Created and set `master` as default branch
- Code style inconsistencies - Applied Black formatter to entire codebase
- Async compatibility warnings in SkillLoader
- pytest asyncio warnings with proper configuration

### Technical Details
- **Merge Commits:**
  - `8382732` - Merge pull request #1 (AGENTS.md + code formatting)
  - `bfc5a26` - Update claude.md with operational memory directive
  - `8ddfc50` - Add workflow and delegation protocol documentation
  - `a781c12` - Mark Codex validation complete
  - `a1e5ba7` - Add release changelog and GitHub Actions for code quality
  - `5a2ee67` - Update claude.md with completed task status
  - `98eef07` - Add SITREP summary to release changelog
  - `3801c16` - Update claude.md with SkillKit discovery notes

### SITREP Summary
- **SITREP #1**: Git ref fix completed - Created `master` branch, deleted `main`, enabling Codex operations
- **SITREP #2**: Delegation protocol implemented - Created workflow.md, demonstrated directive execution pipeline
- **SITREP #3**: Claude.md operational memory established - Replaced agent config with task tracking system
- **SITREP #4**: Codex validation successful - PR #1 merged with AGENTS.md and Black formatting
- **SITREP #5**: Infrastructure foundation laid - Changelog created, GitHub Actions CI/CD implemented
- **SITREP #6**: SkillKit validation & GitHub agent review - All modules validated, unit tests passing, CLI extended with skill execution

### Validation
- Codex task execution confirmed working post-fix
- PR workflow validated: branch creation → changes → PR → merge
- All Python files compile without errors
- Repository fully operational with new `master` branch
- CI/CD pipeline ready for automated quality checks
- Unit tests passing: 2 tests in 0.07s
- SkillKit modules load correctly via CLI and tests

### Project Status
**FROZEN** - ByteCore Agent roadmap frozen pending hardware readiness (2025-06-05)

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format*