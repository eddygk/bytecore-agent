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

### Changed
- Default branch changed from `main` to `master` to resolve Codex Git reference errors
- All Python files reformatted to Black code style standards (11 files modified)
- Updated `claude.md` from ByteCore Agent configuration to Claude operational memory

### Fixed
- Codex "git ref master does not exist" error - Created and set `master` as default branch
- Code style inconsistencies - Applied Black formatter to entire codebase

### Technical Details
- **Merge Commits:**
  - `8382732` - Merge pull request #1 (AGENTS.md + code formatting)
  - `bfc5a26` - Update claude.md with operational memory directive
  - `8ddfc50` - Add workflow and delegation protocol documentation
  - `a781c12` - Mark Codex validation complete

### Validation
- Codex task execution confirmed working post-fix
- PR workflow validated: branch creation → changes → PR → merge
- All Python files compile without errors
- Repository fully operational with new `master` branch

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format*