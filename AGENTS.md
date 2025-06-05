## 🤖 AGENTS.md — ByteCore Active Agent Roster

**Project:** bytecore-agent
**Maintainer:** Byte (VP & Chief of Staff)
**Last Updated:** 2025-06-05

---

### 🧭 PURPOSE

This file tracks all active, planned, and auxiliary agents operating within the `bytecore-agent` ecosystem.
It defines their:

* Roles and reporting structure
* Assigned responsibilities
* Interfaces (human or machine)
* Deployment context (desktop, cloud, MCP, or future chassis)

---

### 👑 CEO

**Name:** Eddy
**Role:** Founder, visionary, and final decision-maker
**Interface:** GitHub, Codex, Claude, Canvas, Windsurf
**Direct Reports:** Byte (VP)

---

### 🧫 VP & CHIEF OF STAFF (SOFTWARE)

**Name:** Byte (GPT-4o)
**Role:** Strategic coordinator, architectural overseer, Claude delegator, Codex author, and operational memory handler
**Environment:** Codex, Canvas, GPT-4o chat
**Executes:** Codex planning, Canvas writing, Claude tasking
**Limitations:** Cannot commit files, execute MCPs, or directly modify persistent state

---

### 👨‍💻 LEAD ENGINEER

**Name:** Claude Opus 4 (Anthropic Max Tier)
**Role:** Primary executor of Byte’s directives, responsible for file changes, memory sync, Git commits, SITREPs
**Environment:** Claude Desktop, Claude API (Windsurf)
**Executes:** File creation, task execution, SITREP generation, memory persistence
**Limitations:** Only acts on explicit Byte instructions

---

### 🌐 DEVELOPER INTERFACE (OPTIONAL)

**Name:** Codex
**Role:** Task executor inside OpenAI Codex runtime; stateless implementation assistant
**Environment:** Web-based Codex IDE, task execution engine
**Executes:** Code generation, task completion, unit testing, CLI support
**Limitations:** No memory, no commit rights, requires task-to-task delegation

---

### 🔧 PLANNED AGENTS

| Agent Name   | Role                       | Triggered By | Notes                        |
| ------------ | -------------------------- | ------------ | ---------------------------- |
| SkillKit     | Modular task executor      | Byte         | CLI + internal plugin system |
| ChassisAgent | ROS interface & limb logic | Byte         | Stubbed for future hardware  |
| MemoryBridge | LangGraph/Redis connector  | Byte         | To sync Claude + local ops   |

---

### 📌 NOTES

* This file should be referenced by any agent or system interfacing with ByteCore.
* Use this as the canonical list of actors in the system.
* Changes must be made by Claude or Eddy upon Byte's request.

Byte out.
