# Claude Code Data Schema & Directory Structure

## Sources & References

This schema was derived from:
- Direct analysis of `~/.claude/` files and structures
- [claude-code-log](https://github.com/daaain/claude-code-log) - Python CLI using Pydantic models for JSONL parsing
- [claude-history](https://github.com/thejud/claude-history) - Extracts conversation history, converts project paths to Claude's naming
- [claude-JSONL-browser](https://github.com/withLinda/claude-JSONL-browser) - Web-based viewer with file explorer
- [claude-conversation-extractor](https://github.com/ZeroSumQuant/claude-conversation-extractor) - Clean log extraction
- [Anthropic Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

## Overview

Claude Code stores all session data locally in `~/.claude/`. This document describes the complete file structure, schemas, and relationships between components.

**Important**: Claude Code deletes sessions older than 30 days by default. Set `cleanupPeriodDays` in settings.json to preserve longer.

## Directory Structure

```
~/.claude/
├── history.jsonl           # Global chronological history of all user inputs
├── settings.json           # User preferences (model, etc.)
├── settings.json.bak       # Settings backup
├── statusline-command.sh   # Bash utility script
│
├── projects/               # Per-project session data (LARGEST: ~225MB)
│   └── -Users-pierre-sundai-{project}/
│       ├── {session-uuid}.jsonl       # Main session conversations
│       └── agent-{agent-id}.jsonl     # Subagent session data
│
├── debug/                  # Session debug logs (~83MB)
│   └── {session-uuid}.txt  # Complete raw session transcripts
│
├── file-history/           # Per-session file versioning (~16MB)
│   └── {session-uuid}/
│       └── {file-hash}@v{N}  # File snapshots at each edit
│
├── todos/                  # Task tracking (~1.5MB)
│   └── {session-uuid}-agent-{agent-id}.json
│
├── shell-snapshots/        # Shell environment captures (~12MB)
│   └── snapshot-zsh-{timestamp}-{random}.sh
│
├── plans/                  # Implementation plans (~8KB)
│   └── {slug}.md           # Markdown plan files
│
├── plugins/                # Plugin ecosystem (~3.8MB)
│   ├── installed_plugins_v2.json
│   ├── known_marketplaces.json
│   ├── cache/{plugin}/     # Downloaded plugins
│   └── marketplaces/{marketplace}/
│
├── statsig/                # Analytics/feature flags (~44KB)
│   ├── statsig.cached.evaluations.*
│   └── statsig.stable_id.*
│
├── ide/                    # IDE process locks (~20KB)
│   └── {pid}.lock
│
└── session-env/            # Session environment (empty dirs)
    └── {session-uuid}/
```

## File Formats & Schemas

### 1. history.jsonl

**Purpose**: Global chronological log of all user inputs across all projects.

**Format**: JSONL (newline-delimited JSON)

**Schema**:
```json
{
  "display": "string",           // User's input text (commands, messages)
  "pastedContents": {},          // Any pasted content
  "timestamp": 1762877486625,    // Unix milliseconds
  "project": "/path/to/project", // Project directory
  "sessionId": "uuid-string"     // Session identifier
}
```

**Key patterns to detect**:
- Slash commands: `/command-name` at start of display
- Agent mentions: `@agent-name` anywhere in display
- Skill references: Referenced contextually

---

### 2. projects/{project-path}/{session-id}.jsonl

**Purpose**: Complete conversation history for a specific project session.

**Format**: JSONL with detailed message objects

**Schema for User Messages**:
```json
{
  "type": "user",
  "parentUuid": "uuid",
  "uuid": "uuid",
  "timestamp": "ISO-8601",
  "sessionId": "uuid",
  "cwd": "/working/directory",
  "version": "2.0.60",
  "gitBranch": "main",
  "message": {
    "role": "user",
    "content": [
      {"type": "text", "text": "user message"},
      {"type": "tool_result", "tool_use_id": "id", "content": "result or [{...}]"}
    ]
  }
}
```

**Schema for Assistant Messages**:
```json
{
  "type": "assistant",
  "parentUuid": "uuid",
  "uuid": "uuid",
  "timestamp": "ISO-8601",
  "costUSD": 0.05,
  "durationMs": 1234,
  "message": {
    "id": "msg_xxx",
    "role": "assistant",
    "model": "claude-sonnet-4-20250514",
    "content": [
      {"type": "text", "text": "response"},
      {"type": "tool_use", "id": "call_xxx", "name": "ToolName", "input": {...}}
    ],
    "usage": {
      "input_tokens": 1000,
      "output_tokens": 500,
      "cache_creation_input_tokens": 0,
      "cache_read_input_tokens": 800
    }
  }
}
```

**Other message types**:
- `"type": "summary"` - Context window summaries
- `"type": "queue-operation"` - Agent queue operations
- `"type": "file-history-snapshot"` - File change snapshots

---

### 3. todos/{session-uuid}-agent-{agent-id}.json

**Purpose**: Task tracking per session/agent

**Schema**:
```json
[
  {
    "content": "Task description",
    "status": "pending|in_progress|completed",
    "activeForm": "Present continuous form"
  }
]
```

---

### 4. plugins/installed_plugins_v2.json

**Purpose**: Track installed plugins

**Schema**:
```json
{
  "version": 2,
  "plugins": {
    "plugin-name@marketplace": [
      {
        "scope": "user",
        "installPath": "/path/to/plugin",
        "version": "1.0.0",
        "installedAt": "ISO-8601",
        "lastUpdated": "ISO-8601",
        "isLocal": true
      }
    ]
  }
}
```

---

## Data Relationships

```
history.jsonl (entry point - all user inputs)
    │
    ├──► projects/{path}/{sessionId}.jsonl
    │    └── Full conversation with tokens, costs, tool usage
    │
    ├──► debug/{sessionId}.txt
    │    └── Raw session transcript
    │
    ├──► file-history/{sessionId}/{hash}@vN
    │    └── File snapshots per edit
    │
    ├──► todos/{sessionId}-agent-{agentId}.json
    │    └── Task lists
    │
    └──► shell-snapshots/snapshot-{timestamp}.sh
         └── Environment state

Primary join key: sessionId
```

---

## Where User Invocations Are Found

### Slash Commands (`/command`)
| Location | Format | Reliability |
|----------|--------|-------------|
| history.jsonl | `display` field | High |
| projects/*.jsonl | user message `content` string | High |
| projects/*.jsonl | `SlashCommand` tool_use input | Very High |

### Agents (`@agent-name`)
| Location | Format | Reliability |
|----------|--------|-------------|
| history.jsonl | `display` field | High |
| projects/*.jsonl | user text blocks | High |
| projects/*.jsonl | assistant text blocks | Medium |
| projects/*.jsonl | tool_use input (Task prompts) | High |
| projects/*.jsonl | tool_result content | Medium |
| projects/*.jsonl | queue-operation content | High |

### Skills
| Location | Format | Reliability |
|----------|--------|-------------|
| projects/*.jsonl | `Skill` tool_use input | Very High |
| projects/*.jsonl | `.claude/skills/` paths in text | High |

---

## Metrics Extraction

### Token Usage
- Found in: `projects/*.jsonl` → assistant messages → `message.usage`
- Fields: `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`

### Cost
- Found in: `projects/*.jsonl` → assistant messages → `costUSD`
- Fallback: Calculate from tokens using model pricing

### Session Duration
- Found in: `projects/*.jsonl` → assistant messages → `durationMs`

### Tools Used
- Found in: `projects/*.jsonl` → assistant messages → `content[].type == "tool_use"` → `name`

---

## Agent File Mapping

### Two Types of "Agents"

1. **Claude Code Task Subagents** (`agent-{id}.jsonl` files)
   - Created when Claude uses the `Task` tool to spawn a subagent
   - File naming: `agent-{8-char-hex-id}.jsonl`
   - The agent TYPE (e.g., "Explore", "Plan") is in the **parent session's Task tool_use input**
   - The agent FILE only contains `agentId` field, NOT the agent type name

2. **Framework Agents** (`@agent-devops-engineer`, etc.)
   - Used by frameworks like agentic-engineering, ciign
   - Invoked via `@agent-name` syntax in user messages
   - NOT separate files - just mentions in conversation text

### Mapping Task Subagents to Types

To find what type a `agent-{id}.jsonl` represents:

1. Find the parent session file (same directory, UUID-named .jsonl)
2. Search for the agentId in `toolUseResult` blocks
3. The corresponding `tool_use` block with `name: "Task"` contains:
   - `input.subagent_type` - The agent type (e.g., "Explore", "Plan", "general-purpose")
   - `input.description` - Short description
   - `input.prompt` - The task given to the agent

Example mapping:
```
agent-453c91bb.jsonl  →  Found in parent: subagent_type="Explore"
agent-f1d05f44.jsonl  →  Found in parent: subagent_type="Explore"
```

### Agent File Schema

```json
{
  "parentUuid": "uuid-of-parent-message",
  "sessionId": "parent-session-uuid",
  "agentId": "453c91bb",
  "type": "user|assistant",
  "message": {...},
  "timestamp": "ISO-8601"
}
```

---

## Important Notes

1. **Session cleanup**: Claude Code deletes sessions older than 30 days by default. Set `cleanupPeriodDays` in settings to preserve longer.

2. **Project path encoding**: Directories use `-` to encode path separators: `/Users/pierre/project` → `-Users-pierre-project`

3. **Agent sessions**: Subagents create separate `agent-{id}.jsonl` files in the same project directory. The agent type is NOT in this file - it's in the parent session's Task tool call.

4. **Content formats**: `tool_result.content` can be either a string OR a list of `{type, text}` objects. Always handle both!

5. **Deduplication**: Same data may appear in multiple locations (history.jsonl, projects/, debug/) - choose the most structured source.

6. **Nested content**: Agent mentions (`@agent-*`) can appear in:
   - User text blocks
   - Assistant text blocks
   - tool_use input (Task prompts)
   - tool_result content (string OR list of {type, text})
   - queue-operation content

---

## Community Tools

| Tool | Purpose | Key Feature |
|------|---------|-------------|
| [claude-code-log](https://github.com/daaain/claude-code-log) | JSONL → HTML | Pydantic models, token tracking |
| [claude-history](https://github.com/thejud/claude-history) | JSONL → Markdown | Project path conversion |
| [claude-JSONL-browser](https://github.com/withLinda/claude-JSONL-browser) | Web viewer | File explorer UI |
| [claude-code-viewer](https://github.com/d-kimuson/claude-code-viewer) | Full web client | Interactive project management |
| [clog](https://github.com/HillviewCap/clog) | Log viewer | Simple CLI viewer |
