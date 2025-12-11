#!/usr/bin/env python3
"""
Project Analyzer for Claude Wrapped.
Analyzes project READMEs and conversation content to:
1. Determine project purpose and technologies
2. Group related projects (e.g., coscientist-swarm, olivetree)
3. Detect framework/tool usage (e.g., claude-flow, SPARC)
"""

import json
import os
import re
import subprocess
from pathlib import Path
from collections import defaultdict, Counter
from typing import Optional
from dataclasses import dataclass, field


# Known frameworks/tools and their detection keywords
FRAMEWORK_KEYWORDS = {
    'claude-flow': [
        # NPM package references
        'claude-flow', '@anthropics/claude-flow', 'npm install claude-flow',
        'npx claude-flow', 'yarn add claude-flow', 'pnpm add claude-flow',
        # Package.json dependencies
        '"claude-flow"', "'claude-flow'",
        # CLI commands and config
        'flow.yaml', 'flow.yml', 'claude-flow init', 'claude-flow run',
        'claude-flow generate', 'claude-flow start',
        # Code patterns
        'import.*claude-flow', 'require.*claude-flow',
        'ClaudeFlow', 'claude_flow',
        # Common usage patterns in prompts
        'using claude-flow', 'with claude-flow', 'claude-flow workflow',
        'claude-flow agent', 'claude-flow orchestrat',
    ],
    'sparc': [
        'SPARC', 'sparc methodology', 'sparc framework', 'sparc-',
        'specification', 'pseudocode', 'architecture', 'refinement', 'completion',
        'sparc workflow', 'sparc_', 'sparc.md'
    ],
    'agentic-engineering': [
        '@agent-', 'agent-devops', 'agent-frontend', 'agent-backend',
        'agentic-engineering', 'ciign', 'multi-agent', 'agent orchestration'
    ],
    'coscientist': [
        'coscientist', 'co-scientist', 'scientific workflow', 'hypothesis',
        'experiment design', 'literature review', 'research assistant'
    ],
    'mcp': [
        'mcp server', 'model context protocol', 'mcp-', '@mcp/',
        'mcpServers', 'MCP tool', 'mcp integration'
    ],
    'langchain': [
        'langchain', 'LangChain', 'LCEL', 'langsmith', 'langgraph'
    ],
    'crewai': [
        'crewai', 'CrewAI', 'crew.ai', 'agent crew'
    ],
}

# Technology detection patterns (for README analysis)
TECH_PATTERNS = {
    'python': [r'\.py\b', r'python', r'pip install', r'requirements\.txt', r'pyproject\.toml'],
    'typescript': [r'\.ts\b', r'typescript', r'\.tsx\b'],
    'javascript': [r'\.js\b', r'javascript', r'node', r'npm', r'yarn'],
    'react': [r'react', r'jsx', r'tsx', r'next\.js', r'nextjs'],
    'vue': [r'vue', r'\.vue\b', r'nuxt'],
    'rust': [r'\.rs\b', r'cargo', r'rust'],
    'go': [r'\.go\b', r'golang', r'go mod'],
    'cloudflare': [r'cloudflare', r'workers', r'wrangler', r'cf-'],
    'docker': [r'docker', r'dockerfile', r'compose'],
    'kubernetes': [r'kubernetes', r'k8s', r'kubectl', r'helm'],
    'ai/ml': [r'anthropic', r'openai', r'llm', r'gpt', r'claude', r'transformer'],
    'database': [r'postgres', r'mysql', r'mongodb', r'redis', r'sqlite', r'supabase'],
}

# Project category patterns
CATEGORY_PATTERNS = {
    'ai-agent': ['agent', 'agentic', 'autonomous', 'multi-agent'],
    'scientific': ['coscientist', 'research', 'hypothesis', 'experiment', 'scientific'],
    'web-app': ['frontend', 'backend', 'fullstack', 'web app', 'dashboard'],
    'cli-tool': ['cli', 'command line', 'terminal'],
    'api': ['api', 'rest', 'graphql', 'endpoint'],
    'mobile': ['mobile', 'ios', 'android', 'react native', 'flutter'],
    'infrastructure': ['infra', 'devops', 'deploy', 'ci/cd', 'kubernetes'],
    'data': ['data', 'etl', 'pipeline', 'analytics', 'visualization'],
}


@dataclass
class ProjectAnalysis:
    """Analysis results for a single project."""
    name: str
    display_name: str  # Cleaned name without folder prefixes
    path: Optional[str] = None
    description: str = ''
    technologies: list = field(default_factory=list)
    frameworks: list = field(default_factory=list)
    category: str = ''
    tags: list = field(default_factory=list)
    related_projects: list = field(default_factory=list)
    keyword_matches: dict = field(default_factory=dict)
    confidence: float = 0.0


def detect_frameworks_in_text(text: str) -> dict[str, int]:
    """Detect framework/tool usage from text content."""
    text_lower = text.lower()
    matches = {}

    for framework, keywords in FRAMEWORK_KEYWORDS.items():
        count = 0
        for keyword in keywords:
            # Case-insensitive search
            pattern = re.compile(re.escape(keyword.lower()))
            count += len(pattern.findall(text_lower))
        if count > 0:
            matches[framework] = count

    return matches


def detect_technologies(text: str) -> list[str]:
    """Detect technologies from text content."""
    text_lower = text.lower()
    detected = []

    for tech, patterns in TECH_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                if tech not in detected:
                    detected.append(tech)
                break

    return detected


def detect_category(text: str, project_name: str) -> str:
    """Determine project category from text and name."""
    text_lower = (text + ' ' + project_name).lower()

    category_scores = {}
    for category, keywords in CATEGORY_PATTERNS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            category_scores[category] = score

    if category_scores:
        return max(category_scores, key=category_scores.get)
    return 'other'


def analyze_readme(project_path: str) -> dict:
    """Analyze a project's README file."""
    readme_names = ['README.md', 'readme.md', 'README', 'README.txt', 'readme.txt']
    readme_content = ''

    for name in readme_names:
        readme_path = Path(project_path) / name
        if readme_path.exists():
            try:
                readme_content = readme_path.read_text(encoding='utf-8', errors='ignore')[:10000]
                break
            except Exception:
                pass

    if not readme_content:
        return {}

    # Extract description (first paragraph or first few lines)
    lines = readme_content.strip().split('\n')
    description_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('!['):
            description_lines.append(line)
            if len(' '.join(description_lines)) > 200:
                break

    return {
        'content': readme_content,
        'description': ' '.join(description_lines)[:300],
        'technologies': detect_technologies(readme_content),
        'frameworks': detect_frameworks_in_text(readme_content),
    }


def analyze_jsonl_for_frameworks(jsonl_dir: Path, project_name: str) -> dict[str, int]:
    """Analyze JSONL conversation files for framework usage keywords."""
    framework_counts = defaultdict(int)

    # Find project's JSONL directory
    encoded_patterns = [
        project_name,
        project_name.replace('-', '_'),
    ]

    project_dirs = []
    if jsonl_dir.exists():
        for d in jsonl_dir.iterdir():
            if d.is_dir():
                for pattern in encoded_patterns:
                    if pattern in d.name:
                        project_dirs.append(d)
                        break

    # Sample conversation content from JSONL files
    sample_text = []
    for project_dir in project_dirs:
        for jsonl_file in list(project_dir.glob('*.jsonl'))[:10]:  # Limit files
            try:
                with open(jsonl_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        if i > 100:  # Limit lines per file
                            break
                        try:
                            msg = json.loads(line)
                            # Extract user messages
                            if msg.get('type') == 'user':
                                content = msg.get('message', {})
                                if isinstance(content, dict):
                                    blocks = content.get('content', [])
                                    if isinstance(blocks, list):
                                        for block in blocks:
                                            if isinstance(block, dict) and block.get('type') == 'text':
                                                sample_text.append(block.get('text', ''))
                                    elif isinstance(blocks, str):
                                        sample_text.append(blocks)
                        except json.JSONDecodeError:
                            pass
            except Exception:
                pass

    # Analyze sampled text
    full_text = ' '.join(sample_text)
    return detect_frameworks_in_text(full_text)


def find_related_projects(
    project_name: str,
    all_projects: list[str],
    framework_data: dict[str, dict[str, int]]
) -> list[str]:
    """Find related projects based on shared frameworks and naming."""
    related = []

    # Get this project's frameworks
    my_frameworks = set(framework_data.get(project_name, {}).keys())

    for other in all_projects:
        if other == project_name:
            continue

        # Check for naming similarity (shared prefix)
        name_parts = project_name.lower().replace('_', '-').split('-')
        other_parts = other.lower().replace('_', '-').split('-')

        # Shared meaningful prefix (more than 3 chars)
        shared_prefix = []
        for p1, p2 in zip(name_parts, other_parts):
            if p1 == p2 and len(p1) > 2:
                shared_prefix.append(p1)
            else:
                break

        if len(shared_prefix) > 0 and shared_prefix[0] not in ('the', 'my', 'new'):
            related.append(other)
            continue

        # Check for shared frameworks
        other_frameworks = set(framework_data.get(other, {}).keys())
        if my_frameworks & other_frameworks:
            # Only add if they share significant frameworks (not just common ones)
            significant_shared = my_frameworks & other_frameworks - {'python', 'javascript', 'typescript'}
            if significant_shared:
                related.append(other)

    return related[:10]  # Limit to 10 related projects


def clean_project_name(encoded_name: str, known_folders: list[str] = None) -> str:
    """Clean project name by removing known folder prefixes."""
    if known_folders is None:
        known_folders = [
            'sundai', 'projects', 'repos', 'code', 'src', 'dev', 'development',
            'work', 'workspace', 'github', 'gitlab', 'bitbucket', 'clones',
            'documents', 'desktop', 'downloads', 'go', 'rust', 'python',
            'users', 'home', 'pierre', 'root'  # User-specific
        ]

    name = encoded_name

    # Remove leading dashes and split
    if name.startswith('-'):
        name = name[1:]

    parts = name.replace('_', '-').split('-')

    # Remove known folder prefixes from the beginning
    while parts and parts[0].lower() in known_folders:
        parts = parts[1:]

    if parts:
        return '-'.join(parts)
    return encoded_name


def analyze_all_projects(
    projects: list[dict],
    claude_dir: Path = None,
    project_base_paths: list[str] = None
) -> list[ProjectAnalysis]:
    """Analyze all projects and return analysis results."""
    if claude_dir is None:
        claude_dir = Path.home() / '.claude'

    jsonl_dir = claude_dir / 'projects'
    results = []

    # First pass: collect framework data from JSONL
    project_names = [p.get('name', '') for p in projects]
    framework_data = {}

    for proj in projects:
        name = proj.get('name', '')
        frameworks = analyze_jsonl_for_frameworks(jsonl_dir, name)
        framework_data[name] = frameworks

    # Second pass: analyze each project
    for proj in projects:
        name = proj.get('name', '')
        full_path = proj.get('full_path', '')

        analysis = ProjectAnalysis(
            name=name,
            display_name=clean_project_name(name),
            path=full_path,
        )

        # Try to find and analyze README
        if project_base_paths:
            for base in project_base_paths:
                # Try to find the actual project directory
                possible_paths = [
                    Path(base) / name,
                    Path(base) / name.replace('-', '_'),
                    Path(base) / clean_project_name(name),
                ]
                for ppath in possible_paths:
                    if ppath.exists() and ppath.is_dir():
                        readme_info = analyze_readme(str(ppath))
                        if readme_info:
                            analysis.description = readme_info.get('description', '')
                            analysis.technologies = readme_info.get('technologies', [])
                            # Merge framework detections
                            for fw, count in readme_info.get('frameworks', {}).items():
                                if fw in framework_data[name]:
                                    framework_data[name][fw] += count
                                else:
                                    framework_data[name][fw] = count
                        break

        # Apply framework data
        analysis.frameworks = list(framework_data.get(name, {}).keys())
        analysis.keyword_matches = framework_data.get(name, {})

        # Detect technologies from JSONL if not from README
        if not analysis.technologies:
            analysis.technologies = detect_technologies(name)

        # Determine category
        analysis.category = detect_category(
            analysis.description + ' ' + ' '.join(analysis.frameworks),
            name
        )

        # Find related projects
        analysis.related_projects = find_related_projects(
            name, project_names, framework_data
        )

        # Calculate confidence score
        confidence = 0.0
        if analysis.description:
            confidence += 0.3
        if analysis.technologies:
            confidence += 0.2
        if analysis.frameworks:
            confidence += 0.3
        if analysis.category != 'other':
            confidence += 0.2
        analysis.confidence = confidence

        results.append(analysis)

    return results


def group_projects_smart(analyses: list[ProjectAnalysis]) -> dict[str, list[str]]:
    """Smart grouping based on analysis results."""
    groups = defaultdict(list)

    # Group by detected frameworks
    for analysis in analyses:
        for framework in analysis.frameworks:
            groups[f'framework:{framework}'].append(analysis.name)

    # Group by category
    for analysis in analyses:
        if analysis.category and analysis.category != 'other':
            groups[f'category:{analysis.category}'].append(analysis.name)

    # Group by related projects (cluster detection)
    # Find clusters of related projects
    visited = set()
    for analysis in analyses:
        if analysis.name in visited:
            continue

        cluster = {analysis.name}
        to_check = list(analysis.related_projects)

        while to_check:
            rel = to_check.pop(0)
            if rel not in cluster:
                cluster.add(rel)
                # Find the related analysis
                for other in analyses:
                    if other.name == rel:
                        to_check.extend([r for r in other.related_projects if r not in cluster])
                        break

        if len(cluster) > 1:
            # Name the cluster by common prefix or most common framework
            cluster_names = list(cluster)
            # Try to find common prefix
            first_parts = cluster_names[0].replace('_', '-').split('-')
            common_prefix = []
            for i, part in enumerate(first_parts):
                if all(
                    n.replace('_', '-').split('-')[i:i+1] == [part]
                    for n in cluster_names
                    if len(n.replace('_', '-').split('-')) > i
                ):
                    common_prefix.append(part)
                else:
                    break

            if common_prefix and common_prefix[0].lower() not in ('the', 'my', 'new', 'test'):
                cluster_name = '-'.join(common_prefix)
            else:
                # Use most common framework
                all_frameworks = []
                for name in cluster:
                    for a in analyses:
                        if a.name == name:
                            all_frameworks.extend(a.frameworks)
                if all_frameworks:
                    cluster_name = Counter(all_frameworks).most_common(1)[0][0]
                else:
                    cluster_name = 'related'

            groups[f'cluster:{cluster_name}'].extend(cluster)
            visited.update(cluster)

    # Filter out small groups
    return {k: list(set(v)) for k, v in groups.items() if len(set(v)) > 1}


def run_repomix_analysis(repo_path: str) -> Optional[str]:
    """Run repomix on a repository to get AI-friendly summary."""
    try:
        # Check if repomix is installed
        result = subprocess.run(
            ['npx', 'repomix', '--version'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return None

        # Run repomix on the repo
        result = subprocess.run(
            ['npx', 'repomix', repo_path, '--output', '-', '--style', 'plain'],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            return result.stdout[:50000]  # Limit output size
        return None

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


if __name__ == '__main__':
    # Test the analyzer
    import sys

    # Load test data
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        # Try to load from default location
        try:
            with open('/tmp/claude_data.json') as f:
                content = f.read()
                json_start = content.find('{')
                data = json.loads(content[json_start:])
        except FileNotFoundError:
            print("No data file found. Run analyzer.py first.")
            sys.exit(1)

    projects = data.get('top_projects', [])
    print(f"Analyzing {len(projects)} projects...\n")

    # Analyze with project paths
    analyses = analyze_all_projects(
        projects,
        project_base_paths=[str(Path.home() / 'sundai'), str(Path.home() / 'projects')]
    )

    # Print results
    for analysis in analyses[:15]:
        print(f"\n{'='*60}")
        print(f"Project: {analysis.name}")
        print(f"Display: {analysis.display_name}")
        print(f"Category: {analysis.category}")
        print(f"Technologies: {', '.join(analysis.technologies) or 'N/A'}")
        print(f"Frameworks: {', '.join(analysis.frameworks) or 'N/A'}")
        print(f"Keyword matches: {analysis.keyword_matches}")
        print(f"Related: {', '.join(analysis.related_projects[:5]) or 'N/A'}")
        print(f"Confidence: {analysis.confidence:.0%}")

    # Smart grouping
    print(f"\n\n{'='*60}")
    print("SMART GROUPINGS:")
    print('='*60)
    groups = group_projects_smart(analyses)
    for group_name, members in sorted(groups.items(), key=lambda x: -len(x[1])):
        print(f"\n{group_name}: ({len(members)} projects)")
        for m in members[:8]:
            print(f"  - {m}")
        if len(members) > 8:
            print(f"  ... and {len(members) - 8} more")
