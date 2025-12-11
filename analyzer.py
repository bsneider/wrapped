#!/usr/bin/env python3
"""
Claude Wrapped Analyzer - The REAL One
Parses ~/.claude directory for comprehensive year-in-review metrics.
Beats Gemini's surface-level analysis by going DEEP.
"""

import json
import os
import re
import glob
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from typing import Optional
import hashlib


@dataclass
class SessionStats:
    """Stats for a single conversation session."""
    session_id: str
    project_path: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    message_count: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    total_cost_usd: float = 0.0
    total_duration_ms: int = 0
    tools_used: list = field(default_factory=list)
    models_used: set = field(default_factory=set)
    sidechain_count: int = 0
    summary_count: int = 0
    error_count: int = 0
    cwd_changes: list = field(default_factory=list)
    # New: Agent/skill/command tracking
    agents_used: list = field(default_factory=list)
    skills_used: list = field(default_factory=list)
    commands_used: list = field(default_factory=list)
    # Task subagent types (Explore, Plan, general-purpose, etc.)
    task_agent_types: list = field(default_factory=list)


@dataclass 
class ClaudeWrappedData:
    """All the data needed for Claude Wrapped."""
    # Basic stats
    total_sessions: int = 0
    total_messages: int = 0
    total_user_messages: int = 0
    total_assistant_messages: int = 0
    
    # Token economics
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cache_creation_tokens: int = 0
    total_cache_read_tokens: int = 0
    total_cost_usd: float = 0.0
    
    # Project explorer - top projects with detailed stats
    top_projects: list = field(default_factory=list)  # List of dicts with project stats
    
    # Developer personality (inspired by competitor)
    developer_personality: str = ""
    personality_description: str = ""
    coding_city: str = ""
    coding_city_description: str = ""
    
    # Time patterns
    hourly_distribution: dict = field(default_factory=lambda: defaultdict(int))
    daily_distribution: dict = field(default_factory=lambda: defaultdict(int))
    monthly_distribution: dict = field(default_factory=lambda: defaultdict(int))
    weekday_distribution: dict = field(default_factory=lambda: defaultdict(int))
    
    # Session patterns
    longest_session_duration_ms: int = 0
    longest_session_id: str = ""
    shortest_sessions: int = 0  # < 2 min sessions (rage quits)
    marathon_sessions: int = 0  # > 2 hour sessions
    average_session_duration_ms: float = 0.0
    
    # The Yapping Index
    user_to_assistant_token_ratio: float = 0.0
    
    # Cache efficiency
    cache_efficiency_ratio: float = 0.0
    
    # Tool usage
    tool_frequency: dict = field(default_factory=lambda: defaultdict(int))
    tool_chains: list = field(default_factory=list)
    
    # Model usage
    model_frequency: dict = field(default_factory=lambda: defaultdict(int))
    
    # Project chaos
    unique_projects: int = 0
    project_list: list = field(default_factory=list)
    most_active_project: str = ""
    most_active_project_sessions: int = 0
    abandoned_projects: list = field(default_factory=list)
    
    # Directory wandering
    unique_cwds: int = 0
    most_common_cwd: str = ""
    max_cwd_changes_in_session: int = 0
    
    # Sidechain stats
    total_sidechains: int = 0
    sidechain_ratio: float = 0.0
    
    # Error/apology stats
    total_errors: int = 0
    error_rate: float = 0.0
    
    # Context collapse (summaries = context was nuked)
    total_summaries: int = 0
    context_collapse_rate: float = 0.0
    
    # Version tracking
    versions_used: list = field(default_factory=list)
    
    # Todo graveyard
    total_todos_created: int = 0
    total_todos_completed: int = 0
    todo_completion_rate: float = 0.0
    orphan_agent_todos: int = 0
    
    # Statsig experiments
    feature_flags_exposed: int = 0
    experiments_participated: int = 0
    
    # Agent/Skill/Command usage
    agent_frequency: dict = field(default_factory=lambda: defaultdict(int))
    skill_frequency: dict = field(default_factory=lambda: defaultdict(int))
    command_frequency: dict = field(default_factory=lambda: defaultdict(int))
    top_agents: list = field(default_factory=list)
    top_skills: list = field(default_factory=list)
    top_commands: list = field(default_factory=list)

    # Task subagent types (Explore, Plan, general-purpose, etc.)
    task_agent_type_frequency: dict = field(default_factory=lambda: defaultdict(int))
    top_task_agent_types: list = field(default_factory=list)

    # Project groupings by common folder prefix
    project_groups: dict = field(default_factory=dict)  # {folder: [projects]}
    
    # Time extremes
    earliest_timestamp: Optional[str] = None
    latest_timestamp: Optional[str] = None
    latest_night_coding: Optional[str] = None  # Latest time coding (closest to midnight)
    earliest_morning_coding: Optional[str] = None  # Earliest morning time
    
    # Streaks
    longest_streak_days: int = 0
    current_streak_days: int = 0
    
    # Per-session data for charts
    sessions_by_date: dict = field(default_factory=lambda: defaultdict(int))
    tokens_by_date: dict = field(default_factory=lambda: defaultdict(int))
    cost_by_date: dict = field(default_factory=lambda: defaultdict(float))
    
    # Top sessions for highlights
    top_expensive_sessions: list = field(default_factory=list)
    top_long_sessions: list = field(default_factory=list)


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Parse ISO timestamp string to datetime."""
    if not ts_str:
        return None
    try:
        # Handle various ISO formats
        ts_str = ts_str.replace('Z', '+00:00')
        if '.' in ts_str:
            # Truncate microseconds if too long
            parts = ts_str.split('.')
            if len(parts) == 2:
                micro_and_tz = parts[1]
                if '+' in micro_and_tz:
                    micro, tz = micro_and_tz.split('+')
                    micro = micro[:6]
                    ts_str = f"{parts[0]}.{micro}+{tz}"
                elif '-' in micro_and_tz and micro_and_tz.index('-') > 0:
                    micro, tz = micro_and_tz.rsplit('-', 1)
                    micro = micro[:6]
                    ts_str = f"{parts[0]}.{micro}-{tz}"
        return datetime.fromisoformat(ts_str)
    except (ValueError, AttributeError):
        return None


def decode_project_path(encoded: str) -> str:
    """Decode the encoded project path from directory name.
    
    Pattern: -Users-username-folder-project-name becomes project-name
    
    The encoding replaces / with - but project names can also have dashes.
    We assume: /Users/username/[maybe-one-folder]/project-name-with-dashes
    
    Strategy:
    1. Remove leading dash
    2. Skip 'Users' or 'home' 
    3. Skip the username (next segment)
    4. Skip common parent folders (optional)
    5. Rejoin everything else with dashes (this is the project name)
    """
    if not encoded:
        return encoded
    
    # Handle worktree patterns first (e.g., project-worktree-feature-branch)
    if '-worktree-' in encoded.lower():
        parts = encoded.split('-worktree-')
        encoded = parts[0]  # Process the base part
    
    # Standard encoding: leading dash with dashes for slashes
    if not encoded.startswith('-'):
        return encoded
    
    # Remove leading dash and split
    parts = encoded[1:].split('-')
    
    if len(parts) < 3:
        return encoded  # Too short, return as-is
    
    # Skip system path prefixes
    start_idx = 0
    
    # Skip 'Users', 'home', 'root'
    if parts[0].lower() in ('users', 'home', 'root'):
        start_idx = 1
    
    # Skip the username (always the next element after Users/home)
    if start_idx < len(parts):
        start_idx += 1
    
    # Common parent folder names that are likely not part of the project name
    common_folders = {
        'projects', 'repos', 'code', 'src', 'dev', 'development', 
        'work', 'workspace', 'github', 'gitlab', 'bitbucket',
        'documents', 'desktop', 'downloads', 'go', 'rust', 'python'
    }
    
    # Skip ONE common folder if present (e.g., 'projects', 'repos')
    if start_idx < len(parts) and parts[start_idx].lower() in common_folders:
        start_idx += 1
    
    # Everything remaining is the project name (rejoined with dashes)
    if start_idx < len(parts):
        project_name = '-'.join(parts[start_idx:])
        return project_name
    
    return encoded


def get_project_display_name(path: str) -> str:
    """Get a clean display name for a project path."""
    if not path:
        return "Unknown"
    
    # If it looks like an already-decoded name (no leading dash, has dashes)
    if not path.startswith('-') and not path.startswith('/'):
        return path
    
    # If it's a full path with slashes
    if '/' in path:
        parts = path.rstrip('/').split('/')
        # Return last non-empty meaningful part
        for part in reversed(parts):
            if part and part.lower() not in ('users', 'home', 'root', 'projects', 'repos', 'code', 'src'):
                return part
        return parts[-1] if parts else path
    
    return path


def parse_jsonl_file(filepath: Path) -> list[dict]:
    """Parse a JSONL file, handling broken lines gracefully."""
    messages = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except json.JSONDecodeError:
                    # Skip malformed lines
                    pass
    except Exception as e:
        pass
    return messages


def detect_agents_only(text: str, stats: 'SessionStats') -> None:
    """Detect ONLY @agent- mentions in text.

    This is safe to run on tool_result content because @agent- prefix is very specific.
    """
    if not text:
        return
    agent_pattern = re.compile(r'@(agent-[a-zA-Z][a-zA-Z0-9_-]+)')
    agents = agent_pattern.findall(text)
    for agent in agents:
        # Skip the placeholder "@agent-name" from documentation
        if agent.lower() != 'agent-name':
            stats.agents_used.append(agent.lower())


def detect_invocations(text: str, stats: 'SessionStats') -> None:
    """Detect agent, skill, and command invocations in user text.

    Patterns to detect:
    - Commands: /command-name or /command (slash commands)
    - Agents: @agent-name mentions
    - Skills: Actual skill folder paths (.claude/skills/skill-name) or Skill tool invocations
    """
    if not text:
        return

    # Detect slash commands - ONLY real Claude Code commands, not API routes
    # Real commands are: /help, /compact, /clear, /doctor, /init, /config, /cost, /memory
    # OR namespaced custom commands like /project:command, /user:command, /gustav:planner
    # OR SlashCommand tool invocations

    # Known built-in Claude Code commands
    builtin_commands = {
        'help', 'compact', 'clear', 'doctor', 'init', 'config', 'cost', 'memory',
        'model', 'vim', 'terminal-setup', 'logout', 'login', 'permissions',
        'mcp', 'listen', 'pr-comments', 'review', 'hooks', 'bug', 'rewind',
        'resume', 'status', 'agents', 'commands', 'add-dir', 'install-github-app'
    }

    # Common API route patterns to EXCLUDE (false positives)
    api_routes = {
        'health', 'api', 'v1', 'v2', 'v3', 'auth', 'login', 'logout', 'users',
        'user', 'admin', 'app', 'apps', 'data', 'static', 'public', 'private',
        'context', 'upgrade', 'extra-usage', 'dashboard', 'analytics', 'metrics',
        'status', 'ping', 'ready', 'live', 'info', 'version', 'docs', 'swagger',
        'graphql', 'rest', 'callback', 'webhook', 'webhooks', 'events', 'socket',
        'ws', 'stream', 'upload', 'download', 'file', 'files', 'image', 'images',
        'asset', 'assets', 'media', 'search', 'query', 'filter', 'sort', 'page',
        'offer', 'portfolio', 'impact', 'collaboration', 'insights', 'exit',
        'trends', 'validate', 'stats', 'home', 'index', 'root'
    }

    # Pattern for commands at start of text (user actually typing a command)
    command_pattern = re.compile(r'^/([a-zA-Z][a-zA-Z0-9_:-]*)(?:\s|$)', re.MULTILINE)
    commands = command_pattern.findall(text)

    for cmd in commands:
        cmd_lower = cmd.lower()
        # Accept if:
        # 1. It's a known built-in command
        # 2. It contains ':' (namespaced custom command like /gustav:planner)
        # 3. It's NOT an API route pattern
        if cmd_lower in builtin_commands or ':' in cmd_lower:
            stats.commands_used.append(cmd_lower)
        elif cmd_lower not in api_routes and len(cmd_lower) > 2:
            # Unknown command but not an API route - might be custom
            stats.commands_used.append(cmd_lower)

    # Detect @agent- mentions ONLY (e.g., @agent-devops-engineer, @agent-frontend-specialist)
    # Real Claude Code agents use the @agent-name format from ciign/agentic-engineering
    # Exclude false positives like @babel, @types, @latest, @v3, @alpha (npm scopes/versions)
    detect_agents_only(text, stats)

    # Detect skill references - only match actual skill paths and Skill tool calls
    # Skills are model-invoked via .claude/skills/skill-name paths
    skill_patterns = [
        # Match .claude/skills/skill-name (most reliable)
        re.compile(r'\.claude/skills/([a-zA-Z][a-zA-Z0-9_-]+)'),
        # Match ~/.claude/skills/skill-name
        re.compile(r'~/\.claude/skills/([a-zA-Z][a-zA-Z0-9_-]+)'),
        # Match Skill tool invocation: skill: "skill-name" or skill: 'skill-name'
        re.compile(r'"skill"\s*:\s*"([a-zA-Z][a-zA-Z0-9_-]+)"'),
        re.compile(r'"skill"\s*:\s*\'([a-zA-Z][a-zA-Z0-9_-]+)\''),
        # Match SKILL.md references (skill name is parent folder)
        re.compile(r'/([a-zA-Z][a-zA-Z0-9_-]+)/SKILL\.md'),
    ]
    for pattern in skill_patterns:
        skills = pattern.findall(text)
        for skill in skills:
            stats.skills_used.append(skill.lower())


def analyze_session(messages: list[dict], session_id: str, project_path: str) -> SessionStats:
    """Analyze a single session's messages."""
    stats = SessionStats(session_id=session_id, project_path=project_path)
    
    timestamps = []
    cwds = []
    tool_sequence = []
    
    for msg in messages:
        stats.message_count += 1
        
        # Get timestamp
        ts = parse_timestamp(msg.get('timestamp', ''))
        if ts:
            timestamps.append(ts)
        
        # Get type
        msg_type = msg.get('type', '')
        
        if msg_type == 'user':
            stats.user_messages += 1

            # Detect agent/skill/command invocations from user text
            user_content = msg.get('message', {})
            if isinstance(user_content, dict):
                content_blocks = user_content.get('content', [])
                if isinstance(content_blocks, list):
                    for block in content_blocks:
                        if isinstance(block, dict):
                            block_type = block.get('type', '')
                            # Check text blocks from user input (for all invocations)
                            if block_type == 'text':
                                text = block.get('text', '')
                                detect_invocations(text, stats)
                            # Also check tool_result content ONLY for @agent- mentions
                            # (safe because @agent- prefix is very specific)
                            elif block_type == 'tool_result':
                                result_content = block.get('content', '')
                                # Content can be string or list of dicts
                                if isinstance(result_content, str):
                                    if '@agent-' in result_content:
                                        detect_agents_only(result_content, stats)
                                elif isinstance(result_content, list):
                                    for item in result_content:
                                        if isinstance(item, dict):
                                            item_text = item.get('text', '')
                                            if isinstance(item_text, str) and '@agent-' in item_text:
                                                detect_agents_only(item_text, stats)
                                        elif isinstance(item, str) and '@agent-' in item:
                                            detect_agents_only(item, stats)
                elif isinstance(content_blocks, str):
                    detect_invocations(content_blocks, stats)
            elif isinstance(user_content, str):
                detect_invocations(user_content, stats)

        elif msg_type == 'queue-operation':
            # Queue operations contain agent invocations
            queue_content = msg.get('content', '')
            if isinstance(queue_content, str):
                detect_invocations(queue_content, stats)
        elif msg_type == 'assistant':
            stats.assistant_messages += 1
            
            # Extract assistant message details
            inner_msg = msg.get('message', {})
            
            # Model tracking
            model = inner_msg.get('model', '')
            if model and model != '<synthetic>':
                stats.models_used.add(model)
            
            # Token usage
            usage = inner_msg.get('usage', {})
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)
            cache_creation = usage.get('cache_creation_input_tokens', 0)
            cache_read = usage.get('cache_read_input_tokens', 0)
            
            stats.total_input_tokens += input_tokens
            stats.total_output_tokens += output_tokens
            stats.cache_creation_tokens += cache_creation
            stats.cache_read_tokens += cache_read
            
            # Cost tracking - use costUSD if present, otherwise calculate from tokens
            cost = msg.get('costUSD', 0)
            if cost:
                stats.total_cost_usd += float(cost)
            elif input_tokens or output_tokens:
                # Calculate cost from tokens using comprehensive model pricing
                # Pricing per 1M tokens (as of December 2025):
                model = inner_msg.get('model', '').lower()
                
                # Opus family
                if 'opus-4-5' in model or 'opus-4.5' in model:
                    # Opus 4.5: $5/$25 per 1M tokens
                    input_price = 5.0 / 1_000_000
                    output_price = 25.0 / 1_000_000
                    cache_write_price = 6.25 / 1_000_000  # 1.25x input
                    cache_read_price = 0.50 / 1_000_000   # 0.1x input
                elif 'opus-4-1' in model or 'opus-4.1' in model or 'opus-4' in model:
                    # Opus 4/4.1: $15/$75 per 1M tokens
                    input_price = 15.0 / 1_000_000
                    output_price = 75.0 / 1_000_000
                    cache_write_price = 18.75 / 1_000_000
                    cache_read_price = 1.50 / 1_000_000
                elif 'opus' in model:
                    # Older Opus (3.x): $15/$75 per 1M tokens
                    input_price = 15.0 / 1_000_000
                    output_price = 75.0 / 1_000_000
                    cache_write_price = 18.75 / 1_000_000
                    cache_read_price = 1.50 / 1_000_000
                    
                # Haiku family
                elif 'haiku-4-5' in model or 'haiku-4.5' in model:
                    # Haiku 4.5: $1/$5 per 1M tokens
                    input_price = 1.0 / 1_000_000
                    output_price = 5.0 / 1_000_000
                    cache_write_price = 1.25 / 1_000_000
                    cache_read_price = 0.10 / 1_000_000
                elif 'haiku-3-5' in model or 'haiku-3.5' in model:
                    # Haiku 3.5: $0.80/$4 per 1M tokens
                    input_price = 0.80 / 1_000_000
                    output_price = 4.0 / 1_000_000
                    cache_write_price = 1.0 / 1_000_000
                    cache_read_price = 0.08 / 1_000_000
                elif 'haiku' in model:
                    # Haiku 3: $0.25/$1.25 per 1M tokens
                    input_price = 0.25 / 1_000_000
                    output_price = 1.25 / 1_000_000
                    cache_write_price = 0.30 / 1_000_000
                    cache_read_price = 0.03 / 1_000_000
                    
                # Sonnet family (default)
                elif 'sonnet-4-5' in model or 'sonnet-4.5' in model:
                    # Sonnet 4.5: $3/$15 per 1M tokens
                    input_price = 3.0 / 1_000_000
                    output_price = 15.0 / 1_000_000
                    cache_write_price = 3.75 / 1_000_000
                    cache_read_price = 0.30 / 1_000_000
                elif 'sonnet-3-7' in model or 'sonnet-3.7' in model:
                    # Sonnet 3.7: $3/$15 per 1M tokens
                    input_price = 3.0 / 1_000_000
                    output_price = 15.0 / 1_000_000
                    cache_write_price = 3.75 / 1_000_000
                    cache_read_price = 0.30 / 1_000_000
                else:
                    # Default to Sonnet 4 pricing: $3/$15 per 1M tokens
                    input_price = 3.0 / 1_000_000
                    output_price = 15.0 / 1_000_000
                    cache_write_price = 3.75 / 1_000_000
                    cache_read_price = 0.30 / 1_000_000
                
                calculated_cost = (
                    input_tokens * input_price +
                    output_tokens * output_price +
                    cache_creation * cache_write_price +
                    cache_read * cache_read_price
                )
                stats.total_cost_usd += calculated_cost
            
            # Duration tracking
            duration = msg.get('durationMs', 0)
            if duration:
                stats.total_duration_ms += int(duration)
            
            # Tool usage and content analysis
            content = inner_msg.get('content', [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        block_type = block.get('type', '')

                        # Check assistant text blocks for agent mentions
                        if block_type == 'text':
                            text = block.get('text', '')
                            if '@agent-' in text:
                                detect_agents_only(text, stats)

                        # Tool usage tracking
                        if block_type == 'tool_use':
                            tool_name = block.get('name', 'unknown')
                            stats.tools_used.append(tool_name)
                            tool_sequence.append(tool_name)
                            tool_input = block.get('input', {})

                            # Check tool_use input for agent mentions (e.g., Task tool prompts)
                            if isinstance(tool_input, dict):
                                input_str = json.dumps(tool_input)
                                if '@agent-' in input_str:
                                    detect_agents_only(input_str, stats)

                            # Detect Skill tool invocations to track skills used
                            if tool_name == 'Skill':
                                skill_name = tool_input.get('skill', '')
                                if skill_name:
                                    stats.skills_used.append(skill_name.lower())

                            # Detect SlashCommand tool invocations to track commands used
                            if tool_name == 'SlashCommand':
                                command = tool_input.get('command', '')
                                if command and command.startswith('/'):
                                    # Extract command name (e.g., "/gustav:planner" -> "gustav:planner")
                                    cmd_parts = command[1:].split()
                                    if cmd_parts:
                                        stats.commands_used.append(cmd_parts[0].lower())

                            # Detect Task tool invocations to track subagent types
                            if tool_name == 'Task':
                                subagent_type = tool_input.get('subagent_type', '')
                                if subagent_type:
                                    stats.task_agent_types.append(subagent_type.lower())
            
            # Error tracking
            if msg.get('isApiErrorMessage') or inner_msg.get('model') == '<synthetic>':
                stats.error_count += 1
                
        elif msg_type == 'summary':
            stats.summary_count += 1
        
        # Sidechain tracking
        if msg.get('isSidechain'):
            stats.sidechain_count += 1
        
        # CWD tracking
        cwd = msg.get('cwd', '')
        if cwd and (not cwds or cwds[-1] != cwd):
            cwds.append(cwd)
    
    # Calculate session time bounds
    if timestamps:
        timestamps.sort()
        stats.start_time = timestamps[0]
        stats.end_time = timestamps[-1]
    
    stats.cwd_changes = cwds
    
    return stats


def analyze_todos(claude_dir: Path) -> dict:
    """Analyze the todos directory for task completion metrics."""
    todos_dir = claude_dir / 'todos'
    results = {
        'total_created': 0,
        'total_completed': 0,
        'total_pending': 0,
        'total_in_progress': 0,
        'orphan_agent_todos': 0,
        'total_files': 0
    }
    
    if not todos_dir.exists():
        return results
    
    for todo_file in todos_dir.glob('*.json'):
        results['total_files'] += 1
        
        # Check if it's an agent todo
        is_agent_todo = '-agent-' in todo_file.name
        
        try:
            with open(todo_file, 'r') as f:
                todos = json.load(f)
                
            if isinstance(todos, list):
                for todo in todos:
                    results['total_created'] += 1
                    status = todo.get('status', 'pending')
                    if status == 'completed':
                        results['total_completed'] += 1
                    elif status == 'in_progress':
                        results['total_in_progress'] += 1
                    else:
                        results['total_pending'] += 1
                        
                # If agent todo with no completed items, it's orphaned
                if is_agent_todo and not any(t.get('status') == 'completed' for t in todos):
                    results['orphan_agent_todos'] += 1
                    
        except (json.JSONDecodeError, Exception):
            pass
    
    return results


def analyze_statsig(claude_dir: Path) -> dict:
    """Analyze statsig directory for feature flag exposure."""
    statsig_dir = claude_dir / 'statsig'
    results = {
        'feature_flags': 0,
        'experiments': 0,
        'stable_id': None,
        'session_count': 0
    }
    
    if not statsig_dir.exists():
        return results
    
    # Look for cached evaluations
    for eval_file in statsig_dir.glob('statsig.cached.evaluations.*'):
        try:
            with open(eval_file, 'r') as f:
                data = json.load(f)
            
            # Count feature gates
            if 'feature_gates' in data:
                results['feature_flags'] = len(data['feature_gates'])
            
            # Count dynamic configs (experiments)
            if 'dynamic_configs' in data:
                results['experiments'] = len(data['dynamic_configs'])
                
        except (json.JSONDecodeError, Exception):
            pass
    
    # Get stable ID
    for stable_file in statsig_dir.glob('statsig.stable_id.*'):
        try:
            with open(stable_file, 'r') as f:
                results['stable_id'] = f.read().strip().strip('"')
        except Exception:
            pass
    
    return results


def calculate_streaks(dates: list[datetime]) -> tuple[int, int]:
    """Calculate longest and current streak of consecutive days."""
    if not dates:
        return 0, 0
    
    # Get unique dates (just the date part)
    unique_dates = sorted(set(d.date() for d in dates))
    
    if not unique_dates:
        return 0, 0
    
    longest_streak = 1
    current_streak = 1
    streak = 1
    
    for i in range(1, len(unique_dates)):
        if (unique_dates[i] - unique_dates[i-1]).days == 1:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 1
    
    # Check current streak (from most recent date)
    today = datetime.now().date()
    if unique_dates[-1] == today or unique_dates[-1] == today - timedelta(days=1):
        current_streak = 1
        for i in range(len(unique_dates) - 2, -1, -1):
            if (unique_dates[i+1] - unique_dates[i]).days == 1:
                current_streak += 1
            else:
                break
    else:
        current_streak = 0
    
    return longest_streak, current_streak


def find_tool_chains(sessions: list[SessionStats], min_length: int = 3) -> list[tuple]:
    """Find common tool usage patterns."""
    chain_counter = Counter()
    
    for session in sessions:
        tools = session.tools_used
        if len(tools) >= min_length:
            # Look for repeated patterns
            for i in range(len(tools) - min_length + 1):
                chain = tuple(tools[i:i + min_length])
                chain_counter[chain] += 1
    
    # Return top 10 most common chains
    return chain_counter.most_common(10)


def determine_developer_personality(data: 'ClaudeWrappedData') -> tuple[str, str]:
    """Determine developer personality based on usage patterns."""
    
    tool_freq = data.tool_frequency
    total_tools = sum(tool_freq.values()) if tool_freq else 0
    
    # Analyze patterns
    read_heavy = tool_freq.get('Read', 0) > tool_freq.get('Edit', 0) * 1.5 if tool_freq else False
    edit_heavy = tool_freq.get('Edit', 0) > tool_freq.get('Read', 0) * 1.5 if tool_freq else False
    bash_heavy = tool_freq.get('Bash', 0) > total_tools * 0.2 if total_tools else False
    
    # Night owl vs early bird
    hour_dist = data.hourly_distribution
    night_activity = sum(hour_dist.get(h, hour_dist.get(str(h), 0)) for h in range(22, 24)) + \
                    sum(hour_dist.get(h, hour_dist.get(str(h), 0)) for h in range(0, 5))
    morning_activity = sum(hour_dist.get(h, hour_dist.get(str(h), 0)) for h in range(5, 10))
    total_activity = sum(hour_dist.values()) if hour_dist else 1
    
    is_night_owl = night_activity > total_activity * 0.15
    is_early_bird = morning_activity > total_activity * 0.2
    
    # Marathon vs sprinter
    is_marathoner = data.marathon_sessions > data.shortest_sessions
    
    # Calculate chaos factor
    chaos_factor = (data.total_errors + data.total_summaries + len(data.abandoned_projects)) / max(data.total_sessions, 1)
    
    # Determine personality
    if is_night_owl and is_marathoner:
        return "The Night Architect", "You build empires while the world sleeps. Long sessions, deep focus, questionable sleep schedule."
    elif is_early_bird and read_heavy:
        return "The Morning Scholar", "Up with the sun, reading code before coffee. You understand before you modify."
    elif bash_heavy and edit_heavy:
        return "The Terminal Wizard", "Command line is your canvas. You speak fluent Bash and think in pipes."
    elif chaos_factor > 0.5:
        return "The Chaos Pilot", "Context collapses? Abandoned projects? Errors? You thrive in entropy. Somehow, it ships."
    elif data.cache_efficiency_ratio > 0.7:
        return "The Efficiency Expert", "Your context reuse is legendary. Every token counts. Your API bill thanks you."
    elif data.sidechain_ratio > 0.1:
        return "The Parallel Processor", "You let Claude go rogue on sidechains. Delegation is your superpower."
    elif is_marathoner:
        return "The Deep Diver", "When you start a session, you COMMIT. Marathon sessions, massive context, no distractions."
    elif data.unique_projects > 10:
        return "The Project Juggler", "So many projects, so little time. You context-switch like a caffeinated octopus."
    else:
        return "The Balanced Builder", "Steady and consistent. You've found your rhythm with Claude."


def determine_coding_city(data: 'ClaudeWrappedData') -> tuple[str, str]:
    """Match user to a coding city based on their patterns (inspired by Spotify's Sound Town)."""
    
    # Analyze patterns
    hour_dist = data.hourly_distribution
    total_activity = sum(hour_dist.values()) if hour_dist else 1
    
    # Find peak hour
    peak_hour = 12  # default
    if hour_dist:
        peak_hour = max(hour_dist.keys(), key=lambda h: hour_dist.get(h, hour_dist.get(str(h), 0)))
        if isinstance(peak_hour, str):
            peak_hour = int(peak_hour)
    
    # Time period analysis
    late_night = sum(hour_dist.get(h, hour_dist.get(str(h), 0)) for h in range(0, 5))
    early_morning = sum(hour_dist.get(h, hour_dist.get(str(h), 0)) for h in range(5, 9))
    morning = sum(hour_dist.get(h, hour_dist.get(str(h), 0)) for h in range(9, 12))
    afternoon = sum(hour_dist.get(h, hour_dist.get(str(h), 0)) for h in range(12, 17))
    evening = sum(hour_dist.get(h, hour_dist.get(str(h), 0)) for h in range(17, 21))
    night = sum(hour_dist.get(h, hour_dist.get(str(h), 0)) for h in range(21, 24))
    
    # Calculate percentages
    night_pct = (late_night + night) / max(total_activity, 1)
    morning_pct = early_morning / max(total_activity, 1)
    afternoon_pct = afternoon / max(total_activity, 1)
    evening_pct = evening / max(total_activity, 1)
    
    # Intensity
    sessions_per_project = data.total_sessions / max(data.unique_projects, 1)
    
    # Weekday patterns
    weekday_dist = data.weekday_distribution
    weekend_activity = weekday_dist.get('Saturday', 0) + weekday_dist.get('Sunday', 0)
    weekday_activity = sum(weekday_dist.get(d, 0) for d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    weekend_ratio = weekend_activity / max(weekday_activity + weekend_activity, 1)
    
    # Determine city based on PRIMARY pattern (most sessions)
    # First check if they're a true night owl (peak at midnight-5am)
    if peak_hour >= 0 and peak_hour < 5:
        return "Tokyo, Japan 🇯🇵", f"Peak coding at {peak_hour}:00 AM! The city that never sleeps matches your true nocturnal nature."
    
    # True early bird (peak 5-8am)
    elif peak_hour >= 5 and peak_hour < 9:
        return "Stockholm, Sweden 🇸🇪", f"Peak coding at {peak_hour}:00 AM! Early risers unite. Fika-fueled productivity."
    
    # Night coder (peak 9pm-midnight) 
    elif peak_hour >= 21:
        return "Berlin, Germany 🇩🇪", f"Peak coding at {peak_hour}:00. Evening sessions fuel your creativity, techno-club style."
    
    # Weekend warrior
    elif weekend_ratio > 0.35:
        return "Austin, TX 🇺🇸", "Weekend coding dominance! Keep Austin weird, ship on Saturday."
    
    # Heavy afternoon worker (classic 9-5 extended)
    elif afternoon_pct > 0.35:
        return "New York, NY 🇺🇸", f"Peak at {peak_hour}:00. Classic grind hours. Wall Street work ethic, Silicon Alley results."
    
    # High project count = startup energy
    elif data.unique_projects > 15:
        return "San Francisco, CA 🇺🇸", "So many projects! Startup energy. You've got that Bay Area hustle."
    
    # Cache efficiency = precision
    elif data.cache_efficiency_ratio > 0.7:
        return "Zurich, Switzerland 🇨🇭", "Precision and efficiency. Your optimized workflows match Swiss engineering excellence."
    
    # High spender
    elif data.total_cost_usd > 100:
        return "Singapore 🇸🇬", "High investment, high returns. Your API spend matches Singapore's premium tech scene."
    
    # Marathon sessions
    elif data.marathon_sessions > 5:
        return "Seoul, South Korea 🇰🇷", "Marathon session master. Your dedication matches Korea's PC bang culture."
    
    # Evening coder
    elif evening_pct > 0.3:
        return "Tel Aviv, Israel 🇮🇱", f"Peak at {peak_hour}:00. Evening hustle, startup nation energy. Ship it!"
    
    # Default
    else:
        return "London, UK 🇬🇧", f"Peak at {peak_hour}:00. Steady, professional, getting things done. Classic efficiency."


def build_top_projects(project_sessions: dict, limit: int = 10) -> list[dict]:
    """Build a list of top projects with detailed stats."""
    project_stats = []
    
    for project_path, sessions in project_sessions.items():
        total_messages = sum(s.message_count for s in sessions)
        total_tokens = sum(s.total_input_tokens + s.total_output_tokens for s in sessions)
        total_cost = sum(s.total_cost_usd for s in sessions)
        
        # Get time range
        start_times = [s.start_time for s in sessions if s.start_time]
        end_times = [s.end_time for s in sessions if s.end_time]
        
        first_session = min(start_times).isoformat() if start_times else None
        last_session = max(end_times).isoformat() if end_times else None
        
        project_stats.append({
            'name': get_project_display_name(project_path),
            'full_path': project_path,
            'sessions': len(sessions),
            'messages': total_messages,
            'tokens': total_tokens,
            'cost': total_cost,
            'first_session': first_session,
            'last_session': last_session,
        })
    
    # Sort by sessions (most active first)
    project_stats.sort(key=lambda x: x['sessions'], reverse=True)
    
    return project_stats[:limit]


def analyze_claude_directory(claude_dir: Path) -> ClaudeWrappedData:
    """Main analysis function - parses entire ~/.claude directory."""
    data = ClaudeWrappedData()
    
    if not claude_dir.exists():
        return data
    
    # Collect all sessions
    all_sessions: list[SessionStats] = []
    all_timestamps: list[datetime] = []
    project_sessions: dict[str, list[SessionStats]] = defaultdict(list)
    all_cwds: list[str] = []
    
    # Find all JSONL files in projects directory
    projects_dir = claude_dir / 'projects'
    if projects_dir.exists():
        for jsonl_file in projects_dir.glob('**/*.jsonl'):
            # Extract project path from parent directory
            parent = jsonl_file.parent.name
            project_path = decode_project_path(parent) if parent != 'projects' else 'root'
            session_id = jsonl_file.stem
            
            messages = parse_jsonl_file(jsonl_file)
            if messages:
                session = analyze_session(messages, session_id, project_path)
                all_sessions.append(session)
                project_sessions[project_path].append(session)
                
                if session.start_time:
                    all_timestamps.append(session.start_time)
                if session.end_time:
                    all_timestamps.append(session.end_time)
                
                all_cwds.extend(session.cwd_changes)
    
    # Also check root-level JSONL files
    for jsonl_file in claude_dir.glob('*.jsonl'):
        if jsonl_file.name != 'history.jsonl':
            session_id = jsonl_file.stem
            messages = parse_jsonl_file(jsonl_file)
            if messages:
                session = analyze_session(messages, session_id, 'root')
                all_sessions.append(session)
                project_sessions['root'].append(session)
    
    # Check history.jsonl - has different format with 'display' field
    history_file = claude_dir / 'history.jsonl'
    if history_file.exists():
        history_messages = parse_jsonl_file(history_file)
        # Create a dummy session to aggregate history data
        history_stats = SessionStats(session_id='global-history', project_path='global')
        for msg in history_messages:
            # History entries have 'display' field with user input
            display_text = msg.get('display', '')
            if display_text:
                detect_invocations(display_text, history_stats)
        all_sessions.append(history_stats)
    
    # Aggregate stats
    data.total_sessions = len(all_sessions)
    
    session_durations = []
    
    for session in all_sessions:
        data.total_messages += session.message_count
        data.total_user_messages += session.user_messages
        data.total_assistant_messages += session.assistant_messages
        data.total_input_tokens += session.total_input_tokens
        data.total_output_tokens += session.total_output_tokens
        data.total_cache_creation_tokens += session.cache_creation_tokens
        data.total_cache_read_tokens += session.cache_read_tokens
        data.total_cost_usd += session.total_cost_usd
        data.total_sidechains += session.sidechain_count
        data.total_summaries += session.summary_count
        data.total_errors += session.error_count
        
        # Tool frequency
        for tool in session.tools_used:
            data.tool_frequency[tool] += 1
        
        # Model frequency
        for model in session.models_used:
            data.model_frequency[model] += 1
        
        # Agent/Skill/Command frequency
        for agent in session.agents_used:
            data.agent_frequency[agent] += 1
        for skill in session.skills_used:
            data.skill_frequency[skill] += 1
        for command in session.commands_used:
            data.command_frequency[command] += 1
        # Task agent type frequency
        for agent_type in session.task_agent_types:
            data.task_agent_type_frequency[agent_type] += 1
        
        # Session duration
        if session.start_time and session.end_time:
            duration_ms = (session.end_time - session.start_time).total_seconds() * 1000
            session_durations.append((duration_ms, session.session_id, session.project_path))
            
            if duration_ms > data.longest_session_duration_ms:
                data.longest_session_duration_ms = duration_ms
                data.longest_session_id = session.session_id
            
            # Count rage quits (< 2 min) and marathons (> 2 hours)
            if duration_ms < 120000:  # 2 minutes
                data.shortest_sessions += 1
            if duration_ms > 7200000:  # 2 hours
                data.marathon_sessions += 1
        
        # CWD changes
        if len(session.cwd_changes) > data.max_cwd_changes_in_session:
            data.max_cwd_changes_in_session = len(session.cwd_changes)
        
        # Time distributions
        if session.start_time:
            hour = session.start_time.hour
            data.hourly_distribution[hour] += 1
            
            weekday = session.start_time.strftime('%A')
            data.weekday_distribution[weekday] += 1
            
            date_str = session.start_time.strftime('%Y-%m-%d')
            data.sessions_by_date[date_str] += 1
            data.tokens_by_date[date_str] += session.total_input_tokens + session.total_output_tokens
            data.cost_by_date[date_str] += session.total_cost_usd
            
            month_str = session.start_time.strftime('%Y-%m')
            data.monthly_distribution[month_str] += 1
    
    # Calculate averages and ratios
    if session_durations:
        data.average_session_duration_ms = sum(d[0] for d in session_durations) / len(session_durations)
        
        # Top expensive and long sessions
        session_costs = [(s.total_cost_usd, s.session_id, s.project_path) for s in all_sessions if s.total_cost_usd > 0]
        session_costs.sort(reverse=True)
        data.top_expensive_sessions = session_costs[:5]
        
        session_durations.sort(reverse=True)
        data.top_long_sessions = session_durations[:5]
    
    # Yapping index (user tokens / assistant tokens)
    if data.total_output_tokens > 0:
        data.user_to_assistant_token_ratio = data.total_input_tokens / data.total_output_tokens
    
    # Cache efficiency
    total_cache = data.total_cache_creation_tokens + data.total_cache_read_tokens
    if total_cache > 0:
        data.cache_efficiency_ratio = data.total_cache_read_tokens / total_cache
    
    # Sidechain ratio
    if data.total_messages > 0:
        data.sidechain_ratio = data.total_sidechains / data.total_messages
    
    # Error rate
    if data.total_assistant_messages > 0:
        data.error_rate = data.total_errors / data.total_assistant_messages
    
    # Context collapse rate
    if data.total_sessions > 0:
        data.context_collapse_rate = data.total_summaries / data.total_sessions
    
    # Project stats
    data.unique_projects = len(project_sessions)
    data.project_list = list(project_sessions.keys())
    
    if project_sessions:
        most_active = max(project_sessions.items(), key=lambda x: len(x[1]))
        data.most_active_project = most_active[0]
        data.most_active_project_sessions = len(most_active[1])
        
        # Find abandoned projects (no sessions in last 30 days)
        from datetime import timezone
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        for project, sessions in project_sessions.items():
            latest = max((s.end_time for s in sessions if s.end_time), default=None)
            if latest:
                # Make comparison timezone-aware safe
                if latest.tzinfo is None:
                    latest = latest.replace(tzinfo=timezone.utc)
                if latest < thirty_days_ago:
                    data.abandoned_projects.append(project)
    
    # CWD stats
    cwd_counter = Counter(all_cwds)
    data.unique_cwds = len(cwd_counter)
    if cwd_counter:
        data.most_common_cwd = cwd_counter.most_common(1)[0][0]
    
    # Version tracking
    versions = set()
    for session in all_sessions:
        # Would need to extract from messages, simplified here
        pass
    data.versions_used = list(versions)
    
    # Time extremes
    if all_timestamps:
        all_timestamps.sort()
        data.earliest_timestamp = all_timestamps[0].isoformat()
        data.latest_timestamp = all_timestamps[-1].isoformat()
        
        # Find latest night coding (closest to midnight)
        night_times = [t for t in all_timestamps if t.hour >= 22 or t.hour <= 4]
        if night_times:
            # Sort by how close to midnight
            def midnight_distance(t):
                if t.hour >= 22:
                    return 24 - t.hour
                return t.hour
            latest_night = min(night_times, key=midnight_distance)
            data.latest_night_coding = latest_night.strftime('%H:%M')
        
        # Find earliest morning coding
        morning_times = [t for t in all_timestamps if 4 <= t.hour <= 8]
        if morning_times:
            earliest_morning = min(morning_times, key=lambda t: t.hour * 60 + t.minute)
            data.earliest_morning_coding = earliest_morning.strftime('%H:%M')
    
    # Calculate streaks
    data.longest_streak_days, data.current_streak_days = calculate_streaks(all_timestamps)
    
    # Tool chains
    data.tool_chains = find_tool_chains(all_sessions)
    
    # Build top projects list
    data.top_projects = build_top_projects(project_sessions)
    
    # Build top agents/skills/commands lists
    data.top_agents = sorted(data.agent_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    data.top_skills = sorted(data.skill_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    data.top_commands = sorted(data.command_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
    data.top_task_agent_types = sorted(data.task_agent_type_frequency.items(), key=lambda x: x[1], reverse=True)[:10]

    # Group projects by common folder prefix
    # Projects with the same first word (folder name) are grouped together
    folder_projects = defaultdict(list)
    for proj in data.top_projects:
        name = proj.get('name', '')
        # Split on dashes or underscores to find the folder prefix
        parts = name.replace('_', '-').split('-')
        if len(parts) > 1:
            folder = parts[0].lower()
            # Only group if it's a meaningful folder name (not short/generic)
            if len(folder) >= 3 and folder not in ('the', 'new', 'my', 'old', 'tmp', 'test'):
                folder_projects[folder].append(name)
            else:
                folder_projects[name.lower()].append(name)
        else:
            folder_projects[name.lower()].append(name)

    # Only keep folder groups with more than 1 project
    data.project_groups = {
        folder: projects for folder, projects in folder_projects.items()
        if len(projects) > 1
    }
    
    # Analyze todos
    todo_stats = analyze_todos(claude_dir)
    data.total_todos_created = todo_stats['total_created']
    data.total_todos_completed = todo_stats['total_completed']
    if data.total_todos_created > 0:
        data.todo_completion_rate = data.total_todos_completed / data.total_todos_created
    data.orphan_agent_todos = todo_stats['orphan_agent_todos']
    
    # Analyze statsig
    statsig_stats = analyze_statsig(claude_dir)
    data.feature_flags_exposed = statsig_stats['feature_flags']
    data.experiments_participated = statsig_stats['experiments']
    
    # Determine developer personality and coding city
    data.developer_personality, data.personality_description = determine_developer_personality(data)
    data.coding_city, data.coding_city_description = determine_coding_city(data)
    
    return data


def to_json_serializable(data: ClaudeWrappedData) -> dict:
    """Convert dataclass to JSON-serializable dict."""
    result = {}
    for key, value in asdict(data).items():
        if isinstance(value, defaultdict):
            result[key] = dict(value)
        elif isinstance(value, set):
            result[key] = list(value)
        else:
            result[key] = value
    return result


def main():
    """Main entry point."""
    import sys
    
    # Default to ~/.claude but allow override
    claude_dir = Path(os.path.expanduser('~/.claude'))
    if len(sys.argv) > 1:
        claude_dir = Path(sys.argv[1])
    
    print(f"🔍 Analyzing {claude_dir}...")
    
    data = analyze_claude_directory(claude_dir)
    
    # Output JSON
    output = to_json_serializable(data)
    print(json.dumps(output, indent=2, default=str))
    
    return output


if __name__ == '__main__':
    main()
