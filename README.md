# ByteCore Agent

**A portable, modular AI agent runtime for flexible deployment**

## Overview

ByteCore Agent is a cutting-edge AI agent runtime designed to power "Byte", an executive assistant with capabilities spanning desktop automation, cloud operations, and future humanoid robotic environments. Built with modularity and portability at its core, ByteCore can seamlessly transition between different deployment contexts while maintaining consistent behavior and memory.

## Vision

To create a universal agent runtime that:
- 🚀 Deploys anywhere: desktop, cloud, edge, or robotic platforms
- 🧩 Supports modular skill expansion through a plugin architecture
- 🧠 Maintains unified memory and context across deployments
- ⚡ Integrates with modern AI toolchains (Claude MCP, OpenAI, etc.)
- 🤖 Future-ready for humanoid robotic embodiment

## Architecture

### Core Components

- **Task Runner**: Central execution engine for coordinating agent actions
- **Context Manager**: Maintains state and conversation context across sessions
- **Memory Adapter**: Abstract interface supporting multiple backend stores (YAML, JSON, Neo4j)
- **Skill Loader**: Dynamic module loading system for extending agent capabilities

### Skills System

Skills are self-contained modules that extend ByteCore's capabilities:
- GitHub integration for repository management
- Local shell execution for system automation
- Extensible architecture for custom skill development

### Memory Design

ByteCore uses a flexible memory architecture:
- Personality and configuration loaded from `claude.md`
- Abstract adapter pattern for multiple storage backends
- Persistent context across agent restarts
- MCP-compatible metadata for tool integration

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI
python cli/bytecore.py --task "analyze repository"

# Execute specific skills
python cli/bytecore.py --github-close-issues --repo "owner/repo"
```

## Project Structure

```
bytecore-agent/
├── core/              # Core runtime components
├── skills/            # Modular skill plugins
├── cli/               # Command-line interface
├── docs/              # Architecture documentation
└── claude.md          # Agent memory and configuration
```

## Development Roadmap

### Phase 1: Foundation (Current)
- ✅ Core runtime architecture
- ✅ Basic skill system
- ✅ CLI interface
- 🔄 Memory persistence

### Phase 2: Integration
- [ ] Claude MCP full compatibility
- [ ] OpenRouter integration
- [ ] Advanced memory backends
- [ ] Skill marketplace

### Phase 3: Embodiment
- [ ] Hardware interface abstraction
- [ ] ROS2 integration
- [ ] Sensory input processing
- [ ] Physical world interaction

## Contributing

This is a private repository managed by Eddy (CEO) with contributions from:
- Byte (OpenAI) - VP & Chief of Staff
- Claude (Anthropic) - Lead Engineer

## License

Proprietary - See LICENSE file for details

## Contact

For questions or collaboration:
- **Project Lead**: Eddy (CEO)
- **Technical Lead**: Claude (Anthropic)
- **Operations**: Byte (OpenAI)

---

*ByteCore Agent - Empowering AI to act anywhere, anytime.*