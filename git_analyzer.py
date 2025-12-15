#!/usr/bin/env python3
"""
Git Repository Analyzer for Claude Wrapped.

Discovers git repositories on the local machine and extracts
developer activity metrics for inclusion in project rankings.
"""

import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


# Common development directories to search for git repos
COMMON_DEV_PATHS = [
    '~/projects',
    '~/repos',
    '~/code',
    '~/dev',
    '~/work',
    '~/github',
    '~/gitlab',
    '~/sundai',
    '~/Documents/code',
    '~/Documents/projects',
    '~/src',
]

# Directories to skip when searching
SKIP_PATTERNS = {
    'node_modules', '.venv', 'venv', 'vendor', 'dist',
    'build', 'target', '__pycache__', 'site-packages',
    '.git', '.cargo', '.npm', '.cache', 'Library',
}

# Patterns for automated/bot commits to filter
AUTOMATED_AUTHORS = {
    'dependabot', 'renovate', 'github-actions', 'bot',
    'semantic-release', 'greenkeeper', 'snyk-bot',
}

# Language detection from file extensions
LANGUAGE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.jsx': 'JavaScript',
    '.go': 'Go',
    '.rs': 'Rust',
    '.java': 'Java',
    '.kt': 'Kotlin',
    '.swift': 'Swift',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.cs': 'C#',
    '.cpp': 'C++',
    '.c': 'C',
    '.h': 'C/C++',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.vue': 'Vue',
    '.svelte': 'Svelte',
    '.sql': 'SQL',
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.zsh': 'Shell',
    '.md': 'Markdown',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.json': 'JSON',
    '.toml': 'TOML',
}

# Weights for language scoring (code vs config/docs)
LANGUAGE_WEIGHTS = {
    'Python': 1.0, 'TypeScript': 1.0, 'JavaScript': 1.0,
    'Go': 1.0, 'Rust': 1.0, 'Java': 1.0, 'Kotlin': 1.0,
    'Swift': 1.0, 'Ruby': 1.0, 'PHP': 1.0, 'C#': 1.0,
    'C++': 1.0, 'C': 1.0, 'Vue': 0.9, 'Svelte': 0.9,
    'HTML': 0.5, 'CSS': 0.5, 'SCSS': 0.5,
    'SQL': 0.7, 'Shell': 0.8,
    'JSON': 0.2, 'YAML': 0.2, 'TOML': 0.2,
    'Markdown': 0.1, 'C/C++': 1.0,
}

# Maximum commits to parse per repo (performance limit)
MAX_COMMITS_TO_PARSE = 5000

# Maximum repo size in MB to analyze
MAX_REPO_SIZE_MB = 500


@dataclass
class GitRepoStats:
    """Statistics for a single git repository."""
    path: str
    name: str
    total_commits: int = 0
    user_commits: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    net_lines: int = 0
    authors: dict = field(default_factory=dict)
    first_commit: Optional[datetime] = None
    last_commit: Optional[datetime] = None
    duration_days: int = 0
    commits_per_day: float = 0.0
    hourly_distribution: dict = field(default_factory=dict)
    daily_distribution: dict = field(default_factory=dict)
    monthly_distribution: dict = field(default_factory=dict)
    file_types: dict = field(default_factory=dict)
    languages: list = field(default_factory=list)
    primary_language: str = ""
    commit_sizes: dict = field(default_factory=lambda: {
        'small': 0,   # < 50 lines
        'medium': 0,  # 50-200 lines
        'large': 0,   # > 200 lines
    })
    engagement_score: float = 0.0
    matched_claude_project: str = ""
    error: str = ""


@dataclass
class GitAnalysisSummary:
    """Summary of all git repository analysis."""
    repos_found: int = 0
    repos_analyzed: int = 0
    total_commits: int = 0
    user_commits: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    total_net_lines: int = 0
    languages: dict = field(default_factory=dict)
    hourly_distribution: dict = field(default_factory=dict)
    daily_distribution: dict = field(default_factory=dict)
    most_active_repo: str = ""
    most_active_repo_commits: int = 0
    longest_streak_days: int = 0
    current_streak_days: int = 0
    peak_hour: int = 0
    peak_day: str = ""
    weekend_ratio: float = 0.0
    top_repos: list = field(default_factory=list)


def find_git_repos(
    base_paths: list[str] = None,
    max_depth: int = 4,
    max_repos: int = 100
) -> list[str]:
    """
    Find git repositories in common development directories.

    Args:
        base_paths: List of paths to search. Defaults to COMMON_DEV_PATHS.
        max_depth: Maximum directory depth to search.
        max_repos: Maximum number of repos to return.

    Returns:
        List of absolute paths to git repositories.
    """
    if base_paths is None:
        base_paths = COMMON_DEV_PATHS

    repos = []

    for base in base_paths:
        base_expanded = os.path.expanduser(base)
        if not os.path.exists(base_expanded):
            continue

        try:
            # Use find command for efficiency
            result = subprocess.run(
                ['find', base_expanded, '-maxdepth', str(max_depth),
                 '-name', '.git', '-type', 'd'],
                capture_output=True,
                text=True,
                timeout=30
            )

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                git_dir = line.strip()
                repo_path = os.path.dirname(git_dir)

                # Skip if in a known skip directory
                path_parts = set(repo_path.split(os.sep))
                if path_parts & SKIP_PATTERNS:
                    continue

                repos.append(repo_path)

                if len(repos) >= max_repos:
                    return repos

        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue

    return repos


def get_user_identifiers() -> list[str]:
    """
    Get identifiers for the current user from git config and environment.

    Returns:
        List of strings that might identify the user in git commits.
    """
    identifiers = []

    # Get git config user info
    try:
        result = subprocess.run(
            ['git', 'config', '--global', 'user.email'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            email = result.stdout.strip().lower()
            identifiers.append(email)
            # Also add username part of email
            if '@' in email:
                identifiers.append(email.split('@')[0])
    except Exception:
        pass

    try:
        result = subprocess.run(
            ['git', 'config', '--global', 'user.name'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            identifiers.append(result.stdout.strip().lower())
    except Exception:
        pass

    # Add system username
    identifiers.append(os.environ.get('USER', '').lower())
    identifiers.append(os.environ.get('USERNAME', '').lower())

    # Filter empty strings
    return [i for i in identifiers if i]


def is_user_commit(author_email: str, author_name: str, user_identifiers: list[str]) -> bool:
    """Check if a commit belongs to the current user."""
    email_lower = author_email.lower()
    name_lower = author_name.lower()

    for identifier in user_identifiers:
        if identifier in email_lower or identifier in name_lower:
            return True

    return False


def is_automated_commit(author_name: str, author_email: str) -> bool:
    """Check if a commit is from an automated bot."""
    combined = (author_name + author_email).lower()
    return any(bot in combined for bot in AUTOMATED_AUTHORS)


def parse_git_log(repo_path: str, max_commits: int = MAX_COMMITS_TO_PARSE) -> list[dict]:
    """
    Parse git log for a repository.

    Args:
        repo_path: Path to the git repository.
        max_commits: Maximum number of commits to parse.

    Returns:
        List of commit dictionaries with stats.
    """
    commits = []

    try:
        # Get commits with file stats
        result = subprocess.run(
            ['git', '-C', repo_path, 'log',
             f'-{max_commits}',
             '--numstat',
             '--format=COMMIT|%H|%an|%ae|%at|%s'],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            return commits

        current_commit = None

        for line in result.stdout.split('\n'):
            if line.startswith('COMMIT|'):
                if current_commit:
                    commits.append(current_commit)

                parts = line.split('|')
                if len(parts) >= 5:
                    current_commit = {
                        'hash': parts[1],
                        'author_name': parts[2],
                        'author_email': parts[3],
                        'timestamp': int(parts[4]) if parts[4].isdigit() else 0,
                        'message': parts[5] if len(parts) > 5 else '',
                        'additions': 0,
                        'deletions': 0,
                        'files': [],
                    }

            elif line and '\t' in line and current_commit:
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        adds = int(parts[0]) if parts[0] != '-' else 0
                        dels = int(parts[1]) if parts[1] != '-' else 0
                        filename = parts[2]
                        current_commit['additions'] += adds
                        current_commit['deletions'] += dels
                        current_commit['files'].append(filename)
                    except ValueError:
                        pass

        if current_commit:
            commits.append(current_commit)

    except subprocess.TimeoutExpired:
        pass
    except Exception:
        pass

    return commits


def analyze_repo(repo_path: str, user_identifiers: list[str] = None) -> GitRepoStats:
    """
    Analyze a single git repository.

    Args:
        repo_path: Path to the git repository.
        user_identifiers: List of strings to identify user commits.

    Returns:
        GitRepoStats with analysis results.
    """
    name = os.path.basename(repo_path)
    stats = GitRepoStats(path=repo_path, name=name)

    if user_identifiers is None:
        user_identifiers = get_user_identifiers()

    # Parse git log
    commits = parse_git_log(repo_path)

    if not commits:
        stats.error = "no_commits"
        return stats

    stats.total_commits = len(commits)

    # Initialize distributions
    hourly = defaultdict(int)
    daily = defaultdict(int)
    monthly = defaultdict(int)
    authors = defaultdict(lambda: {'commits': 0, 'additions': 0, 'deletions': 0})
    file_types = defaultdict(int)
    commit_dates = set()

    for commit in commits:
        timestamp = commit['timestamp']
        author_name = commit['author_name']
        author_email = commit['author_email']
        additions = commit['additions']
        deletions = commit['deletions']
        files = commit['files']

        # Skip automated commits
        if is_automated_commit(author_name, author_email):
            continue

        # Track if user commit
        if is_user_commit(author_email, author_name, user_identifiers):
            stats.user_commits += 1

        # Accumulate totals
        stats.total_additions += additions
        stats.total_deletions += deletions

        # Author stats
        authors[author_name]['commits'] += 1
        authors[author_name]['additions'] += additions
        authors[author_name]['deletions'] += deletions

        # Time distributions
        if timestamp:
            dt = datetime.fromtimestamp(timestamp)
            hourly[dt.hour] += 1
            daily[dt.strftime('%A')] += 1
            monthly[dt.strftime('%Y-%m')] += 1
            commit_dates.add(dt.date())

            # Track first/last commit
            if stats.first_commit is None or dt < stats.first_commit:
                stats.first_commit = dt
            if stats.last_commit is None or dt > stats.last_commit:
                stats.last_commit = dt

        # Commit size classification
        total_lines = additions + deletions
        if total_lines < 50:
            stats.commit_sizes['small'] += 1
        elif total_lines < 200:
            stats.commit_sizes['medium'] += 1
        else:
            stats.commit_sizes['large'] += 1

        # File type tracking
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext:
                file_types[ext] += 1

    # Calculate net lines
    stats.net_lines = stats.total_additions - stats.total_deletions

    # Convert distributions
    stats.hourly_distribution = dict(hourly)
    stats.daily_distribution = dict(daily)
    stats.monthly_distribution = dict(monthly)
    stats.authors = dict(authors)
    stats.file_types = dict(file_types)

    # Calculate duration
    if stats.first_commit and stats.last_commit:
        stats.duration_days = (stats.last_commit - stats.first_commit).days or 1
        stats.commits_per_day = stats.total_commits / stats.duration_days

    # Detect languages
    lang_counts = defaultdict(int)
    for ext, count in file_types.items():
        lang = LANGUAGE_EXTENSIONS.get(ext)
        if lang:
            weight = LANGUAGE_WEIGHTS.get(lang, 0.5)
            lang_counts[lang] += count * weight

    if lang_counts:
        sorted_langs = sorted(lang_counts.items(), key=lambda x: -x[1])
        stats.languages = [lang for lang, _ in sorted_langs[:5]]
        stats.primary_language = sorted_langs[0][0]

    # Calculate engagement score
    stats.engagement_score = calculate_engagement_score(stats)

    return stats


def calculate_engagement_score(stats: GitRepoStats) -> float:
    """
    Calculate engagement score for a repository (0-1 scale).

    Factors:
    - Commit count (25%)
    - Lines changed (30%)
    - Recency (25%)
    - Duration (20%)
    """
    # Normalize commit count (500 commits = 1.0)
    commit_score = min(1.0, stats.total_commits / 500)

    # Normalize lines changed (50k = 1.0)
    lines_changed = stats.total_additions + stats.total_deletions
    lines_score = min(1.0, lines_changed / 50000)

    # Recency: 1.0 for today, decays over 30 days
    recency_score = 0.0
    if stats.last_commit:
        now = datetime.now()
        days_since = (now - stats.last_commit).days
        recency_score = max(0.0, 1.0 - (days_since / 30))

    # Duration: Longer projects get boost (1 year = 1.0)
    duration_score = min(1.0, stats.duration_days / 365) if stats.duration_days else 0.0

    # Weighted combination
    score = (
        0.25 * commit_score +
        0.30 * lines_score +
        0.25 * recency_score +
        0.20 * duration_score
    )

    # Boost for user being primary contributor
    if stats.total_commits > 0:
        user_ratio = stats.user_commits / stats.total_commits
        if user_ratio > 0.8:
            score *= 1.1

    # Boost for diverse languages
    if len(stats.languages) > 2:
        score *= 1.05

    return min(1.0, score)


def calculate_streaks(commit_dates: list[datetime]) -> tuple[int, int]:
    """
    Calculate longest and current commit streaks.

    Args:
        commit_dates: List of commit timestamps.

    Returns:
        Tuple of (longest_streak, current_streak).
    """
    if not commit_dates:
        return 0, 0

    # Get unique dates
    unique_dates = sorted(set(d.date() for d in commit_dates))

    if not unique_dates:
        return 0, 0

    # Calculate longest streak
    longest = 1
    current = 1

    for i in range(1, len(unique_dates)):
        if (unique_dates[i] - unique_dates[i-1]).days == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    # Calculate current streak
    today = datetime.now().date()
    current_streak = 0

    if unique_dates[-1] == today or unique_dates[-1] == today - timedelta(days=1):
        current_streak = 1
        for i in range(len(unique_dates) - 2, -1, -1):
            if (unique_dates[i+1] - unique_dates[i]).days == 1:
                current_streak += 1
            else:
                break

    return longest, current_streak


def analyze_all_repos(
    base_paths: list[str] = None,
    max_repos: int = 100,
    max_workers: int = 4
) -> tuple[list[GitRepoStats], GitAnalysisSummary]:
    """
    Analyze all git repositories found in common locations.

    Args:
        base_paths: List of paths to search.
        max_repos: Maximum number of repos to analyze.
        max_workers: Number of parallel workers.

    Returns:
        Tuple of (list of GitRepoStats, GitAnalysisSummary).
    """
    # Find repos
    repo_paths = find_git_repos(base_paths, max_repos=max_repos)

    if not repo_paths:
        return [], GitAnalysisSummary()

    # Get user identifiers once
    user_identifiers = get_user_identifiers()

    # Analyze repos in parallel
    all_stats = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(analyze_repo, path, user_identifiers): path
            for path in repo_paths
        }

        for future in as_completed(futures):
            try:
                stats = future.result(timeout=120)
                if stats and not stats.error:
                    all_stats.append(stats)
            except Exception:
                pass

    # Sort by engagement score
    all_stats.sort(key=lambda x: x.engagement_score, reverse=True)

    # Build summary
    summary = build_summary(all_stats, len(repo_paths))

    return all_stats, summary


def build_summary(all_stats: list[GitRepoStats], repos_found: int) -> GitAnalysisSummary:
    """Build analysis summary from all repo stats."""
    summary = GitAnalysisSummary()
    summary.repos_found = repos_found
    summary.repos_analyzed = len(all_stats)

    if not all_stats:
        return summary

    # Aggregate metrics
    hourly_agg = defaultdict(int)
    daily_agg = defaultdict(int)
    lang_agg = defaultdict(int)
    all_commit_dates = []

    for stats in all_stats:
        summary.total_commits += stats.total_commits
        summary.user_commits += stats.user_commits
        summary.total_additions += stats.total_additions
        summary.total_deletions += stats.total_deletions
        summary.total_net_lines += stats.net_lines

        # Aggregate hourly
        for hour, count in stats.hourly_distribution.items():
            hourly_agg[hour] += count

        # Aggregate daily
        for day, count in stats.daily_distribution.items():
            daily_agg[day] += count

        # Aggregate languages
        for lang in stats.languages:
            lang_agg[lang] += 1

        # Collect commit dates for streak calculation
        if stats.first_commit:
            all_commit_dates.append(stats.first_commit)
        if stats.last_commit:
            all_commit_dates.append(stats.last_commit)

        # Track most active repo
        if stats.total_commits > summary.most_active_repo_commits:
            summary.most_active_repo_commits = stats.total_commits
            summary.most_active_repo = stats.name

    summary.hourly_distribution = dict(hourly_agg)
    summary.daily_distribution = dict(daily_agg)
    summary.languages = dict(lang_agg)

    # Find peak hour
    if hourly_agg:
        summary.peak_hour = max(hourly_agg.keys(), key=lambda h: hourly_agg[h])

    # Find peak day
    if daily_agg:
        summary.peak_day = max(daily_agg.keys(), key=lambda d: daily_agg[d])

    # Calculate weekend ratio
    total_daily = sum(daily_agg.values())
    if total_daily > 0:
        weekend = daily_agg.get('Saturday', 0) + daily_agg.get('Sunday', 0)
        summary.weekend_ratio = weekend / total_daily

    # Calculate streaks
    if all_commit_dates:
        summary.longest_streak_days, summary.current_streak_days = calculate_streaks(all_commit_dates)

    # Top repos
    summary.top_repos = [
        {
            'name': s.name,
            'path': s.path,
            'commits': s.total_commits,
            'user_commits': s.user_commits,
            'net_lines': s.net_lines,
            'languages': s.languages,
            'engagement_score': s.engagement_score,
            'last_commit': s.last_commit.isoformat() if s.last_commit else None,
        }
        for s in all_stats[:25]
    ]

    return summary


def correlate_repos_to_projects(
    git_repos: list[GitRepoStats],
    claude_projects: list[dict]
) -> dict[str, GitRepoStats]:
    """
    Match git repos to Claude Code projects.

    Args:
        git_repos: List of analyzed git repos.
        claude_projects: List of Claude project dicts with 'name' key.

    Returns:
        Dict mapping Claude project names to matched GitRepoStats.
    """
    matches = {}

    for repo in git_repos:
        repo_name = repo.name.lower().replace('_', '-')

        for project in claude_projects:
            proj_name = project.get('name', '').lower().replace('_', '-')

            if not proj_name:
                continue

            # Exact match
            if repo_name == proj_name:
                matches[project['name']] = repo
                repo.matched_claude_project = project['name']
                break

            # Partial match (repo name in project name or vice versa)
            if repo_name in proj_name or proj_name in repo_name:
                # Only use partial match if no existing exact match
                if project['name'] not in matches:
                    matches[project['name']] = repo
                    repo.matched_claude_project = project['name']

    return matches


def to_json_serializable(stats: GitRepoStats) -> dict:
    """Convert GitRepoStats to JSON-serializable dict."""
    result = asdict(stats)

    # Convert datetime objects
    if result.get('first_commit'):
        result['first_commit'] = stats.first_commit.isoformat() if stats.first_commit else None
    if result.get('last_commit'):
        result['last_commit'] = stats.last_commit.isoformat() if stats.last_commit else None

    return result


def main():
    """Main entry point for standalone execution."""
    import sys

    print("Scanning for git repositories...", file=sys.stderr)

    # Optional: custom base paths from args
    base_paths = None
    if len(sys.argv) > 1:
        base_paths = sys.argv[1:]

    all_stats, summary = analyze_all_repos(base_paths)

    print(f"Found {summary.repos_found} repos, analyzed {summary.repos_analyzed}", file=sys.stderr)

    # Output JSON
    output = {
        'summary': asdict(summary),
        'repos': [to_json_serializable(s) for s in all_stats],
    }

    print(json.dumps(output, indent=2, default=str))


if __name__ == '__main__':
    main()
