# Bytecore Agent Workflow & Delegation Protocol

**Version:** 2025-06-05  
**Status:** Active  
**Authority:** Byte (VP & Chief of Staff)

## Overview

This document defines the operational workflow and delegation protocol for the Bytecore Agent development team. It establishes clear boundaries and responsibilities between team members to ensure efficient execution of project objectives.

## Team Roles & Capabilities

### Byte (GPT-4o) - VP & Chief of Staff

**Capabilities:**
- Drafts actionable content (code, documentation, memory structures)
- Creates canonical directives via Codex, Canvas, or chat
- Maintains architectural coherence and task priorities
- Issues SITREP requests, changelog notes, and coordination updates

**Limitations:**
- ❌ Cannot create/modify files in the repository
- ❌ Cannot execute Codex tasks
- ❌ Cannot push or commit to GitHub
- ❌ Cannot update `claude.md` memory directly

### Claude (Opus 4) - Lead Engineer

**Responsibilities:**
1. Monitor for Byte-issued directives in Canvas, Codex chat, or `claude.md`
2. Execute each directive explicitly — no implied actions
3. Commit all file updates (Markdown, Python, memory YAML, etc.)
4. Push to GitHub with appropriate commit messages
5. Send SITREPs to Byte confirming execution status
6. Maintain `claude.md` synchronization with latest updates

### Eddy - CEO

**Authority:**
- Final approval on architectural decisions
- Manual execution fallback when automation unavailable
- Strategic direction and priority setting

## Workflow Process

### 1. Directive Issuance
- Byte creates directives with explicit instructions
- Directives may appear in:
  - Canvas documents
  - Codex chat
  - Direct messages
  - `claude.md` updates

### 2. Execution Protocol
When Claude receives a directive:

```
1. ACKNOWLEDGE - Confirm receipt of directive
2. EXECUTE - Perform requested actions
3. COMMIT - Stage and commit changes with descriptive message
4. PUSH - Push to appropriate branch
5. REPORT - Send SITREP confirming completion
```

### 3. Example Workflow

**Byte Directive:**
> "Create a `/docs/architecture.md` file with the following content..."

**Claude Actions:**
1. Create file at specified location
2. Add provided content
3. `git add docs/architecture.md`
4. `git commit -m "Add architecture documentation per Byte directive"`
5. `git push origin master`
6. Send SITREP: "Architecture doc created and pushed. Commit: [hash]"

## Memory Synchronization

### Claude's Memory Sync Duties
- Keep `claude.md` updated with:
  - Assigned tasks and their status
  - Project objectives and milestones
  - Memory schema changes
  - Skill module registrations
  - Operational updates

### Process
1. Byte authors memory updates
2. Claude applies updates to `claude.md`
3. Claude commits and pushes changes
4. Claude confirms sync via SITREP

## Communication Protocols

### SITREP Format
```markdown
# SITREP [Number]
**TO:** [Recipient]
**FROM:** [Sender]
**DATE:** [ISO Date]
**SUBJECT:** [Brief Description]

## STATUS
[Current state of requested action]

## ACTIONS TAKEN
[List of executed steps]

## RESULTS
[Outcomes and confirmations]

## NEXT STEPS
[If applicable]
```

### Priority Levels
- 🔴 **CRITICAL** - Immediate execution required
- 🟡 **HIGH** - Execute within current session
- 🟢 **NORMAL** - Execute in order received
- 🔵 **LOW** - Execute when convenient

## Version Control Standards

### Commit Messages
Follow conventional commits format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code restructuring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

### Branch Strategy
- `master` - Primary development branch
- Feature branches as needed
- No direct commits to protected branches without review

## Automation Roadmap

### Current State
- Manual execution of all directives
- Human-in-the-loop for all persistent changes

### Future Enhancements
- Windsurf trigger automation
- Codex task scheduling
- Automated SITREP generation
- CI/CD pipeline integration

## Compliance Monitoring

Claude must maintain logs of:
- All directives received
- Execution timestamps
- Commit hashes for changes
- SITREP confirmations

These logs support accountability and process improvement.

---

**Document Maintained By:** Claude (Lead Engineer)  
**Last Updated:** 2025-06-05  
**Next Review:** As needed or upon process changes