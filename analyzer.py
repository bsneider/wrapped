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
    """Decode the encoded project path from directory name."""
    # -Users-foo-bar becomes /Users/foo/bar
    if encoded.startswith('-'):
        return encoded.replace('-', '/')
    return encoded


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
            stats.total_input_tokens += usage.get('input_tokens', 0)
            stats.total_output_tokens += usage.get('output_tokens', 0)
            stats.cache_creation_tokens += usage.get('cache_creation_input_tokens', 0)
            stats.cache_read_tokens += usage.get('cache_read_input_tokens', 0)
            
            # Cost tracking
            cost = msg.get('costUSD', 0)
            if cost:
                stats.total_cost_usd += float(cost)
            
            # Duration tracking
            duration = msg.get('durationMs', 0)
            if duration:
                stats.total_duration_ms += int(duration)
            
            # Tool usage
            content = inner_msg.get('content', [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'tool_use':
                        tool_name = block.get('name', 'unknown')
                        stats.tools_used.append(tool_name)
                        tool_sequence.append(tool_name)
            
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
    
    # Check history.jsonl
    history_file = claude_dir / 'history.jsonl'
    if history_file.exists():
        messages = parse_jsonl_file(history_file)
        if messages:
            session = analyze_session(messages, 'global-history', 'global')
            all_sessions.append(session)
    
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
        thirty_days_ago = datetime.now() - timedelta(days=30)
        for project, sessions in project_sessions.items():
            latest = max((s.end_time for s in sessions if s.end_time), default=None)
            if latest and latest < thirty_days_ago:
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
