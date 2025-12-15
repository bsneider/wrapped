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

# Import patterns from centralized patterns.py
from patterns import (
    FRAMEWORK_KEYWORDS,
    PROJECT_COMPONENTS,
    CODING_CONCEPTS,
    TECH_PATTERNS,
    CATEGORY_PATTERNS,
    FRAMEWORK_ICONS,
    COMPONENT_ICONS,
    CONCEPT_ICONS,
    CATEGORY_PURPOSES,
    DOMAIN_HINTS,
)


# All patterns are now imported from patterns.py above
# The centralized patterns.py file contains:
# - FRAMEWORK_KEYWORDS: Detection patterns for 150+ frameworks, tools, and services
# - PROJECT_COMPONENTS: Component types (chrome-extension, api-server, etc.)
# - CODING_CONCEPTS: Architecture and coding patterns
# - TECH_PATTERNS: Technology detection for README analysis
# - CATEGORY_PATTERNS: Project categorization patterns
# - *_ICONS: Display icons for each category
# - DOMAIN_HINTS: Summary generation helpers
# - CATEGORY_PURPOSES: Category purpose descriptions


@dataclass
class ProjectAnalysis:
    """Analysis results for a single project."""
    name: str
    display_name: str  # Cleaned name without folder prefixes
    path: Optional[str] = None
    description: str = ''
    summary: str = ''  # 5-word summary
    technologies: list = field(default_factory=list)
    frameworks: list = field(default_factory=list)
    components: list = field(default_factory=list)  # chrome-extension, api-server, etc.
    coding_concepts: list = field(default_factory=list)  # Architecture, patterns, practices
    category: str = ''
    tags: list = field(default_factory=list)
    related_projects: list = field(default_factory=list)
    keyword_matches: dict = field(default_factory=dict)
    component_matches: dict = field(default_factory=dict)  # Component types detected
    concept_matches: dict = field(default_factory=dict)  # Coding concepts detected
    confidence: float = 0.0


def detect_frameworks_in_text(text: str) -> dict[str, int]:
    """Detect framework/tool usage from text content (case-insensitive)."""
    text_lower = text.lower()
    matches = {}

    for framework, keywords in FRAMEWORK_KEYWORDS.items():
        count = 0
        for keyword in keywords:
            # Case-insensitive search
            keyword_lower = keyword.lower()
            # Use word boundary for short keywords to reduce false positives
            if len(keyword_lower) <= 3:
                pattern = re.compile(r'\b' + re.escape(keyword_lower) + r'\b')
            else:
                pattern = re.compile(re.escape(keyword_lower))
            count += len(pattern.findall(text_lower))
        if count > 0:
            matches[framework] = count

    return matches


def detect_coding_concepts(text: str) -> dict[str, int]:
    """Detect coding concepts, patterns and practices from text (case-insensitive)."""
    text_lower = text.lower()
    matches = {}

    for concept, keywords in CODING_CONCEPTS.items():
        count = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            pattern = re.compile(re.escape(keyword_lower))
            count += len(pattern.findall(text_lower))
        if count > 0:
            matches[concept] = count

    return matches


def detect_components(text: str) -> dict[str, int]:
    """Detect project component types from text (case-insensitive)."""
    text_lower = text.lower()
    matches = {}

    for component, keywords in PROJECT_COMPONENTS.items():
        count = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            pattern = re.compile(re.escape(keyword_lower))
            count += len(pattern.findall(text_lower))
        if count > 0:
            matches[component] = count

    return matches


def generate_llm_summary(
    name: str,
    frameworks: list,
    components: list,
    category: str,
    description: str = ''
) -> str:
    """Generate a project summary using Claude Haiku (cheap and fast)."""
    try:
        import anthropic

        client = anthropic.Anthropic()

        # Build context for the LLM
        context_parts = [f"Project name: {name}"]
        if description:
            context_parts.append(f"Description: {description[:200]}")
        if frameworks:
            context_parts.append(f"Technologies: {', '.join(frameworks[:8])}")
        if components:
            context_parts.append(f"Components: {', '.join(components[:5])}")
        if category:
            context_parts.append(f"Category: {category}")

        context = "\n".join(context_parts)

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=50,
            messages=[
                {
                    "role": "user",
                    "content": f"Generate a 5-7 word summary explaining what this software project does. Be specific about its purpose.\n\n{context}\n\nSummary (5-7 words only):"
                }
            ]
        )

        summary = message.content[0].text.strip()
        # Clean up any quotes or extra formatting
        summary = summary.strip('"\'').strip()
        # Ensure it's not too long
        words = summary.split()[:8]
        return ' '.join(words)

    except Exception as e:
        # Fall back to heuristic-based summary
        return None


def generate_project_summary(
    name: str,
    frameworks: list,
    components: list,
    concepts: list,
    category: str,
    description: str = '',
    use_llm: bool = False
) -> str:
    """Generate a concise ~5-word summary explaining what the project does."""

    # Try LLM-based summary if requested
    if use_llm:
        llm_summary = generate_llm_summary(name, frameworks, components, category, description)
        if llm_summary:
            return llm_summary

    # If we have a good description, extract key info from it
    if description and len(description) > 20:
        # Take first sentence or first ~50 chars
        first_sentence = description.split('.')[0].strip()
        if len(first_sentence) <= 60:
            return first_sentence
        # Truncate intelligently
        words = first_sentence.split()[:8]
        return ' '.join(words) + '...'

    # Build summary from detected components and purpose
    # Component prefixes for summary generation
    component_prefixes = {
        'chrome-extension': 'Browser extension for',
        'vscode-extension': 'VSCode extension for',
        'web-frontend': 'Web interface for',
        'mobile-app': 'Mobile app for',
        'desktop-app': 'Desktop application for',
        'api-server': 'API backend for',
        'graphql-api': 'GraphQL API for',
        'websocket-server': 'Realtime service for',
        'ml-pipeline': 'ML pipeline for',
        'data-ingestion': 'Data ingestion system for',
        'knowledge-graph': 'Knowledge graph for',
        'rag-system': 'RAG system for',
        'kubernetes': 'K8s-deployed',
        'docker-compose': 'Containerized',
        'ci-cd-pipeline': 'CI/CD for',
        'cli-tool': 'CLI tool for',
        'sdk-library': 'SDK/Library for',
        'mcp-server': 'MCP server for',
        'agent-system': 'Multi-agent system for',
    }

    # Use imported DOMAIN_HINTS and CATEGORY_PURPOSES from patterns.py

    summary_parts = []

    # Start with component type
    if components:
        top_comp = components[0]
        if top_comp in component_prefixes:
            summary_parts.append(component_prefixes[top_comp])

    # Add domain/purpose from frameworks
    for fw in frameworks[:3]:
        if fw in DOMAIN_HINTS:
            summary_parts.append(DOMAIN_HINTS[fw])
            break

    # Or from category
    if not summary_parts or len(summary_parts) == 1:
        if category in CATEGORY_PURPOSES:
            summary_parts.append(CATEGORY_PURPOSES[category])

    # Add specific functionality hints from name
    name_lower = name.lower()
    if 'swarm' in name_lower:
        summary_parts.append('swarm orchestration')
    elif 'flow' in name_lower:
        summary_parts.append('workflow automation')
    elif 'ingestion' in name_lower or 'data-ingestion' in components:
        summary_parts.append('data capture')
    elif 'graph' in name_lower or 'knowledge-graph' in components:
        summary_parts.append('knowledge graphs')
    elif 'chat' in name_lower:
        summary_parts.append('conversational AI')
    elif 'sync' in name_lower:
        summary_parts.append('data synchronization')

    # Construct final summary
    if summary_parts:
        # Join and clean up
        summary = ' '.join(summary_parts[:3])
        # Remove duplicate words
        words = summary.split()
        seen = set()
        unique_words = []
        for w in words:
            w_lower = w.lower()
            if w_lower not in seen:
                seen.add(w_lower)
                unique_words.append(w)
        return ' '.join(unique_words[:7])

    # Fallback: humanize the project name
    name_words = name.replace('-', ' ').replace('_', ' ').title()
    return name_words


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


def analyze_jsonl_for_frameworks(jsonl_dir: Path, project_name: str) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    """Analyze JSONL conversation files for framework usage, coding concepts, and components.

    Returns:
        tuple: (framework_counts, concept_counts, component_counts)
    """
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
                            # Also extract assistant messages for more context
                            elif msg.get('type') == 'assistant':
                                content = msg.get('message', {})
                                if isinstance(content, dict):
                                    blocks = content.get('content', [])
                                    if isinstance(blocks, list):
                                        for block in blocks:
                                            if isinstance(block, dict) and block.get('type') == 'text':
                                                sample_text.append(block.get('text', ''))
                        except json.JSONDecodeError:
                            pass
            except Exception:
                pass

    # Analyze sampled text
    full_text = ' '.join(sample_text)
    framework_counts = detect_frameworks_in_text(full_text)
    concept_counts = detect_coding_concepts(full_text)
    component_counts = detect_components(full_text)

    return framework_counts, concept_counts, component_counts


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

    # First pass: collect framework, concept, and component data from JSONL
    project_names = [p.get('name', '') for p in projects]
    framework_data = {}
    concept_data = {}
    component_data = {}

    for proj in projects:
        name = proj.get('name', '')
        frameworks, concepts, components = analyze_jsonl_for_frameworks(jsonl_dir, name)
        framework_data[name] = frameworks
        concept_data[name] = concepts
        component_data[name] = components

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

        # Apply coding concepts data
        analysis.coding_concepts = list(concept_data.get(name, {}).keys())
        analysis.concept_matches = concept_data.get(name, {})

        # Apply component data
        analysis.components = list(component_data.get(name, {}).keys())
        analysis.component_matches = component_data.get(name, {})

        # Detect technologies from JSONL if not from README
        if not analysis.technologies:
            analysis.technologies = detect_technologies(name)

        # Determine category
        analysis.category = detect_category(
            analysis.description + ' ' + ' '.join(analysis.frameworks),
            name
        )

        # Generate 5-word summary
        analysis.summary = generate_project_summary(
            name,
            analysis.frameworks,
            analysis.components,
            analysis.coding_concepts,
            analysis.category,
            analysis.description
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
        if analysis.coding_concepts:
            confidence += 0.1
        if analysis.category != 'other':
            confidence += 0.1
        analysis.confidence = confidence

        results.append(analysis)

    return results


def group_projects_smart(analyses: list[ProjectAnalysis]) -> dict[str, list[str]]:
    """Smart grouping based on analysis results."""
    groups = defaultdict(list)

    # Group by detected frameworks (normalize to lowercase for consistency)
    for analysis in analyses:
        for framework in analysis.frameworks:
            groups[f'framework:{framework.lower()}'].append(analysis.name)

    # Group by category (normalize to lowercase)
    for analysis in analyses:
        if analysis.category and analysis.category != 'other':
            groups[f'category:{analysis.category.lower()}'].append(analysis.name)

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
