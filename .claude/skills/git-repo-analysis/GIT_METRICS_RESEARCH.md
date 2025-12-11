# Git Metrics Research for Developer Analytics

## Overview

This document captures research on extracting meaningful developer activity metrics from git repositories for use in Claude Wrapped analytics.

## Available Git Data Sources

### 1. Commit Log (`git log`)

The primary source of developer activity data.

**Key Fields**:
- `%H` - Full commit hash
- `%h` - Abbreviated hash
- `%an` - Author name
- `%ae` - Author email
- `%at` - Author timestamp (Unix epoch)
- `%cn` - Committer name
- `%ce` - Committer email
- `%ct` - Committer timestamp
- `%s` - Subject (first line of commit message)
- `%b` - Body (rest of commit message)

**Optimal Format for Parsing**:
```bash
git log --format="%H|%an|%ae|%at|%s" --numstat
```

### 2. File Statistics (`--numstat`)

Per-commit file changes:
```
additions<TAB>deletions<TAB>filename
```

Example:
```
15      3       src/main.py
0       25      tests/old_test.py
-       -       binary_file.png   # Binary files show "-"
```

### 3. Repository Metadata

```bash
# First commit date
git log --reverse --format="%at" | head -1

# Last commit date
git log -1 --format="%at"

# Total commit count
git rev-list --count HEAD

# All branches
git branch -a

# Current branch
git branch --show-current

# Remote URLs
git remote -v
```

## Metric Categories

### Activity Metrics

| Metric | Calculation | Insight |
|--------|-------------|---------|
| Commits/day | total_commits / project_days | Development velocity |
| Lines/commit | (additions + deletions) / commits | Commit granularity |
| Net LOC | total_additions - total_deletions | Code growth |
| Churn rate | (additions + deletions) / total_lines | Code volatility |

### Time-Based Metrics

| Metric | Insight |
|--------|---------|
| Hour distribution | Developer's preferred coding hours |
| Day distribution | Weekday vs weekend patterns |
| Streak days | Consecutive days with commits |
| Active months | Months with significant activity |

### Author Metrics

| Metric | Calculation |
|--------|-------------|
| Commit share | author_commits / total_commits |
| Line contribution | author_lines / total_lines |
| Primary author | Author with most commits |
| Collaboration score | unique_authors / total_commits |

## Language Detection

### From File Extensions

```python
LANG_MAP = {
    # Primary languages
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

    # Web/Frontend
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.vue': 'Vue',
    '.svelte': 'Svelte',

    # Data/Config
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
    '.sql': 'SQL',

    # Shell/Scripts
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.zsh': 'Shell',

    # Documentation
    '.md': 'Markdown',
    '.rst': 'RST',
}
```

### Language Weighting

Weight by lines of actual code changed (excluding docs/config):

```python
CODE_WEIGHTS = {
    'Python': 1.0,
    'TypeScript': 1.0,
    'JavaScript': 1.0,
    'Go': 1.0,
    'Rust': 1.0,
    'Java': 1.0,
    'JSON': 0.3,
    'YAML': 0.3,
    'Markdown': 0.1,
    'HTML': 0.5,
    'CSS': 0.5,
}
```

## Engagement Score Formula

### Base Formula

```python
def engagement_score(repo):
    """
    Calculate engagement score (0-1) for a repository.

    Components:
    - Activity volume (commits, lines)
    - Recency (how recently active)
    - Duration (project lifespan)
    - Consistency (commit frequency variance)
    """

    # Normalize to 0-1 scale
    commit_score = min(1.0, repo.total_commits / 500)
    lines_score = min(1.0, repo.net_lines / 50000)

    # Recency: 1.0 for today, decays over 30 days
    days_since = (now - repo.last_commit).days
    recency_score = max(0, 1 - (days_since / 30))

    # Duration: Longer projects get slight boost
    duration_score = min(1.0, repo.duration_days / 365)

    # Weighted combination
    return (
        0.30 * commit_score +
        0.25 * lines_score +
        0.30 * recency_score +
        0.15 * duration_score
    )
```

### Adjustment Factors

```python
# Boost for diverse file types (not just one language)
if len(repo.languages) > 2:
    score *= 1.1

# Boost for user being primary author (>80% commits)
if repo.user_commit_share > 0.8:
    score *= 1.15

# Penalty for very old last commit (>6 months)
if days_since > 180:
    score *= 0.7
```

## Integration with Claude Session Data

### Correlation Strategy

1. **Direct Path Match**: Claude project paths often decode to actual filesystem paths
2. **Name Similarity**: Project names usually match repo names
3. **Temporal Overlap**: Active periods should correlate

### Combined Ranking Formula

```python
def combined_project_score(claude_data, git_data):
    """
    Combine Claude session metrics with git metrics.

    Claude metrics (from analyzer.py):
    - tokens (35%)
    - duration (25%)
    - messages (20%)
    - cost (15%)
    - sessions (5%)

    Git metrics:
    - commits (25%)
    - lines_changed (30%)
    - recency (25%)
    - duration (20%)
    """

    if claude_data and git_data:
        # Both sources available - full weighting
        claude_score = calculate_claude_score(claude_data)
        git_score = calculate_git_score(git_data)
        return 0.55 * claude_score + 0.45 * git_score

    elif claude_data:
        # Claude only - slight penalty
        return 0.85 * calculate_claude_score(claude_data)

    elif git_data:
        # Git only (no Claude sessions) - can still include
        return 0.50 * calculate_git_score(git_data)

    return 0
```

## Performance Considerations

### Large Repository Handling

```python
# Thresholds
MAX_COMMITS_TO_ANALYZE = 5000
MAX_REPO_SIZE_MB = 500
MAX_FILES_IN_COMMIT = 200  # Skip bulk commits (initial commits, vendor adds)

# Check repo size before deep analysis
def should_analyze_repo(path):
    size = get_repo_size_mb(path)
    if size > MAX_REPO_SIZE_MB:
        return False  # Likely a cloned library

    commits = get_commit_count(path)
    if commits > 50000:
        return False  # Massive repo, likely not personal project

    return True
```

### Caching Strategy

```python
CACHE_STRUCTURE = {
    "repos": {
        "/path/to/repo": {
            "stats": {...},
            "analyzed_at": 1702345678,
            "commit_hash": "abc123",  # HEAD at time of analysis
        }
    },
    "global_stats": {...},
    "last_full_scan": 1702345678,
}

# Re-analyze if:
# 1. Cache older than 24 hours
# 2. HEAD has changed
# 3. Cache doesn't exist
```

## Output Integration

### New Fields for ClaudeWrappedData

```python
@dataclass
class ClaudeWrappedData:
    # ... existing fields ...

    # Git repository metrics
    git_repos_analyzed: int = 0
    git_total_commits: int = 0
    git_total_lines_written: int = 0
    git_primary_languages: list = field(default_factory=list)
    git_hourly_distribution: dict = field(default_factory=dict)
    git_daily_distribution: dict = field(default_factory=dict)
    git_most_active_repo: str = ""
    git_longest_streak_days: int = 0

    # Combined project rankings (merged Claude + Git data)
    top_projects_combined: list = field(default_factory=list)
```

### API Response Format

```json
{
    "git_analysis": {
        "summary": {
            "repos_found": 42,
            "repos_analyzed": 35,
            "total_commits": 8500,
            "total_lines": 250000,
            "languages": {
                "Python": 45000,
                "TypeScript": 35000,
                "Go": 15000
            }
        },
        "top_repos": [...],
        "time_patterns": {
            "peak_hour": 21,
            "peak_day": "Wednesday",
            "weekend_ratio": 0.15
        },
        "streaks": {
            "longest": 45,
            "current": 12
        }
    }
}
```

## Error Handling

### Common Issues

1. **Permission denied**: Some repos may not be readable
2. **Corrupt repos**: Incomplete `.git` directories
3. **Shallow clones**: Limited history available
4. **Non-git directories**: False positives in search
5. **Timeout**: Very large repos taking too long

### Graceful Degradation

```python
def analyze_repo_safe(path):
    try:
        return analyze_repo(path)
    except subprocess.TimeoutExpired:
        return PartialStats(path, error="timeout")
    except PermissionError:
        return PartialStats(path, error="permission_denied")
    except Exception as e:
        return PartialStats(path, error=str(e))
```

## Future Enhancements

1. **Branch analysis**: Track feature branches vs main
2. **Tag/release detection**: Identify project milestones
3. **Co-author analysis**: Detect collaboration patterns
4. **Commit message analysis**: NLP on commit messages for project insights
5. **GitHub API integration**: Fetch issue/PR data for public repos
