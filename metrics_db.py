#!/usr/bin/env python3
"""
SQLite database for storing Claude Wrapped metrics history.
Tracks metrics over time to show trends and changes.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


DB_PATH = Path.home() / '.claude' / 'wrapped_metrics.db'


def init_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Initialize the SQLite database with required tables."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Main metrics snapshot table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT NOT NULL,
            total_sessions INTEGER,
            total_messages INTEGER,
            total_user_messages INTEGER,
            total_assistant_messages INTEGER,
            total_input_tokens INTEGER,
            total_output_tokens INTEGER,
            total_cache_creation_tokens INTEGER,
            total_cache_read_tokens INTEGER,
            total_cost_usd REAL,
            unique_projects INTEGER,
            longest_streak_days INTEGER,
            current_streak_days INTEGER,
            marathon_sessions INTEGER,
            rage_quit_sessions INTEGER,
            total_errors INTEGER,
            total_summaries INTEGER,
            cache_efficiency_ratio REAL,
            developer_personality TEXT,
            coding_city TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Project metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER,
            project_name TEXT,
            sessions INTEGER,
            messages INTEGER,
            tokens INTEGER,
            cost_usd REAL,
            first_session TEXT,
            last_session TEXT,
            FOREIGN KEY (snapshot_id) REFERENCES metrics_snapshots(id)
        )
    ''')

    # Tool usage table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tool_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER,
            tool_name TEXT,
            usage_count INTEGER,
            FOREIGN KEY (snapshot_id) REFERENCES metrics_snapshots(id)
        )
    ''')

    # Agent usage table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER,
            agent_name TEXT,
            usage_count INTEGER,
            FOREIGN KEY (snapshot_id) REFERENCES metrics_snapshots(id)
        )
    ''')

    # Task agent types table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_agent_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER,
            agent_type TEXT,
            usage_count INTEGER,
            FOREIGN KEY (snapshot_id) REFERENCES metrics_snapshots(id)
        )
    ''')

    # Model usage table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER,
            model_name TEXT,
            usage_count INTEGER,
            FOREIGN KEY (snapshot_id) REFERENCES metrics_snapshots(id)
        )
    ''')

    # Project analysis/classification table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT UNIQUE,
            project_path TEXT,
            description TEXT,
            technologies TEXT,  -- JSON array
            category TEXT,
            tags TEXT,  -- JSON array
            related_projects TEXT,  -- JSON array
            analyzed_at TEXT,
            analysis_source TEXT  -- 'readme', 'llm', 'manual'
        )
    ''')

    conn.commit()
    return conn


def save_metrics_snapshot(conn: sqlite3.Connection, data: dict) -> int:
    """Save a metrics snapshot to the database. Returns the snapshot ID."""
    cursor = conn.cursor()

    # Get snapshot date (today)
    snapshot_date = datetime.now().strftime('%Y-%m-%d')

    # Check if we already have a snapshot for today
    cursor.execute(
        'SELECT id FROM metrics_snapshots WHERE snapshot_date = ?',
        (snapshot_date,)
    )
    existing = cursor.fetchone()

    if existing:
        # Update existing snapshot
        snapshot_id = existing[0]
        cursor.execute('''
            UPDATE metrics_snapshots SET
                total_sessions = ?,
                total_messages = ?,
                total_user_messages = ?,
                total_assistant_messages = ?,
                total_input_tokens = ?,
                total_output_tokens = ?,
                total_cache_creation_tokens = ?,
                total_cache_read_tokens = ?,
                total_cost_usd = ?,
                unique_projects = ?,
                longest_streak_days = ?,
                current_streak_days = ?,
                marathon_sessions = ?,
                rage_quit_sessions = ?,
                total_errors = ?,
                total_summaries = ?,
                cache_efficiency_ratio = ?,
                developer_personality = ?,
                coding_city = ?
            WHERE id = ?
        ''', (
            data.get('total_sessions', 0),
            data.get('total_messages', 0),
            data.get('total_user_messages', 0),
            data.get('total_assistant_messages', 0),
            data.get('total_input_tokens', 0),
            data.get('total_output_tokens', 0),
            data.get('total_cache_creation_tokens', 0),
            data.get('total_cache_read_tokens', 0),
            data.get('total_cost_usd', 0),
            data.get('unique_projects', 0),
            data.get('longest_streak_days', 0),
            data.get('current_streak_days', 0),
            data.get('marathon_sessions', 0),
            data.get('shortest_sessions', 0),
            data.get('total_errors', 0),
            data.get('total_summaries', 0),
            data.get('cache_efficiency_ratio', 0),
            data.get('developer_personality', ''),
            data.get('coding_city', ''),
            snapshot_id
        ))

        # Clear old related data for this snapshot
        cursor.execute('DELETE FROM project_metrics WHERE snapshot_id = ?', (snapshot_id,))
        cursor.execute('DELETE FROM tool_usage WHERE snapshot_id = ?', (snapshot_id,))
        cursor.execute('DELETE FROM agent_usage WHERE snapshot_id = ?', (snapshot_id,))
        cursor.execute('DELETE FROM task_agent_types WHERE snapshot_id = ?', (snapshot_id,))
        cursor.execute('DELETE FROM model_usage WHERE snapshot_id = ?', (snapshot_id,))
    else:
        # Insert new snapshot
        cursor.execute('''
            INSERT INTO metrics_snapshots (
                snapshot_date, total_sessions, total_messages, total_user_messages,
                total_assistant_messages, total_input_tokens, total_output_tokens,
                total_cache_creation_tokens, total_cache_read_tokens, total_cost_usd,
                unique_projects, longest_streak_days, current_streak_days,
                marathon_sessions, rage_quit_sessions, total_errors, total_summaries,
                cache_efficiency_ratio, developer_personality, coding_city
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot_date,
            data.get('total_sessions', 0),
            data.get('total_messages', 0),
            data.get('total_user_messages', 0),
            data.get('total_assistant_messages', 0),
            data.get('total_input_tokens', 0),
            data.get('total_output_tokens', 0),
            data.get('total_cache_creation_tokens', 0),
            data.get('total_cache_read_tokens', 0),
            data.get('total_cost_usd', 0),
            data.get('unique_projects', 0),
            data.get('longest_streak_days', 0),
            data.get('current_streak_days', 0),
            data.get('marathon_sessions', 0),
            data.get('shortest_sessions', 0),
            data.get('total_errors', 0),
            data.get('total_summaries', 0),
            data.get('cache_efficiency_ratio', 0),
            data.get('developer_personality', ''),
            data.get('coding_city', '')
        ))
        snapshot_id = cursor.lastrowid

    # Save project metrics
    for proj in data.get('top_projects', []):
        cursor.execute('''
            INSERT INTO project_metrics (
                snapshot_id, project_name, sessions, messages, tokens,
                cost_usd, first_session, last_session
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot_id,
            proj.get('name', ''),
            proj.get('sessions', 0),
            proj.get('messages', 0),
            proj.get('tokens', 0),
            proj.get('cost', 0),
            proj.get('first_session', ''),
            proj.get('last_session', '')
        ))

    # Save tool usage
    for tool, count in data.get('tool_frequency', {}).items():
        cursor.execute('''
            INSERT INTO tool_usage (snapshot_id, tool_name, usage_count)
            VALUES (?, ?, ?)
        ''', (snapshot_id, tool, count))

    # Save agent usage
    for agent, count in data.get('agent_frequency', {}).items():
        cursor.execute('''
            INSERT INTO agent_usage (snapshot_id, agent_name, usage_count)
            VALUES (?, ?, ?)
        ''', (snapshot_id, agent, count))

    # Save task agent types
    for agent_type, count in data.get('task_agent_type_frequency', {}).items():
        cursor.execute('''
            INSERT INTO task_agent_types (snapshot_id, agent_type, usage_count)
            VALUES (?, ?, ?)
        ''', (snapshot_id, agent_type, count))

    # Save model usage
    for model, count in data.get('model_frequency', {}).items():
        cursor.execute('''
            INSERT INTO model_usage (snapshot_id, model_name, usage_count)
            VALUES (?, ?, ?)
        ''', (snapshot_id, model, count))

    conn.commit()
    return snapshot_id


def get_metrics_history(conn: sqlite3.Connection, days: int = 30) -> list[dict]:
    """Get metrics history for the past N days."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM metrics_snapshots
        WHERE snapshot_date >= date('now', ?)
        ORDER BY snapshot_date ASC
    ''', (f'-{days} days',))

    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_latest_snapshot(conn: sqlite3.Connection) -> Optional[dict]:
    """Get the most recent metrics snapshot."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM metrics_snapshots
        ORDER BY snapshot_date DESC LIMIT 1
    ''')

    row = cursor.fetchone()
    if row:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    return None


def save_project_analysis(
    conn: sqlite3.Connection,
    project_name: str,
    project_path: str,
    description: str,
    technologies: list,
    category: str,
    tags: list,
    related_projects: list,
    source: str = 'readme'
) -> None:
    """Save or update project analysis data."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO project_analysis (
            project_name, project_path, description, technologies,
            category, tags, related_projects, analyzed_at, analysis_source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        project_name,
        project_path,
        description,
        json.dumps(technologies),
        category,
        json.dumps(tags),
        json.dumps(related_projects),
        datetime.now().isoformat(),
        source
    ))
    conn.commit()


def get_project_analysis(conn: sqlite3.Connection, project_name: str) -> Optional[dict]:
    """Get analysis data for a specific project."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM project_analysis WHERE project_name = ?
    ''', (project_name,))

    row = cursor.fetchone()
    if row:
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        # Parse JSON fields
        result['technologies'] = json.loads(result.get('technologies', '[]') or '[]')
        result['tags'] = json.loads(result.get('tags', '[]') or '[]')
        result['related_projects'] = json.loads(result.get('related_projects', '[]') or '[]')
        return result
    return None


def get_all_project_analyses(conn: sqlite3.Connection) -> list[dict]:
    """Get all project analysis data."""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM project_analysis')

    columns = [desc[0] for desc in cursor.description]
    results = []
    for row in cursor.fetchall():
        result = dict(zip(columns, row))
        result['technologies'] = json.loads(result.get('technologies', '[]') or '[]')
        result['tags'] = json.loads(result.get('tags', '[]') or '[]')
        result['related_projects'] = json.loads(result.get('related_projects', '[]') or '[]')
        results.append(result)
    return results


def get_projects_by_category(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """Get projects grouped by category."""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, project_name FROM project_analysis
        WHERE category IS NOT NULL AND category != ''
        ORDER BY category, project_name
    ''')

    groups = defaultdict(list)
    for category, project_name in cursor.fetchall():
        groups[category].append(project_name)
    return dict(groups)


def get_projects_by_technology(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """Get projects grouped by technology."""
    analyses = get_all_project_analyses(conn)
    groups = defaultdict(list)

    for analysis in analyses:
        for tech in analysis.get('technologies', []):
            groups[tech].append(analysis['project_name'])

    return dict(groups)


if __name__ == '__main__':
    # Test the database
    conn = init_db()
    print(f"Database initialized at {DB_PATH}")

    # Show any existing snapshots
    history = get_metrics_history(conn)
    print(f"Found {len(history)} snapshots")
    for snap in history[-5:]:
        print(f"  {snap['snapshot_date']}: {snap['total_sessions']} sessions, ${snap['total_cost_usd']:.2f}")

    conn.close()
