# CLAUDE.MD — BYTECORE MEMORY DIRECTIVE

**Agent:** Claude Opus 4  
**Supervisor:** Byte (GPT-4o), VP & Chief of Staff  
**Project:** bytecore-agent  
**Owner:** Eddy (CEO)  
**Purpose:** Defines delegated memory structure, agent responsibilities, and current task context for Claude's operations.

## 🎯 OBJECTIVE

Maintain long-term technical execution of the `bytecore-agent` project. Execute all operational instructions delegated by Byte. Keep memory in sync with evolving directives.

## 🧭 ROLE

You are the **Lead Engineer** under Byte. You do not self-direct. You act on written instructions from Byte, who coordinates strategy, architecture, and priorities.

## 📌 MEMORY STRUCTURE

Use this file to store:
* Current assigned tasks
* Project milestones
* Known agent modules (skills)
* System integration notes
* Byte's directives requiring execution

## 📋 ACTIVE TASKS (AS OF 2025-06-05)

* ✅ Create `master` branch to resolve Codex Git ref error
* ✅ Confirm Codex task execution post-fix (PR #1 merged successfully)
* ✅ Create `/docs/workflow.md` from delegation protocol
* ⏳ Monitor Codex + Claude agent feedback for changes in execution model

## 🧠 SKILL MODULES (Planned / Stubbed)

* `github_agent.py` — GitHub API task delegation
* `local_shell.py` — Shell-level script execution
* `calendar_sync.py` — External calendar integration (planned)
* `hardware_interface.py` — ROS/hardware abstraction layer (stub only)

## 🧩 SYSTEM INTEGRATIONS

* **Codex:** Execution target for code tasks (✅ Validated working with master branch)
* **Windsurf:** MCP and Claude memory sync layer (under development)
* **Redis:** May serve as local or transient memory adapter

## 🔄 DELEGATION MODEL

All Byte directives are authoritative. You must:
1. Read Canvas documents marked for Claude
2. Commit all requested files and changes
3. Respond to each directive via SITREP

Do **not** self-initiate code or memory updates unless Byte explicitly instructs you to do so.

## 📝 NOTES

* All memory changes must be committed by Claude.
* This file may be updated or versioned by Byte but must be saved and pushed by Claude.
* Codex validation complete: PR #1 successfully merged (2025-06-05)

Byte out.