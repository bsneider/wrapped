#!/usr/bin/env python3
"""
Prompt DNA Analyzer - Extract user's prompting patterns and preferences.

Analyzes actual prompt content to identify:
- Repeated phrases (catchphrases)
- House rules (recurring instructions)
- Communication style
- Output format preferences
- Role assignment patterns

This enables:
1. "Your Prompt DNA" section in wrapped report
2. Auto-generated CLAUDE.md based on detected preferences
"""

import json
import re
import os
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PromptDNA:
    """Analysis results for a user's prompting patterns."""

    # Message counts
    total_prompts_analyzed: int = 0
    total_words: int = 0

    # Catchphrases - repeated multi-word phrases
    top_catchphrases: list = field(default_factory=list)  # [(phrase, count), ...]

    # House rules - recurring instructions
    house_rules: list = field(default_factory=list)  # [(rule, count), ...]

    # Role assignments - "You are a..."
    role_assignments: list = field(default_factory=list)  # [(role, count), ...]

    # Output format preferences
    output_formats: dict = field(default_factory=dict)  # {format: count}

    # Communication style
    avg_prompt_length_words: float = 0.0
    avg_prompt_length_chars: float = 0.0
    question_ratio: float = 0.0  # % of prompts that are questions
    directive_ratio: float = 0.0  # % that start with imperatives

    # Style classification
    prompt_style: str = ""  # "exploratory", "directive", "structured", etc.
    prompt_personality: str = ""  # Fun personality name
    prompt_personality_description: str = ""
    prompt_personality_icon: str = ""

    # Structural patterns
    uses_xml_tags: int = 0
    uses_numbered_lists: int = 0
    uses_markdown: int = 0
    uses_json_requests: int = 0
    uses_examples: int = 0

    # Tech stack mentions
    tech_mentions: dict = field(default_factory=dict)  # {tech: count}

    # Constraint patterns
    constraint_patterns: list = field(default_factory=list)  # ["max X chars", "under Y lines"]

    # Opening patterns - how prompts typically start
    opening_patterns: dict = field(default_factory=dict)  # {pattern_type: count}
    top_opening_phrase: str = ""

    # Quality signals (based on research)
    clarity_score: float = 0.0  # 0-1, based on specificity markers
    structure_score: float = 0.0  # 0-1, based on formatting
    context_score: float = 0.0  # 0-1, based on context provision


# Common instruction patterns to detect "house rules"
INSTRUCTION_PATTERNS = [
    (r'\balways\s+(\w+(?:\s+\w+){0,4})', 'always'),
    (r'\bnever\s+(\w+(?:\s+\w+){0,4})', 'never'),
    (r'\bdon\'?t\s+(\w+(?:\s+\w+){0,4})', 'dont'),
    (r'\bdo\s+not\s+(\w+(?:\s+\w+){0,4})', 'do_not'),
    (r'\bmust\s+(\w+(?:\s+\w+){0,4})', 'must'),
    (r'\bshould\s+(\w+(?:\s+\w+){0,4})', 'should'),
    (r'\buse\s+(\w+(?:\s+\w+){0,3})', 'use'),
    (r'\bavoid\s+(\w+(?:\s+\w+){0,3})', 'avoid'),
    (r'\bkeep\s+it\s+(\w+)', 'keep_it'),
    (r'\bbe\s+(concise|brief|specific|detailed|thorough)', 'be'),
    (r'\bno\s+(\w+(?:\s+\w+){0,2})', 'no'),
    (r'\bwithout\s+(\w+(?:\s+\w+){0,2})', 'without'),
    (r'\bonly\s+(\w+(?:\s+\w+){0,3})', 'only'),
    (r'\bexclude\s+(\w+(?:\s+\w+){0,2})', 'exclude'),
    (r'\binclude\s+(\w+(?:\s+\w+){0,2})', 'include'),
    (r'\bensure\s+(\w+(?:\s+\w+){0,3})', 'ensure'),
    (r'\bmake\s+sure\s+(\w+(?:\s+\w+){0,3})', 'make_sure'),
]

# Tech stack keywords to detect
TECH_KEYWORDS = {
    # Languages
    'python', 'javascript', 'typescript', 'rust', 'go', 'golang', 'java', 'kotlin',
    'swift', 'ruby', 'php', 'c++', 'cpp', 'c#', 'csharp', 'scala', 'elixir',
    # Frameworks
    'react', 'vue', 'angular', 'svelte', 'nextjs', 'next.js', 'nuxt', 'remix',
    'django', 'flask', 'fastapi', 'express', 'nestjs', 'rails', 'laravel',
    'spring', 'spring boot', 'actix', 'rocket', 'gin', 'fiber',
    # Databases
    'postgresql', 'postgres', 'mysql', 'mongodb', 'redis', 'elasticsearch',
    'sqlite', 'dynamodb', 'cassandra', 'neo4j', 'supabase', 'firebase',
    # Cloud/Infra
    'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'k8s', 'terraform',
    'vercel', 'netlify', 'heroku', 'cloudflare',
    # AI/ML
    'openai', 'anthropic', 'claude', 'gpt', 'llm', 'langchain', 'llamaindex',
    'pytorch', 'tensorflow', 'huggingface', 'transformers',
    # Tools
    'git', 'github', 'gitlab', 'npm', 'yarn', 'pnpm', 'pip', 'cargo',
    'webpack', 'vite', 'esbuild', 'tailwind', 'sass', 'postcss',
}

# Output format patterns
OUTPUT_FORMAT_PATTERNS = [
    (r'\bjson\s*format', 'JSON'),
    (r'\brespond\s+(?:with\s+)?(?:only\s+)?(?:a\s+)?json', 'JSON'),
    (r'\boutput\s+(?:as\s+)?json', 'JSON'),
    (r'\bmarkdown\b', 'Markdown'),
    (r'\byaml\b', 'YAML'),
    (r'\bxml\b', 'XML'),
    (r'\bcsv\b', 'CSV'),
    (r'\bbullet\s*(?:points?|list)', 'Bullet list'),
    (r'\bnumbered\s+list', 'Numbered list'),
    (r'\btable\s+format', 'Table'),
    (r'\bcode\s+block', 'Code block'),
    (r'\bplain\s+text', 'Plain text'),
    (r'\bone\s+(?:word|line|sentence)', 'Single item'),
    (r'\brespond\s+with\s+only', 'Constrained'),
]

# Role assignment pattern
ROLE_PATTERN = re.compile(
    r'you\s+are\s+(?:a|an|the)?\s*([^.!?\n]{3,50}?)(?:\.|!|\?|$|\n)',
    re.IGNORECASE
)

# Template detection patterns
TEMPLATE_INDICATORS = [
    r'\(\d+\s*pts?\)',           # (5pts), (10 pt)
    r'\d+\s*points?',            # 5 points
    r'/\d+\)?',                  # /10, /5)
    r'score:',                   # score:
    r'rating:',                  # rating:
    r'\byes\s*/\s*no\b',         # yes/no
    r'^\s*\d+[\.\)]\s',          # numbered list at start
    r'\[\s*[x✓✗ ]\s*\]',        # checkboxes [x] [ ]
    r'criteria:',                # criteria:
    r'rubric',                   # rubric
    r'checklist',                # checklist
    r'evaluate',                 # evaluate
    r'assessment',               # assessment
]


def detect_template_context(message: str, match_pos: int, window: int = 100) -> bool:
    """Check if a match appears within a template/structured context."""
    # Get surrounding context
    start = max(0, match_pos - window)
    end = min(len(message), match_pos + window)
    context = message[start:end].lower()

    for pattern in TEMPLATE_INDICATORS:
        if re.search(pattern, context, re.IGNORECASE | re.MULTILINE):
            return True
    return False


# Stopwords to filter from n-grams
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
    'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
    'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
    'than', 'too', 'very', 'just', 'also', 'now', 'here', 'there',
}


def extract_user_messages(claude_dir: Path) -> list[str]:
    """Extract all user message content from JSONL files."""
    messages = []
    projects_dir = claude_dir / 'projects'

    if not projects_dir.exists():
        return messages

    for jsonl_file in projects_dir.glob('**/*.jsonl'):
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        msg = json.loads(line)
                        if msg.get('type') == 'user':
                            content = msg.get('message', {})
                            if isinstance(content, dict):
                                text = content.get('content', '')
                                if isinstance(text, str) and len(text) > 10:
                                    messages.append(text)
                            elif isinstance(content, str) and len(content) > 10:
                                messages.append(content)
                    except json.JSONDecodeError:
                        continue
        except (IOError, OSError):
            continue

    return messages


def extract_ngrams(text: str, n: int) -> list[str]:
    """Extract n-grams from text."""
    # Tokenize: lowercase, keep alphanumeric and common punctuation
    words = re.findall(r'\b[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*\b', text.lower())

    # Filter very short words and stopwords for n > 2
    if n > 2:
        words = [w for w in words if len(w) > 2 and w not in STOPWORDS]

    ngrams = []
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        # Filter out ngrams that are mostly stopwords
        ngram_words = ngram.split()
        non_stop = sum(1 for w in ngram_words if w not in STOPWORDS)
        if non_stop >= n // 2 + 1:  # At least half non-stopwords
            ngrams.append(ngram)

    return ngrams


def extract_catchphrases(messages: list[str], min_count: int = 3) -> list[tuple[str, int]]:
    """Extract repeated multi-word phrases (catchphrases)."""
    all_ngrams = Counter()

    for msg in messages:
        # Extract 3-grams, 4-grams, and 5-grams
        for n in [3, 4, 5]:
            ngrams = extract_ngrams(msg, n)
            all_ngrams.update(ngrams)

    # Filter by minimum count and remove subphrases
    candidates = [(phrase, count) for phrase, count in all_ngrams.items()
                  if count >= min_count]

    # Sort by count * length (prefer longer, more frequent phrases)
    candidates.sort(key=lambda x: x[1] * len(x[0].split()), reverse=True)

    # Remove subphrases (if "keep it simple" appears, don't also show "keep it")
    final = []
    seen_parts = set()
    for phrase, count in candidates[:50]:  # Check top 50
        words = phrase.split()
        # Check if this is a subphrase of something we've already included
        is_subphrase = False
        for seen in seen_parts:
            if phrase in seen:
                is_subphrase = True
                break

        if not is_subphrase:
            final.append((phrase, count))
            seen_parts.add(phrase)
            if len(final) >= 10:
                break

    return final


def extract_house_rules(messages: list[str], min_count: int = 2) -> list[tuple[str, int, str]]:
    """Extract recurring instructions (house rules).

    Returns list of (rule, count, source_type) where source_type is 'template' or 'freeform'.
    """
    rules = Counter()
    rule_template_counts = Counter()  # Track how often each rule appears in template context

    for msg in messages:
        msg_lower = msg.lower()
        for pattern, rule_type in INSTRUCTION_PATTERNS:
            for match_obj in re.finditer(pattern, msg_lower):
                match = match_obj.group(1)
                # Clean up the match
                rule = match.strip()
                if len(rule) > 3 and len(rule) < 50:
                    # Format nicely
                    if rule_type == 'always':
                        rule_text = f"always {rule}"
                    elif rule_type == 'never':
                        rule_text = f"never {rule}"
                    elif rule_type in ('dont', 'do_not'):
                        rule_text = f"don't {rule}"
                    elif rule_type == 'use':
                        rule_text = f"use {rule}"
                    elif rule_type == 'avoid':
                        rule_text = f"avoid {rule}"
                    elif rule_type == 'keep_it':
                        rule_text = f"keep it {rule}"
                    elif rule_type == 'be':
                        rule_text = f"be {rule}"
                    elif rule_type == 'no':
                        rule_text = f"no {rule}"
                    elif rule_type == 'without':
                        rule_text = f"without {rule}"
                    elif rule_type == 'only':
                        rule_text = f"only {rule}"
                    else:
                        rule_text = f"{rule_type} {rule}"

                    rules[rule_text] += 1

                    # Check if this occurrence is in a template context
                    if detect_template_context(msg, match_obj.start()):
                        rule_template_counts[rule_text] += 1

    # Filter by minimum count and determine source type
    filtered = []
    for rule, count in rules.items():
        if count >= min_count:
            template_count = rule_template_counts.get(rule, 0)
            # If >50% of occurrences are in template context, mark as template
            source_type = 'template' if template_count > count * 0.5 else 'freeform'
            filtered.append((rule, count, source_type))

    filtered.sort(key=lambda x: x[1], reverse=True)
    return filtered[:15]


def extract_role_assignments(messages: list[str], min_count: int = 2) -> list[tuple[str, int, str]]:
    """Extract role assignments like 'You are a...'

    Returns list of (role, count, source_type) where source_type is 'template' or 'freeform'.
    """
    roles = Counter()
    role_template_counts = Counter()

    for msg in messages:
        for match_obj in ROLE_PATTERN.finditer(msg):
            match = match_obj.group(1)
            role = match.strip().lower()
            # Clean up common suffixes
            role = re.sub(r'\s+who\s.*$', '', role)
            role = re.sub(r'\s+that\s.*$', '', role)
            role = re.sub(r'\s+specializing\s.*$', '', role)
            if len(role) > 5 and len(role) < 60:
                roles[role] += 1
                # Check template context
                if detect_template_context(msg, match_obj.start()):
                    role_template_counts[role] += 1

    filtered = []
    for role, count in roles.items():
        if count >= min_count:
            template_count = role_template_counts.get(role, 0)
            source_type = 'template' if template_count > count * 0.5 else 'freeform'
            filtered.append((role, count, source_type))

    filtered.sort(key=lambda x: x[1], reverse=True)
    return filtered[:10]


def extract_output_formats(messages: list[str]) -> dict[str, int]:
    """Detect requested output formats."""
    formats = Counter()

    for msg in messages:
        msg_lower = msg.lower()
        for pattern, format_name in OUTPUT_FORMAT_PATTERNS:
            if re.search(pattern, msg_lower):
                formats[format_name] += 1

    return dict(formats)


def extract_tech_mentions(messages: list[str]) -> dict[str, int]:
    """Extract technology stack mentions."""
    tech = Counter()

    for msg in messages:
        msg_lower = msg.lower()
        for keyword in TECH_KEYWORDS:
            # Use word boundaries
            if re.search(rf'\b{re.escape(keyword)}\b', msg_lower):
                # Normalize some variants
                normalized = keyword.replace('.', '').replace(' ', '')
                if normalized in ('nextjs', 'next'):
                    normalized = 'nextjs'
                elif normalized in ('golang', 'go'):
                    normalized = 'go'
                elif normalized in ('postgresql', 'postgres'):
                    normalized = 'postgresql'
                tech[normalized] += 1

    return dict(tech.most_common(20))


def analyze_communication_style(messages: list[str]) -> dict:
    """Analyze communication style patterns."""
    if not messages:
        return {}

    total_words = 0
    total_chars = 0
    questions = 0
    directives = 0
    xml_tags = 0
    numbered_lists = 0
    markdown = 0
    json_requests = 0
    examples = 0

    opening_patterns = Counter()

    directive_starters = {
        'write', 'create', 'make', 'build', 'generate', 'fix', 'update',
        'add', 'remove', 'delete', 'change', 'modify', 'implement',
        'explain', 'describe', 'list', 'show', 'find', 'search',
        'analyze', 'review', 'check', 'test', 'run', 'execute',
    }

    for msg in messages:
        words = msg.split()
        total_words += len(words)
        total_chars += len(msg)

        # Question detection
        if '?' in msg:
            questions += 1

        # Directive detection (starts with imperative verb)
        first_word = words[0].lower().rstrip(':,') if words else ''
        if first_word in directive_starters:
            directives += 1
            opening_patterns['directive'] += 1
        elif msg.strip().startswith(('How ', 'What ', 'Why ', 'When ', 'Where ', 'Can ', 'Could ')):
            opening_patterns['question'] += 1
        elif msg.strip().startswith(('I ', 'I\'m ', 'I\'ve ')):
            opening_patterns['first_person'] += 1
        elif msg.strip().startswith(('You are', 'Act as', 'Pretend')):
            opening_patterns['role_assignment'] += 1
        elif msg.strip().startswith(('Here', 'This', 'The ')):
            opening_patterns['contextual'] += 1

        # Structure detection
        if re.search(r'<\w+>', msg):
            xml_tags += 1
        if re.search(r'^\s*\d+[\.\)]\s', msg, re.MULTILINE):
            numbered_lists += 1
        if re.search(r'\*\*|##|```', msg):
            markdown += 1
        if re.search(r'json|JSON', msg) and re.search(r'\{|\[', msg):
            json_requests += 1
        if re.search(r'example:|for example|e\.g\.|such as:', msg, re.IGNORECASE):
            examples += 1

    n = len(messages)

    return {
        'avg_prompt_length_words': total_words / n if n else 0,
        'avg_prompt_length_chars': total_chars / n if n else 0,
        'question_ratio': questions / n if n else 0,
        'directive_ratio': directives / n if n else 0,
        'xml_tags': xml_tags,
        'numbered_lists': numbered_lists,
        'markdown': markdown,
        'json_requests': json_requests,
        'examples': examples,
        'opening_patterns': dict(opening_patterns),
    }


def classify_prompt_personality(dna: PromptDNA) -> tuple[str, str, str]:
    """Classify user into a prompt personality type."""

    personalities = {
        'the_architect': {
            'triggers': lambda d: d.uses_numbered_lists > 10 or d.uses_xml_tags > 5,
            'name': 'The Architect',
            'desc': 'You think in systems. Every prompt is a blueprint.',
            'icon': '🏗️',
        },
        'the_explorer': {
            'triggers': lambda d: d.question_ratio > 0.5,
            'name': 'The Explorer',
            'desc': 'Curiosity drives your prompts. Questions lead to discoveries.',
            'icon': '🔍',
        },
        'the_commander': {
            'triggers': lambda d: d.directive_ratio > 0.6 and d.avg_prompt_length_words < 50,
            'name': 'The Commander',
            'desc': 'Direct and decisive. You know exactly what you want.',
            'icon': '⚔️',
        },
        'the_novelist': {
            'triggers': lambda d: d.avg_prompt_length_words > 150,
            'name': 'The Novelist',
            'desc': 'Context is king. You leave nothing to chance.',
            'icon': '📚',
        },
        'the_minimalist': {
            'triggers': lambda d: d.avg_prompt_length_words < 30,
            'name': 'The Minimalist',
            'desc': 'Less is more. Every word earns its place.',
            'icon': '✨',
        },
        'the_perfectionist': {
            'triggers': lambda d: len(d.house_rules) > 5,
            'name': 'The Perfectionist',
            'desc': 'Rules and constraints define quality. Standards matter.',
            'icon': '💎',
        },
        'the_shapeshifter': {
            'triggers': lambda d: len(d.role_assignments) > 3,
            'name': 'The Shapeshifter',
            'desc': 'You summon experts at will. Every role serves a purpose.',
            'icon': '🎭',
        },
        'the_coder': {
            'triggers': lambda d: d.uses_json_requests > 5 or d.uses_markdown > 10,
            'name': 'The Coder',
            'desc': 'Structured output, structured thinking. Code is your canvas.',
            'icon': '💻',
        },
    }

    # Check triggers in order of specificity
    for key, p in personalities.items():
        if p['triggers'](dna):
            return p['name'], p['desc'], p['icon']

    # Default
    return 'The Pragmatist', 'Adaptable and practical. The right tool for each job.', '🎯'


def calculate_quality_scores(messages: list[str], dna: PromptDNA) -> tuple[float, float, float]:
    """Calculate prompt quality scores based on research findings."""

    # Clarity score: specificity markers, clear instructions
    clarity_signals = 0
    structure_signals = 0
    context_signals = 0

    clarity_patterns = [
        r'\bspecifically\b',
        r'\bexactly\b',
        r'\bmust\s+(?:be|have|include)',
        r'\brequired?\b',
        r'\d+\s*(?:characters?|words?|lines?|items?)',  # Numeric constraints
        r'\bformat\s*:',
        r'\boutput\s*:',
    ]

    structure_patterns = [
        r'^\s*\d+[\.\)]\s',  # Numbered lists
        r'<\w+>',  # XML tags
        r'\*\*\w+\*\*',  # Bold headers
        r'^#+\s',  # Markdown headers
        r'```',  # Code blocks
    ]

    context_patterns = [
        r'\bgiven\s+(?:that|the)',
        r'\bcontext\s*:',
        r'\bbackground\s*:',
        r'\bcurrently\b',
        r'\bexisting\b',
        r'\bpreviously\b',
    ]

    for msg in messages:
        msg_lower = msg.lower()

        for pattern in clarity_patterns:
            if re.search(pattern, msg_lower):
                clarity_signals += 1
                break

        for pattern in structure_patterns:
            if re.search(pattern, msg, re.MULTILINE):
                structure_signals += 1
                break

        for pattern in context_patterns:
            if re.search(pattern, msg_lower):
                context_signals += 1
                break

    n = len(messages) if messages else 1

    clarity_score = min(1.0, clarity_signals / n * 2)  # Scale to 0-1
    structure_score = min(1.0, structure_signals / n * 2)
    context_score = min(1.0, context_signals / n * 2)

    return clarity_score, structure_score, context_score


def generate_claude_md(dna: PromptDNA) -> str:
    """Generate a CLAUDE.md file based on detected patterns."""

    lines = [
        "# Claude Preferences",
        "",
        f"*Auto-generated from {dna.total_prompts_analyzed} prompts analyzed by Claude Wrapped*",
        "",
    ]

    # Communication style
    lines.extend([
        "## Communication Style",
        "",
    ])

    if dna.avg_prompt_length_words < 50:
        lines.append("- Keep responses concise and to the point")
    elif dna.avg_prompt_length_words > 150:
        lines.append("- Provide detailed, comprehensive responses")

    if dna.question_ratio > 0.5:
        lines.append("- Ask clarifying questions when requirements are ambiguous")

    if dna.directive_ratio > 0.5:
        lines.append("- Be direct and action-oriented")

    lines.append("")

    # House rules
    if dna.house_rules:
        lines.extend([
            "## Preferences",
            "",
            "*Based on your most common instructions:*",
            "",
        ])
        for item in dna.house_rules[:10]:
            # Handle both 2-tuple and 3-tuple formats
            rule = item[0] if isinstance(item, tuple) else item
            # Capitalize and clean up
            rule_clean = rule.strip()
            if rule_clean and not rule_clean[0].isupper():
                rule_clean = rule_clean[0].upper() + rule_clean[1:]
            lines.append(f"- {rule_clean}")
        lines.append("")

    # Tech stack
    if dna.tech_mentions:
        lines.extend([
            "## Tech Stack",
            "",
            "*Technologies you frequently work with:*",
            "",
        ])
        top_tech = sorted(dna.tech_mentions.items(), key=lambda x: -x[1])[:10]
        for tech, count in top_tech:
            lines.append(f"- {tech.title()}")
        lines.append("")

    # Output preferences
    if dna.output_formats:
        lines.extend([
            "## Output Preferences",
            "",
        ])
        for fmt, count in sorted(dna.output_formats.items(), key=lambda x: -x[1])[:5]:
            lines.append(f"- Prefer {fmt} format when appropriate")
        lines.append("")

    # Structure preferences
    structure_prefs = []
    if dna.uses_xml_tags > 5:
        structure_prefs.append("XML tags for structure")
    if dna.uses_numbered_lists > 10:
        structure_prefs.append("numbered lists for steps")
    if dna.uses_markdown > 10:
        structure_prefs.append("Markdown formatting")

    if structure_prefs:
        lines.extend([
            "## Formatting",
            "",
            f"- Use {', '.join(structure_prefs)}",
            "",
        ])

    lines.extend([
        "---",
        "*Generated by Claude Wrapped 2025*",
    ])

    return '\n'.join(lines)


def analyze_prompt_dna(claude_dir: Path) -> PromptDNA:
    """Main analysis function - extracts all prompt DNA metrics."""

    # Extract messages
    messages = extract_user_messages(claude_dir)

    if not messages:
        return PromptDNA()

    dna = PromptDNA()
    dna.total_prompts_analyzed = len(messages)
    dna.total_words = sum(len(m.split()) for m in messages)

    # Extract patterns
    dna.top_catchphrases = extract_catchphrases(messages)
    dna.house_rules = extract_house_rules(messages)
    dna.role_assignments = extract_role_assignments(messages)
    dna.output_formats = extract_output_formats(messages)
    dna.tech_mentions = extract_tech_mentions(messages)

    # Communication style analysis
    style = analyze_communication_style(messages)
    dna.avg_prompt_length_words = style.get('avg_prompt_length_words', 0)
    dna.avg_prompt_length_chars = style.get('avg_prompt_length_chars', 0)
    dna.question_ratio = style.get('question_ratio', 0)
    dna.directive_ratio = style.get('directive_ratio', 0)
    dna.uses_xml_tags = style.get('xml_tags', 0)
    dna.uses_numbered_lists = style.get('numbered_lists', 0)
    dna.uses_markdown = style.get('markdown', 0)
    dna.uses_json_requests = style.get('json_requests', 0)
    dna.uses_examples = style.get('examples', 0)
    dna.opening_patterns = style.get('opening_patterns', {})

    # Find top opening pattern
    if dna.opening_patterns:
        top_opening = max(dna.opening_patterns.items(), key=lambda x: x[1])
        dna.top_opening_phrase = top_opening[0]

    # Classify personality
    dna.prompt_personality, dna.prompt_personality_description, dna.prompt_personality_icon = \
        classify_prompt_personality(dna)

    # Calculate quality scores
    dna.clarity_score, dna.structure_score, dna.context_score = \
        calculate_quality_scores(messages, dna)

    # Classify overall style
    if dna.question_ratio > 0.5:
        dna.prompt_style = "exploratory"
    elif dna.directive_ratio > 0.6:
        dna.prompt_style = "directive"
    elif dna.uses_xml_tags > 5 or dna.uses_numbered_lists > 10:
        dna.prompt_style = "structured"
    else:
        dna.prompt_style = "balanced"

    return dna


def prompt_dna_to_dict(dna: PromptDNA) -> dict:
    """Convert PromptDNA to JSON-serializable dict."""
    # Convert house_rules and role_assignments to dicts with source_type
    house_rules_dicts = []
    for item in dna.house_rules:
        if len(item) == 3:
            rule, count, source_type = item
        else:
            rule, count = item
            source_type = 'freeform'
        house_rules_dicts.append({
            'text': rule,
            'count': count,
            'source': source_type
        })

    role_assignments_dicts = []
    for item in dna.role_assignments:
        if len(item) == 3:
            role, count, source_type = item
        else:
            role, count = item
            source_type = 'freeform'
        role_assignments_dicts.append({
            'text': role,
            'count': count,
            'source': source_type
        })

    return {
        'total_prompts_analyzed': dna.total_prompts_analyzed,
        'total_words': dna.total_words,
        'top_catchphrases': dna.top_catchphrases,
        'house_rules': house_rules_dicts,
        'role_assignments': role_assignments_dicts,
        'output_formats': dna.output_formats,
        'avg_prompt_length_words': round(dna.avg_prompt_length_words, 1),
        'avg_prompt_length_chars': round(dna.avg_prompt_length_chars, 1),
        'question_ratio': round(dna.question_ratio, 3),
        'directive_ratio': round(dna.directive_ratio, 3),
        'prompt_style': dna.prompt_style,
        'prompt_personality': dna.prompt_personality,
        'prompt_personality_description': dna.prompt_personality_description,
        'prompt_personality_icon': dna.prompt_personality_icon,
        'uses_xml_tags': dna.uses_xml_tags,
        'uses_numbered_lists': dna.uses_numbered_lists,
        'uses_markdown': dna.uses_markdown,
        'uses_json_requests': dna.uses_json_requests,
        'uses_examples': dna.uses_examples,
        'tech_mentions': dna.tech_mentions,
        'opening_patterns': dna.opening_patterns,
        'top_opening_phrase': dna.top_opening_phrase,
        'clarity_score': round(dna.clarity_score, 2),
        'structure_score': round(dna.structure_score, 2),
        'context_score': round(dna.context_score, 2),
        'generated_claude_md': generate_claude_md(dna),
    }


# CLI for testing
if __name__ == '__main__':
    import sys

    claude_dir = Path(os.path.expanduser('~/.claude'))
    if len(sys.argv) > 1:
        claude_dir = Path(sys.argv[1])

    print(f"Analyzing {claude_dir}...")
    dna = analyze_prompt_dna(claude_dir)

    print(f"\n=== Prompt DNA Analysis ===")
    print(f"Prompts analyzed: {dna.total_prompts_analyzed}")
    print(f"Total words: {dna.total_words}")
    print(f"\nPersonality: {dna.prompt_personality_icon} {dna.prompt_personality}")
    print(f"  {dna.prompt_personality_description}")
    print(f"\nStyle: {dna.prompt_style}")
    print(f"Avg prompt length: {dna.avg_prompt_length_words:.0f} words")
    print(f"Question ratio: {dna.question_ratio:.1%}")
    print(f"Directive ratio: {dna.directive_ratio:.1%}")

    print(f"\n=== Top Catchphrases ===")
    for phrase, count in dna.top_catchphrases[:5]:
        print(f"  \"{phrase}\" ({count}x)")

    print(f"\n=== House Rules ===")
    for item in dna.house_rules[:5]:
        rule, count, source = item[0], item[1], item[2] if len(item) > 2 else 'freeform'
        print(f"  {rule} ({count}x) [{source}]")

    print(f"\n=== Role Assignments ===")
    for item in dna.role_assignments[:5]:
        role, count, source = item[0], item[1], item[2] if len(item) > 2 else 'freeform'
        print(f"  You are a {role} ({count}x) [{source}]")

    print(f"\n=== Tech Stack ===")
    for tech, count in list(dna.tech_mentions.items())[:5]:
        print(f"  {tech}: {count}")

    print(f"\n=== Generated CLAUDE.md ===")
    print(generate_claude_md(dna))
