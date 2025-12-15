# Claude Folder Data Analysis Skill

Use this skill when analyzing Claude Code's local data storage in `~/.claude/`.

## When to Use

- Parsing JSONL session files
- Extracting usage statistics (tokens, costs, sessions)
- Finding user invocations (commands, agents, skills)
- Understanding file relationships and data flow

## Key Knowledge

### File Locations
- `~/.claude/history.jsonl` - Global user input history
- `~/.claude/projects/{path}/*.jsonl` - Per-project conversations
- `~/.claude/projects/{path}/agent-{id}.jsonl` - Subagent sessions
- `~/.claude/todos/*.json` - Task lists
- `~/.claude/debug/*.txt` - Raw transcripts

### Critical Parsing Details

1. **Content can be string OR list**:
   ```python
   # tool_result.content can be:
   "string content"
   # OR
   [{"type": "text", "text": "content"}]
   ```

2. **Agent mentions appear in multiple places**:
   - User text blocks
   - Assistant text blocks
   - tool_use input (Task prompts)
   - tool_result content
   - queue-operation content

3. **Agent files don't contain agent type**:
   - `agent-{id}.jsonl` only has `agentId` field
   - Agent type is in parent session's `Task` tool_use `input.subagent_type`

4. **Two types of "agents"**:
   - Task subagents: `agent-{id}.jsonl` files
   - Framework agents: `@agent-name` mentions (no separate files)

### Data Extraction Patterns

```python
# Token usage
msg['message']['usage']['input_tokens']
msg['message']['usage']['output_tokens']

# Cost
msg.get('costUSD', 0)

# Model
msg['message']['model']

# Tool usage
for block in msg['message']['content']:
    if block['type'] == 'tool_use':
        tool_name = block['name']
```

## Reference

See `CLAUDE_DATA_SCHEMA.md` in this skill folder for complete schema documentation.
