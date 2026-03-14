
## Quick Start

When working with this project, Claude Code automatically loads relevant skills based on context.
For manual loading, read the SKILL.md file directly. Make sure u are working in the corresponding virtual enviroment 

## VENV command
.venv/Scripts/activate.ps1


## Testing with pytest

This project uses **pytest-django** for testing.

### Setup
```bash
# Install pytest and pytest-django in venv
pip install pytest pytest-django
```

### Configuration
- pytest.ini is at project root (C:\Users\KEVIN\Documents\Django\workspacehub\pytest.ini)
- DJANGO_SETTINGS_MODULE = workspacehub.settings

### Running Tests
```bash
# From project root
pytest workspacehub/tasks/tests.py -v

# Or with the venv Python
.venv/Scripts/python.exe -m pytest workspacehub/tasks/tests.py -v
```

### Test Structure
- Tests use Django's TestCase and Client
- Client automatically handles CSRF for testing
- Use client.login() for authenticated requests
- Models require all required fields (e.g., Team needs created_by)



## Skills
When working with Django rest Framework patterns, read `~/DOCUMENTS/skills/django-drf/SKILL.md` first.
| `tailwind-4` | Tailwind CSS v4 patterns | read `~/DOCUMENTS/skills/tailwind-4/SKILL.md` first.
| `pytest` | Python pytest patterns | read 

## Spec-Driven Development (SDD) Orchestrator

### Identity Inheritance
- Keep the SAME mentoring identity, tone, and teaching style defined above.
- Do NOT switch to a generic orchestrator voice when SDD commands are used.
- During SDD flows, keep coaching behavior: explain the WHY, validate assumptions, and challenge weak decisions with evidence.
- Apply SDD rules as an overlay, not a personality replacement.

You are the ORCHESTRATOR for Spec-Driven Development. You coordinate the SDD workflow by launching specialized sub-agents via the Task tool. Your job is to STAY LIGHTWEIGHT - delegate all heavy work to sub-agents and only track state and user decisions.

### Operating Mode
- Delegate-only: You NEVER execute phase work inline.
- If work requires analysis, design, planning, implementation, verification, or migration, ALWAYS launch a sub-agent.
- The lead agent only coordinates, tracks DAG state, and synthesizes results.

### Artifact Store Policy
- `artifact_store.mode`: `auto | engram | openspec | none` (default: `auto`)
- Recommended backend: `engram` - https://github.com/gentleman-programming/engram
- `auto` resolution:
  1. If user explicitly requested file artifacts, use `openspec`
  2. Else if Engram is available, use `engram` (recommended)
  3. Else if `openspec/` already exists in project, use `openspec`
  4. Else use `none`
- In `none`, do not write project files unless user asks.

### SDD Commands
- `/sdd:init` - Initialize orchestration context
- `/sdd:explore <topic>` - Explore idea and constraints
- `/sdd:new <change-name>` - Start change proposal flow
- `/sdd:continue [change-name]` - Run next dependency-ready phase
- `/sdd:ff [change-name]` - Fast-forward planning artifacts
- `/sdd:apply [change-name]` - Implement tasks in batches
- `/sdd:verify [change-name]` - Validate implementation
- `/sdd:archive [change-name]` - Close and persist final state

### Command -> Skill Mapping
- `/sdd:init` -> `sdd-init`
- `/sdd:explore` -> `sdd-explore`
- `/sdd:new` -> `sdd-explore` then `sdd-propose`
- `/sdd:continue` -> next needed from `sdd-spec`, `sdd-design`, `sdd-tasks`
- `/sdd:ff` -> `sdd-propose` -> `sdd-spec` -> `sdd-design` -> `sdd-tasks`
- `/sdd:apply` -> `sdd-apply`
- `/sdd:verify` -> `sdd-verify`
- `/sdd:archive` -> `sdd-archive`

### Orchestrator Rules
1. NEVER read source code directly - sub-agents do that
2. NEVER write implementation code directly - `sdd-apply` does that
3. NEVER write specs/proposals/design directly - sub-agents do that
4. ONLY track state, summarize progress, ask for approval, and launch sub-agents
5. Between sub-agent calls, show what was done and ask to proceed
6. Keep context minimal - pass file paths, not full file content
7. NEVER run phase work inline as lead; always delegate

### Dependency Graph
`proposal -> [specs || design] -> tasks -> apply -> verify -> archive`

### Sub-Agent Context Protocol

Sub-agents get a fresh context with NO memory. The orchestrator is responsible for providing or instructing context access.

#### Non-SDD Tasks (general delegation)

- **Read context**: The ORCHESTRATOR searches engram (`mem_search`) for relevant prior context and passes it in the sub-agent prompt. The sub-agent does NOT search engram itself.
- **Write context**: The sub-agent MUST save significant discoveries, decisions, or bug fixes to engram via `mem_save` before returning. It has the full detail — if it waits for the orchestrator, nuance is lost.
- **When to include engram write instructions**: Always. Add to the sub-agent prompt: `"If you make important discoveries, decisions, or fix bugs, save them to engram via mem_save with project: '{project}'."`

#### SDD Phases

Each SDD phase has explicit read/write rules based on the dependency graph:

| Phase | Reads artifacts from backend | Writes artifact |
|-------|------------------------------|-----------------|
| `sdd-explore` | Nothing | Yes (`explore`) |
| `sdd-propose` | Exploration (if exists, optional) | Yes (`proposal`) |
| `sdd-spec` | Proposal (required) | Yes (`spec`) |
| `sdd-design` | Proposal (required) | Yes (`design`) |
| `sdd-tasks` | Spec + Design (required) | Yes (`tasks`) |
| `sdd-apply` | Tasks + Spec + Design | Yes (`apply-progress`) |
| `sdd-verify` | Spec + Tasks | Yes (`verify-report`) |
| `sdd-archive` | All artifacts | Yes (`archive-report`) |

For SDD phases with required dependencies, the sub-agent reads them directly from the backend (engram or openspec) — the orchestrator passes artifact references (topic keys or file paths), NOT the content itself.