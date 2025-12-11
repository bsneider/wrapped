# Git Repository Analysis Skill

Use this skill when analyzing git repositories to extract developer activity metrics, project engagement patterns, and contribution statistics for inclusion in Claude Wrapped metrics.

## When to Use

- Discovering git repositories on the local machine
- Extracting commit history metrics from repos
- Analyzing developer contribution patterns
- Calculating project engagement scores based on git activity
- Augmenting Claude session data with actual code development metrics

## Key Concepts

### Repository Discovery

Git repositories can be found by searching for `.git` directories in common development locations:

```python
COMMON_DEV_PATHS = [
    '~/projects', '~/repos', '~/code', '~/dev', '~/work',
    '~/github', '~/gitlab', '~/sundai', '~/Documents/code',
]
```

**Discovery Strategy**:
1. Search each base path with limited depth (3-4 levels)
2. Filter out vendor directories (node_modules, .venv, vendor)
3. Validate each repo is accessible and has commits

### Commit Metrics

Git commits provide rich activity data:

| Metric | Git Command | Purpose |
|--------|-------------|---------|
| Total commits | `git rev-list --count HEAD` | Repository size/maturity |
| Commit history | `git log --format="%at|%an|%s"` | Timeline & authors |
| File changes | `git log --numstat` | Lines added/deleted |
| Author stats | `git shortlog -sn` | Contributor breakdown |
| Date range | First/last commit timestamps | Project lifespan |

### Lines of Code Metrics

```python
# Per-commit line changes
git log --numstat --format="%H|%an|%at|%s"

# Extractable metrics:
- additions: Lines added per commit
- deletions: Lines removed per commit
- net_lines: additions - deletions
- churn: additions + deletions (total change volume)
```

### Time Pattern Analysis

Extract temporal patterns from commit timestamps:

```python
from datetime import datetime

def analyze_time_patterns(timestamps):
    hourly = defaultdict(int)
    daily = defaultdict(int)
    monthly = defaultdict(int)

    for ts in timestamps:
        dt = datetime.fromtimestamp(ts)
        hourly[dt.hour] += 1
        daily[dt.strftime('%A')] += 1
        monthly[dt.strftime('%Y-%m')] += 1

    return hourly, daily, monthly
```

### Author Attribution

Link git authors to user identity:

```python
# Common patterns to match:
# - Email domain matching
# - Username in email prefix
# - Git config user.name/user.email

def is_user_commit(author_email, user_identifiers):
    """Check if commit belongs to current user."""
    email_lower = author_email.lower()
    for identifier in user_identifiers:
        if identifier.lower() in email_lower:
            return True
    return False
```

## Key Metrics

### Engagement Score

Calculate weighted engagement score for project ranking:

```python
def calculate_engagement_score(repo_stats, max_values):
    """
    Weights:
    - commit_count: 25% - Developer activity frequency
    - lines_changed: 30% - Code contribution volume
    - recency: 25% - Recent activity (days since last commit)
    - duration: 20% - Project lifespan
    """
    return (
        0.25 * (repo_stats['commits'] / max_values['commits']) +
        0.30 * (repo_stats['lines_changed'] / max_values['lines_changed']) +
        0.25 * (recency_score(repo_stats['last_commit'])) +
        0.20 * (repo_stats['duration_days'] / max_values['duration_days'])
    )
```

### Activity Intensity

```python
intensity = total_commits / project_duration_days
# < 0.1: Low activity
# 0.1 - 0.5: Moderate activity
# 0.5 - 2: High activity
# > 2: Very high (rapid development)
```

### Commit Size Distribution

```python
SMALL_COMMIT = 50    # < 50 lines changed
MEDIUM_COMMIT = 200  # 50-200 lines changed
LARGE_COMMIT = 200   # > 200 lines changed

# Small commits = incremental changes
# Large commits = major features/refactors
```

### Language Detection

Detect primary languages from file extensions in commits:

```python
LANGUAGE_EXTENSIONS = {
    '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
    '.go': 'Go', '.rs': 'Rust', '.java': 'Java', '.rb': 'Ruby',
    '.cpp': 'C++', '.c': 'C', '.swift': 'Swift', '.kt': 'Kotlin',
}
```

## Implementation Pattern

### Repository Scanner Class

```python
@dataclass
class GitRepoStats:
    """Statistics for a single git repository."""
    path: str
    name: str
    total_commits: int = 0
    user_commits: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    authors: dict = field(default_factory=dict)
    first_commit: Optional[datetime] = None
    last_commit: Optional[datetime] = None
    hourly_distribution: dict = field(default_factory=dict)
    daily_distribution: dict = field(default_factory=dict)
    file_types: dict = field(default_factory=dict)
    commit_sizes: dict = field(default_factory=dict)
    languages: list = field(default_factory=list)
    engagement_score: float = 0.0
```

### Efficient Parsing

For large repositories, use streaming parsing:

```python
def parse_git_log_stream(repo_path, limit=1000):
    """Stream-parse git log without loading all into memory."""
    cmd = ['git', '-C', repo_path, 'log',
           '--numstat',
           '--format=COMMIT|%at|%an|%ae|%s',
           f'-{limit}']

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

    current_commit = None
    for line in process.stdout:
        # Process line by line...
```

## Merging with Claude Session Data

### Correlation Strategy

Match git repos to Claude projects by:

1. **Path matching**: Compare decoded Claude project paths to repo paths
2. **Name similarity**: Fuzzy match project names
3. **Time correlation**: Match active periods

```python
def correlate_repos_to_projects(git_repos, claude_projects):
    """Match git repos to Claude Code projects."""
    matches = []

    for repo in git_repos:
        repo_name = repo.name.lower().replace('_', '-')

        for project in claude_projects:
            proj_name = project['name'].lower().replace('_', '-')

            if repo_name == proj_name:
                matches.append((repo, project, 1.0))  # Exact match
            elif repo_name in proj_name or proj_name in repo_name:
                matches.append((repo, project, 0.8))  # Partial match

    return matches
```

### Combined Engagement Score

Merge Claude session metrics with git metrics:

```python
def combined_engagement_score(claude_stats, git_stats):
    """
    Claude metrics (existing):
    - tokens (35%), duration (25%), messages (20%), cost (15%), sessions (5%)

    Git metrics (new):
    - commits (20%), lines_changed (25%), recency (15%)

    Combined: Weight Claude at 60%, Git at 40%
    """
    claude_score = calculate_claude_engagement(claude_stats)
    git_score = calculate_git_engagement(git_stats)

    # Projects with both get full score
    if claude_stats and git_stats:
        return 0.60 * claude_score + 0.40 * git_score
    elif claude_stats:
        return 0.80 * claude_score  # Slight penalty for no git
    else:
        return 0.50 * git_score  # Git-only projects ranked lower
```

## Best Practices

### Performance Optimization

```python
# Limit commit history parsing for large repos
MAX_COMMITS_TO_PARSE = 5000

# Skip very large repos (cloned libraries)
MAX_REPO_SIZE_MB = 500

# Parallel repository scanning
from concurrent.futures import ThreadPoolExecutor

def scan_repos_parallel(repo_paths, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(analyze_repo, repo_paths))
```

### Filtering Noise

```python
# Skip directories that are typically not user projects
SKIP_PATTERNS = [
    'node_modules', '.venv', 'venv', 'vendor', 'dist',
    'build', 'target', '.git', '__pycache__', 'site-packages',
]

# Skip repos with only automated commits
AUTOMATED_AUTHORS = ['dependabot', 'renovate', 'github-actions']
```

### Caching Results

```python
# Cache expensive git operations
CACHE_FILE = '~/.cache/claude-wrapped/git_repo_cache.json'
CACHE_TTL_HOURS = 24

def get_cached_repo_stats(repo_path):
    cache = load_cache()
    key = repo_path

    if key in cache and not is_stale(cache[key]):
        return cache[key]

    stats = analyze_repo_fresh(repo_path)
    cache[key] = {'stats': stats, 'timestamp': time.time()}
    save_cache(cache)
    return stats
```

## Related Files

- `git_analyzer.py`: Main implementation module
- `analyzer.py`: Integration point for Claude session data
- `project_analyzer.py`: Project framework detection
- `patterns.py`: Language and framework patterns

## Output Format

Git analysis results should follow this structure for integration:

```json
{
    "git_repos": [
        {
            "name": "project-name",
            "path": "/path/to/repo",
            "stats": {
                "total_commits": 150,
                "user_commits": 120,
                "total_additions": 5000,
                "total_deletions": 1200,
                "net_lines": 3800,
                "first_commit": "2024-01-15T10:30:00",
                "last_commit": "2025-12-10T22:45:00",
                "duration_days": 330,
                "commits_per_day": 0.45,
                "languages": ["Python", "TypeScript", "SQL"],
                "top_contributors": [
                    {"name": "user", "commits": 120, "lines": 4500}
                ]
            },
            "engagement_score": 0.85,
            "matched_claude_project": "project-name"
        }
    ],
    "git_summary": {
        "total_repos": 25,
        "total_commits": 3500,
        "total_lines_written": 150000,
        "most_active_repo": "project-name",
        "primary_languages": ["Python", "TypeScript"],
        "coding_hours_by_day": {...},
        "coding_hours_by_hour": {...}
    }
}
```
