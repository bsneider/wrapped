#!/usr/bin/env python3
"""
Proficiency Analyzer - Research-backed assessment of prompting ability.

Based on 25+ academic papers and industry research, this module assesses
user prompting proficiency across four dimensions:

1. Prompt Engineering - Clarity, specificity, technique usage
2. Context Engineering - Efficiency, positioning, compression
3. Memory Engineering - Cross-session continuity, redundancy avoidance
4. Tool Use Proficiency - Discovery, composition, parallelism

References:
- arXiv:2402.07927 - Systematic Survey of Prompt Engineering
- arXiv:2501.11709 - Knowledge Gaps in Developer Prompts
- arXiv:2503.00681 - From Prompting to Partnering
- Anthropic Research - XML formatting yields 15-20% improvement
- Industry: Numbered steps lead to 87% better compliance
"""

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ProficiencyAssessment:
    """Complete proficiency assessment results."""

    # Dimension scores (0-100)
    prompt_engineering_score: int = 0
    context_engineering_score: int = 0
    memory_engineering_score: int = 0
    tool_use_score: int = 0

    # Overall
    overall_proficiency: int = 0
    proficiency_level: str = ""  # "novice", "intermediate", "advanced", "expert"

    # Prompt Engineering breakdown
    prompt_clarity_score: int = 0
    prompt_specificity_score: int = 0
    prompt_technique_score: int = 0
    prompt_iteration_efficiency: int = 0
    prompt_gap_rate: float = 0.0  # Lower is better

    # Context Engineering breakdown
    context_efficiency_score: int = 0
    context_position_awareness: int = 0
    context_compression_skill: int = 0

    # Memory Engineering breakdown
    memory_continuity_score: int = 0
    memory_isolation_score: int = 0
    memory_redundancy_score: int = 0  # Lower redundancy = higher score

    # Tool Use breakdown
    tool_discovery_score: int = 0
    tool_composition_score: int = 0
    tool_parallelism_score: int = 0
    tool_recovery_score: int = 0

    # Insights
    top_strength: str = ""
    top_strength_description: str = ""
    primary_weakness: str = ""
    primary_weakness_description: str = ""
    recommendations: list = field(default_factory=list)

    # Trends (if historical data available)
    skills_improved: list = field(default_factory=list)
    skills_declined: list = field(default_factory=list)


# ============================================================================
# PROMPT ENGINEERING ANALYSIS
# ============================================================================

# Clarity signals based on research
CLARITY_POSITIVE_PATTERNS = [
    (r'\d+[\.\)]\s', 'numbered_steps'),       # Numbered steps (87% better compliance)
    (r'specifically\b', 'specificity'),
    (r'exactly\b', 'precision'),
    (r'must\s+(?:be|have|include)', 'requirements'),
    (r'format\s*:', 'format_spec'),
    (r'output\s*:', 'output_spec'),
    (r'<\w+>', 'xml_tags'),                    # XML tags (15-20% improvement with Claude)
    (r'step\s+\d+', 'explicit_steps'),
    (r'first,?\s|then,?\s|finally,?\s', 'sequence'),
    (r'ensure\s+that', 'constraints'),
    (r'return\s+only', 'output_constraint'),
    (r'do\s+not\s+include', 'exclusion'),
    (r'example:', 'example_provided'),
    (r'```', 'code_blocks'),
]

CLARITY_NEGATIVE_PATTERNS = [
    (r'\bmaybe\b', 'uncertainty'),
    (r'\bkind\s+of\b', 'vagueness'),
    (r'\bsomething\s+like\b', 'ambiguity'),
    (r'\betc\.?\b', 'incomplete_list'),
    (r'\bwhatever\b', 'low_effort'),
    (r'\bidk\b', 'uncertainty'),
    (r'\bi\s+guess\b', 'uncertainty'),
    (r'\bstuff\b', 'vagueness'),
    (r'\bthings\b(?!\s+(?:like|such))', 'vagueness'),
]

# Technique patterns (advanced prompting)
TECHNIQUE_PATTERNS = {
    'chain_of_thought': [
        r'let\'?s?\s+think\s+(?:about\s+this\s+)?step\s+by\s+step',
        r'think\s+through\s+this',
        r'reason\s+(?:through|about)',
        r'walk\s+(?:me\s+)?through',
    ],
    'few_shot': [
        r'(?:here\'?s?\s+)?(?:an?\s+)?example:',
        r'for\s+example:',
        r'like\s+this:',
        r'input:.*output:',
    ],
    'role_prompting': [
        r'(?:you\s+are|act\s+as|pretend\s+(?:to\s+be|you\'?re))\s+(?:a|an)',
        r'as\s+(?:a|an)\s+\w+\s+expert',
    ],
    'structured_output': [
        r'respond\s+(?:in|with|using)\s+(?:json|yaml|xml)',
        r'format\s+(?:as|your\s+response\s+as)',
        r'use\s+(?:the\s+following\s+)?(?:format|structure)',
    ],
    'self_reflection': [
        r'verify\s+your\s+(?:answer|response|work)',
        r'double[\s-]check',
        r'are\s+you\s+sure',
        r'review\s+(?:your|the)\s+(?:answer|response)',
    ],
}

# Knowledge gap indicators (research: 54.7% gap rate = poor, 13.2% = excellent)
GAP_PATTERNS = {
    'missing_context': [
        r'^(?:fix|update|change|modify)\s+(?:it|this|that)\b',  # No specific target
        r'^(?:make|do)\s+it\s+(?:work|better)\b',
        r'the\s+(?:error|bug|issue|problem)\b(?!\s+(?:is|in|at|with|:))',
    ],
    'missing_specs': [
        r'\bimprove\b(?!\s+(?:by|the|performance|speed))',
        r'\boptimize\b(?!\s+(?:for|the))',
        r'\bbetter\b(?!\s+(?:than|at|for|way))',
        r'^make\s+(?:it|this)\s+\w+$',  # Very short, vague
    ],
    'unclear_instructions': [
        r'\bsomehow\b',
        r'\bsomething\s+(?:wrong|broken|weird)',
        r'not\s+(?:working|right)\b(?!\s+(?:because|when|if))',
    ],
}


def analyze_prompt_engineering(messages: list[dict], sessions: list[dict]) -> dict:
    """
    Analyze prompt engineering proficiency.

    Returns component scores and overall prompt engineering score.
    """
    if not messages:
        return {
            'score': 0,
            'clarity': 0,
            'specificity': 0,
            'technique': 0,
            'iteration': 0,
            'gap_rate': 1.0,
        }

    user_messages = [m for m in messages if m.get('role') == 'user']
    if not user_messages:
        return {'score': 0, 'clarity': 0, 'specificity': 0, 'technique': 0, 'iteration': 0, 'gap_rate': 1.0}

    # Calculate component scores
    clarity = calculate_clarity_score(user_messages)
    specificity = calculate_specificity_score(user_messages)
    technique = calculate_technique_score(user_messages)
    iteration = calculate_iteration_efficiency(sessions)
    gap_rate = calculate_gap_rate(user_messages)

    # Weighted combination (based on research importance)
    score = int(
        0.25 * clarity +
        0.25 * specificity +
        0.20 * technique +
        0.20 * iteration +
        0.10 * (100 - gap_rate * 100)  # Lower gap rate = higher contribution
    )

    return {
        'score': min(100, max(0, score)),
        'clarity': clarity,
        'specificity': specificity,
        'technique': technique,
        'iteration': iteration,
        'gap_rate': gap_rate,
    }


def calculate_clarity_score(messages: list[dict]) -> int:
    """Calculate clarity score based on positive/negative signals."""
    if not messages:
        return 0

    positive_count = 0
    negative_count = 0

    for msg in messages:
        content = msg.get('content', '')
        if not isinstance(content, str):
            continue

        content_lower = content.lower()

        # Count positive signals
        for pattern, _ in CLARITY_POSITIVE_PATTERNS:
            if re.search(pattern, content_lower):
                positive_count += 1

        # Count negative signals
        for pattern, _ in CLARITY_NEGATIVE_PATTERNS:
            if re.search(pattern, content_lower):
                negative_count += 1

    n = len(messages)
    positive_ratio = positive_count / (n * 3) if n else 0  # Normalize (expect ~3 signals per good prompt)
    negative_ratio = negative_count / n if n else 0

    # Score: high positive, low negative = good
    score = (positive_ratio * 70) + (30 * (1 - min(1, negative_ratio)))
    return min(100, max(0, int(score)))


def calculate_specificity_score(messages: list[dict]) -> int:
    """Calculate specificity based on constraints, formats, examples."""
    if not messages:
        return 0

    specificity_signals = 0

    specificity_patterns = [
        r'\d+\s*(?:chars?|characters?|words?|lines?|items?|elements?)',  # Numeric constraints
        r'(?:max|min|at\s+(?:least|most))\s+\d+',
        r'between\s+\d+\s+and\s+\d+',
        r'no\s+more\s+than',
        r'at\s+least\s+\d+',
        r'exactly\s+\d+',
        r'format:',
        r'output:',
        r'schema:',
        r'type:',
        r'return\s+type',
        r'interface\s*\{',
        r'```\w+',  # Code blocks with language
        r'example:',
        r'e\.g\.',
        r'such\s+as:',
        r'including:',
    ]

    for msg in messages:
        content = msg.get('content', '')
        if not isinstance(content, str):
            continue

        content_lower = content.lower()
        for pattern in specificity_patterns:
            if re.search(pattern, content_lower):
                specificity_signals += 1

    n = len(messages)
    ratio = specificity_signals / (n * 2) if n else 0  # Expect ~2 signals per specific prompt
    return min(100, max(0, int(ratio * 100)))


def calculate_technique_score(messages: list[dict]) -> int:
    """Detect usage of advanced prompting techniques."""
    if not messages:
        return 0

    technique_usage = defaultdict(int)

    for msg in messages:
        content = msg.get('content', '')
        if not isinstance(content, str):
            continue

        content_lower = content.lower()

        for technique, patterns in TECHNIQUE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    technique_usage[technique] += 1
                    break  # Count technique once per message

    # Score based on technique diversity and frequency
    techniques_used = len(technique_usage)
    total_uses = sum(technique_usage.values())
    n = len(messages)

    # Diversity bonus (using multiple techniques is good)
    diversity_score = min(100, techniques_used * 25)  # Up to 4 techniques = 100

    # Frequency score (using techniques consistently)
    frequency_score = min(100, (total_uses / n * 100) if n else 0)

    return int(0.6 * diversity_score + 0.4 * frequency_score)


def calculate_iteration_efficiency(sessions: list[dict]) -> int:
    """
    Calculate iteration efficiency - fewer turns to complete tasks is better.

    Research: Expert prompters complete tasks in 2-3 turns, novices take 6+
    """
    if not sessions:
        return 50  # Default to middle

    turn_counts = []
    for session in sessions:
        messages = session.get('messages', [])
        user_turns = sum(1 for m in messages if m.get('role') == 'user')
        if user_turns > 0:
            turn_counts.append(user_turns)

    if not turn_counts:
        return 50

    avg_turns = sum(turn_counts) / len(turn_counts)

    # Scoring: 1-3 turns = excellent, 4-6 = good, 7-10 = average, 10+ = poor
    if avg_turns <= 3:
        return 100
    elif avg_turns <= 5:
        return 85
    elif avg_turns <= 7:
        return 70
    elif avg_turns <= 10:
        return 50
    elif avg_turns <= 15:
        return 30
    else:
        return 15


def calculate_gap_rate(messages: list[dict]) -> float:
    """
    Calculate knowledge gap rate in prompts.

    Research finding: 54.7% gap rate = ineffective, 13.2% = effective
    """
    if not messages:
        return 0.5

    gaps_found = 0

    for msg in messages:
        content = msg.get('content', '')
        if not isinstance(content, str):
            continue

        content_lower = content.lower()
        has_gap = False

        for gap_type, patterns in GAP_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    has_gap = True
                    break
            if has_gap:
                break

        if has_gap:
            gaps_found += 1

    return gaps_found / len(messages) if messages else 0.5


# ============================================================================
# CONTEXT ENGINEERING ANALYSIS
# ============================================================================

def analyze_context_engineering(sessions: list[dict], messages: list[dict]) -> dict:
    """
    Analyze context engineering proficiency.

    Key insights from research:
    - Instructions at END perform 36% better (Anthropic)
    - At 32k tokens, most models drop below 50% performance
    - Context efficiency matters more than quantity
    """
    if not sessions:
        return {'score': 0, 'efficiency': 0, 'position': 0, 'compression': 0}

    efficiency = calculate_context_efficiency(messages)
    position = calculate_position_awareness(messages)
    compression = calculate_compression_skill(sessions)

    score = int(
        0.35 * efficiency +
        0.35 * position +
        0.30 * compression
    )

    return {
        'score': min(100, max(0, score)),
        'efficiency': efficiency,
        'position': position,
        'compression': compression,
    }


def calculate_context_efficiency(messages: list[dict]) -> int:
    """
    Measure context efficiency - relevant content vs noise.
    """
    if not messages:
        return 50

    user_messages = [m for m in messages if m.get('role') == 'user']
    if not user_messages:
        return 50

    efficiency_signals = 0
    inefficiency_signals = 0

    # Efficiency signals
    efficiency_patterns = [
        r'relevant\s+(?:code|context|info)',
        r'here\'?s?\s+the\s+(?:relevant|specific|key)',
        r'focus\s+on',
        r'the\s+(?:key|main|important)\s+(?:part|section|code)',
        r'excerpt',
        r'snippet',
    ]

    # Inefficiency signals
    inefficiency_patterns = [
        r'here\'?s?\s+(?:the\s+)?(?:entire|whole|full|complete)\s+(?:file|code|content)',
        r'i\'?ll?\s+paste\s+everything',
        r'all\s+(?:\d+|the)\s+(?:files?|code)',
        r'dump(?:ing)?\s+(?:the|all)',
    ]

    for msg in user_messages:
        content = msg.get('content', '')
        if not isinstance(content, str):
            continue

        content_lower = content.lower()

        for pattern in efficiency_patterns:
            if re.search(pattern, content_lower):
                efficiency_signals += 1

        for pattern in inefficiency_patterns:
            if re.search(pattern, content_lower):
                inefficiency_signals += 1

    n = len(user_messages)
    if n == 0:
        return 50

    # Also check message lengths - very long messages might indicate dumping
    avg_length = sum(len(m.get('content', '')) for m in user_messages) / n
    length_penalty = max(0, (avg_length - 2000) / 5000)  # Penalty for very long messages

    base_score = 50 + (efficiency_signals * 10) - (inefficiency_signals * 15)
    score = base_score - (length_penalty * 30)

    return min(100, max(0, int(score)))


def calculate_position_awareness(messages: list[dict]) -> int:
    """
    Check if user places critical instructions at optimal positions.

    Research: Instructions at END of prompts improve performance 36%
    """
    if not messages:
        return 50

    user_messages = [m for m in messages if m.get('role') == 'user']
    if not user_messages:
        return 50

    position_aware_count = 0

    instruction_starters = [
        r'^(?:important|note|remember|make\s+sure|ensure|don\'t\s+forget)',
        r'^(?:please|now|finally)',
        r'^(?:output|format|return)',
    ]

    for msg in user_messages:
        content = msg.get('content', '')
        if not isinstance(content, str) or len(content) < 100:
            continue

        # Check if instructions are at the end (last 20% of message)
        lines = content.strip().split('\n')
        if len(lines) < 5:
            continue

        last_portion = '\n'.join(lines[-max(2, len(lines)//5):]).lower()

        for pattern in instruction_starters:
            if re.search(pattern, last_portion, re.MULTILINE):
                position_aware_count += 1
                break

    # Also check for explicit "finally" or "lastly" markers
    for msg in user_messages:
        content = msg.get('content', '').lower()
        if re.search(r'(?:finally|lastly|in\s+conclusion|to\s+summarize).*(?:make\s+sure|ensure|output|return)', content):
            position_aware_count += 1

    n = len([m for m in user_messages if len(m.get('content', '')) > 100])
    if n == 0:
        return 50

    ratio = position_aware_count / n
    return min(100, max(0, int(50 + ratio * 100)))


def calculate_compression_skill(sessions: list[dict]) -> int:
    """
    Assess ability to compress/summarize context when needed.
    """
    if not sessions:
        return 50

    compression_signals = 0

    compression_patterns = [
        r'summar(?:y|ize|izing)',
        r'in\s+(?:short|brief)',
        r'the\s+(?:key|main|essential)\s+points?',
        r'tl;?dr',
        r'condensed?',
        r'abbreviated?',
        r'(?:just|only)\s+the\s+(?:relevant|important)',
    ]

    for session in sessions:
        for msg in session.get('messages', []):
            if msg.get('role') != 'user':
                continue

            content = msg.get('content', '')
            if not isinstance(content, str):
                continue

            content_lower = content.lower()
            for pattern in compression_patterns:
                if re.search(pattern, content_lower):
                    compression_signals += 1
                    break

    total_sessions = len(sessions)
    if total_sessions == 0:
        return 50

    ratio = compression_signals / total_sessions
    return min(100, max(0, int(50 + ratio * 100)))


# ============================================================================
# MEMORY ENGINEERING ANALYSIS
# ============================================================================

def analyze_memory_engineering(sessions: list[dict], messages: list[dict]) -> dict:
    """
    Analyze memory engineering proficiency.

    Key metrics:
    - Cross-session continuity: Referencing prior context
    - Project isolation: Proper separation of contexts
    - Redundancy avoidance: Not re-explaining known info
    """
    if not sessions:
        return {'score': 0, 'continuity': 0, 'isolation': 0, 'redundancy': 0}

    continuity = calculate_continuity_score(sessions)
    isolation = calculate_isolation_score(sessions)
    redundancy = calculate_redundancy_score(messages)

    score = int(
        0.35 * continuity +
        0.30 * isolation +
        0.35 * redundancy
    )

    return {
        'score': min(100, max(0, score)),
        'continuity': continuity,
        'isolation': isolation,
        'redundancy': redundancy,
    }


def calculate_continuity_score(sessions: list[dict]) -> int:
    """
    Measure cross-session continuity - references to prior context.
    """
    if not sessions:
        return 50

    continuity_signals = 0

    continuity_patterns = [
        r'as\s+(?:we|i)\s+(?:discussed|mentioned|talked\s+about)',
        r'continuing\s+(?:from|with|our)',
        r'(?:based|building)\s+on\s+(?:our\s+)?(?:previous|earlier|last)',
        r'(?:you|we)\s+(?:mentioned|said|discussed)\s+(?:earlier|before|previously)',
        r'(?:referring|going\s+back)\s+to',
        r'(?:as|like)\s+(?:before|last\s+time)',
        r'remember\s+(?:when|how|that)',
        r'the\s+(?:project|code|feature)\s+(?:we|I)\s+(?:worked\s+on|started)',
    ]

    for session in sessions:
        for msg in session.get('messages', []):
            if msg.get('role') != 'user':
                continue

            content = msg.get('content', '')
            if not isinstance(content, str):
                continue

            content_lower = content.lower()
            for pattern in continuity_patterns:
                if re.search(pattern, content_lower):
                    continuity_signals += 1
                    break

    total_sessions = len(sessions)
    ratio = continuity_signals / total_sessions if total_sessions else 0

    # Good users reference prior context in ~30%+ of sessions
    return min(100, max(0, int(ratio * 200)))  # 50% ratio = 100 score


def calculate_isolation_score(sessions: list[dict]) -> int:
    """
    Measure project isolation awareness.
    """
    if not sessions:
        return 50

    # Look for explicit project/context switching signals
    isolation_signals = 0

    isolation_patterns = [
        r'(?:new|different|separate)\s+(?:project|context|task)',
        r'(?:switching|moving)\s+to',
        r'(?:forget|ignore)\s+(?:the\s+)?(?:previous|earlier|last)',
        r'(?:start|begin)(?:ning)?\s+(?:fresh|new|clean)',
        r'unrelated\s+to',
        r'(?:this|new)\s+(?:project|codebase|repo)',
    ]

    for session in sessions:
        for msg in session.get('messages', []):
            if msg.get('role') != 'user':
                continue

            content = msg.get('content', '')
            if not isinstance(content, str):
                continue

            content_lower = content.lower()
            for pattern in isolation_patterns:
                if re.search(pattern, content_lower):
                    isolation_signals += 1
                    break

    # This is harder to measure without multiple projects
    # Give benefit of doubt for fewer signals
    total_sessions = len(sessions)
    if total_sessions < 10:
        return 60  # Not enough data

    ratio = isolation_signals / total_sessions
    return min(100, max(0, int(50 + ratio * 200)))


def calculate_redundancy_score(messages: list[dict]) -> int:
    """
    Measure redundancy avoidance - higher score = less redundancy.

    Research: 40% fewer re-explanations = high memory skill
    """
    if not messages:
        return 50

    user_messages = [m for m in messages if m.get('role') == 'user']
    if not user_messages:
        return 50

    redundancy_signals = 0

    redundancy_patterns = [
        r'(?:let\s+me|i\'?ll?)\s+(?:re-?explain|explain\s+again)',
        r'(?:to|let\s+me)\s+remind\s+you',
        r'as\s+i\s+(?:said|mentioned)\s+(?:before|earlier|already)',
        r'(?:again|once\s+more),?\s+(?:the|this|my)',
        r'you\s+(?:probably|might)\s+(?:not\s+)?remember',
        r'in\s+case\s+you\s+(?:forgot|don\'t\s+remember)',
        r'i\'?(?:ll|m\s+going\s+to)\s+repeat',
    ]

    for msg in user_messages:
        content = msg.get('content', '')
        if not isinstance(content, str):
            continue

        content_lower = content.lower()
        for pattern in redundancy_patterns:
            if re.search(pattern, content_lower):
                redundancy_signals += 1
                break

    n = len(user_messages)
    redundancy_rate = redundancy_signals / n if n else 0

    # Lower redundancy = higher score
    # 0% redundancy = 100, 30%+ = poor
    return min(100, max(0, int(100 - redundancy_rate * 300)))


# ============================================================================
# TOOL USE PROFICIENCY ANALYSIS
# ============================================================================

def analyze_tool_use(sessions: list[dict], tool_data: dict) -> dict:
    """
    Analyze tool use proficiency.

    Metrics:
    - Discovery: Appropriate tool requests
    - Composition: Multi-tool workflows
    - Parallelism: Independent operations parallelized
    - Recovery: Graceful error handling
    """
    if not sessions and not tool_data:
        return {'score': 0, 'discovery': 0, 'composition': 0, 'parallelism': 0, 'recovery': 0}

    discovery = calculate_tool_discovery(sessions, tool_data)
    composition = calculate_tool_composition(sessions, tool_data)
    parallelism = calculate_tool_parallelism(sessions)
    recovery = calculate_error_recovery(sessions)

    score = int(
        0.25 * discovery +
        0.30 * composition +
        0.25 * parallelism +
        0.20 * recovery
    )

    return {
        'score': min(100, max(0, score)),
        'discovery': discovery,
        'composition': composition,
        'parallelism': parallelism,
        'recovery': recovery,
    }


def calculate_tool_discovery(sessions: list[dict], tool_data: dict) -> int:
    """
    Measure appropriate tool discovery/requests.
    """
    if not tool_data:
        return 50

    # Check tool diversity
    tool_counts = tool_data.get('tool_frequency', {})
    tools_used = len([t for t, c in tool_counts.items() if c > 0])
    total_uses = sum(tool_counts.values())

    # Good discovery = using multiple tools appropriately
    if tools_used == 0:
        return 30

    # Diversity score (using 5+ tools well = good)
    diversity = min(100, tools_used * 15)

    # Volume score (using tools frequently = engagement)
    volume = min(100, total_uses / 10) if total_uses else 0

    return int(0.6 * diversity + 0.4 * volume)


def calculate_tool_composition(sessions: list[dict], tool_data: dict) -> int:
    """
    Measure multi-tool workflow composition.
    """
    if not tool_data:
        return 50

    tool_counts = tool_data.get('tool_frequency', {})

    # Check for common composition patterns
    # Read -> Edit is good
    # Grep -> Read -> Edit is better
    # Task delegation shows advanced usage

    read_count = tool_counts.get('Read', 0)
    edit_count = tool_counts.get('Edit', 0)
    grep_count = tool_counts.get('Grep', 0)
    glob_count = tool_counts.get('Glob', 0)
    bash_count = tool_counts.get('Bash', 0)
    task_count = tool_counts.get('Task', 0)

    # Composition indicators
    composition_score = 0

    # Read-then-Edit pattern (good)
    if read_count > 0 and edit_count > 0:
        ratio = min(edit_count, read_count) / max(edit_count, read_count)
        composition_score += ratio * 30

    # Search-then-Read pattern (good)
    if (grep_count > 0 or glob_count > 0) and read_count > 0:
        composition_score += 25

    # Task delegation (advanced)
    if task_count > 0:
        composition_score += min(30, task_count * 10)

    # Bash + other tools (integration)
    if bash_count > 0 and (read_count > 0 or edit_count > 0):
        composition_score += 15

    return min(100, max(0, int(composition_score)))


def calculate_tool_parallelism(sessions: list[dict]) -> int:
    """
    Measure parallel execution awareness.

    Users who request parallel operations when beneficial show advanced understanding.
    """
    if not sessions:
        return 50

    parallel_signals = 0

    parallel_patterns = [
        r'(?:in\s+)?parallel',
        r'(?:at\s+the\s+)?same\s+time',
        r'simultaneously',
        r'(?:all|both)\s+(?:at\s+once|together)',
        r'concurrently',
        r'while\s+(?:also|you\'?re)',
    ]

    for session in sessions:
        for msg in session.get('messages', []):
            if msg.get('role') != 'user':
                continue

            content = msg.get('content', '')
            if not isinstance(content, str):
                continue

            content_lower = content.lower()
            for pattern in parallel_patterns:
                if re.search(pattern, content_lower):
                    parallel_signals += 1
                    break

    total_sessions = len(sessions)
    ratio = parallel_signals / total_sessions if total_sessions else 0

    # Even 10% parallel awareness is good for most users
    return min(100, max(0, int(50 + ratio * 300)))


def calculate_error_recovery(sessions: list[dict]) -> int:
    """
    Measure graceful error recovery patterns.
    """
    if not sessions:
        return 50

    recovery_signals = 0
    error_mentions = 0

    recovery_patterns = [
        r'(?:let\'?s?\s+)?try\s+(?:a\s+)?(?:different|another|alternative)',
        r'(?:instead|alternatively)',
        r'(?:fall\s*back|revert)\s+to',
        r'if\s+(?:that|this)\s+(?:doesn\'?t\s+work|fails)',
        r'(?:as\s+a\s+)?(?:backup|fallback)',
        r'(?:handle|catch)\s+(?:the\s+)?(?:error|exception)',
    ]

    error_patterns = [
        r'\berror\b',
        r'\bfail(?:ed|ure|s)?\b',
        r'\bbroken\b',
        r'\bcrash(?:ed|es)?\b',
        r'\bbug\b',
    ]

    for session in sessions:
        for msg in session.get('messages', []):
            if msg.get('role') != 'user':
                continue

            content = msg.get('content', '')
            if not isinstance(content, str):
                continue

            content_lower = content.lower()

            for pattern in error_patterns:
                if re.search(pattern, content_lower):
                    error_mentions += 1
                    break

            for pattern in recovery_patterns:
                if re.search(pattern, content_lower):
                    recovery_signals += 1
                    break

    if error_mentions == 0:
        return 70  # No errors = decent baseline

    recovery_rate = recovery_signals / error_mentions if error_mentions else 0
    return min(100, max(0, int(50 + recovery_rate * 100)))


# ============================================================================
# RECOMMENDATIONS ENGINE
# ============================================================================

def generate_recommendations(assessment: ProficiencyAssessment) -> list[str]:
    """Generate actionable recommendations based on assessment."""
    recommendations = []

    # Prompt Engineering recommendations
    if assessment.prompt_clarity_score < 60:
        recommendations.append(
            "Use numbered steps in your prompts - research shows 87% better compliance"
        )

    if assessment.prompt_specificity_score < 60:
        recommendations.append(
            "Add specific constraints (word count, format) to your requests"
        )

    if assessment.prompt_technique_score < 50:
        recommendations.append(
            "Try 'Let's think step by step' for complex problems (Chain-of-Thought)"
        )

    if assessment.prompt_gap_rate > 0.3:
        recommendations.append(
            f"Your prompts have a {assessment.prompt_gap_rate*100:.0f}% knowledge gap rate - "
            "aim for under 20% by providing more context"
        )

    # Context Engineering recommendations
    if assessment.context_position_awareness < 60:
        recommendations.append(
            "Place critical instructions at the END of long prompts - "
            "research shows 36% improvement with Claude"
        )

    if assessment.context_efficiency_score < 50:
        recommendations.append(
            "Include only relevant context - avoid pasting entire files when snippets suffice"
        )

    # Memory Engineering recommendations
    if assessment.memory_redundancy_score < 60:
        recommendations.append(
            "Reference prior context instead of re-explaining: "
            "'As we discussed...' saves tokens and improves coherence"
        )

    if assessment.memory_continuity_score < 50:
        recommendations.append(
            "Leverage cross-session memory by referencing previous work"
        )

    # Tool Use recommendations
    if assessment.tool_composition_score < 50:
        recommendations.append(
            "Chain tools together: Search -> Read -> Edit is more efficient than separate requests"
        )

    if assessment.tool_parallelism_score < 50:
        recommendations.append(
            "Request parallel operations when tasks are independent to save time"
        )

    # XML formatting (Claude-specific)
    if assessment.prompt_engineering_score < 70:
        recommendations.append(
            "Try XML tags in prompts (<context>, <instructions>) - "
            "Claude is specifically trained for 15-20% better performance with XML"
        )

    return recommendations[:5]  # Top 5 recommendations


def identify_strengths_weaknesses(assessment: ProficiencyAssessment) -> tuple[str, str, str, str]:
    """Identify top strength and primary weakness."""

    dimensions = {
        'Prompt Engineering': assessment.prompt_engineering_score,
        'Context Engineering': assessment.context_engineering_score,
        'Memory Engineering': assessment.memory_engineering_score,
        'Tool Use': assessment.tool_use_score,
    }

    strength_descriptions = {
        'Prompt Engineering': "Your prompts are clear, specific, and use advanced techniques effectively",
        'Context Engineering': "You manage context efficiently, placing information strategically",
        'Memory Engineering': "You leverage cross-session continuity and avoid redundant explanations",
        'Tool Use': "You compose tools effectively and parallelize operations when beneficial",
    }

    weakness_descriptions = {
        'Prompt Engineering': "Focus on clarity, specificity, and advanced techniques like CoT",
        'Context Engineering': "Work on context efficiency and strategic information placement",
        'Memory Engineering': "Reduce redundancy and leverage cross-session references",
        'Tool Use': "Try chaining tools together and requesting parallel operations",
    }

    sorted_dims = sorted(dimensions.items(), key=lambda x: x[1], reverse=True)

    strength = sorted_dims[0][0]
    weakness = sorted_dims[-1][0]

    return (
        strength,
        strength_descriptions[strength],
        weakness,
        weakness_descriptions[weakness]
    )


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def extract_sessions_and_messages(claude_dir: Path) -> tuple[list[dict], list[dict]]:
    """Extract sessions and messages from Claude directory."""
    sessions = []
    all_messages = []

    projects_dir = claude_dir / 'projects'
    if not projects_dir.exists():
        return sessions, all_messages

    for jsonl_file in projects_dir.glob('**/*.jsonl'):
        session_messages = []
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        msg = json.loads(line)

                        # Extract user messages
                        if msg.get('type') == 'user':
                            content = msg.get('message', {})
                            if isinstance(content, dict):
                                text = content.get('content', '')
                            else:
                                text = str(content)

                            if text and len(text) > 5:
                                message_data = {
                                    'role': 'user',
                                    'content': text,
                                }
                                session_messages.append(message_data)
                                all_messages.append(message_data)

                        # Extract assistant messages for context
                        elif msg.get('type') == 'assistant':
                            content = msg.get('message', {})
                            if isinstance(content, dict):
                                text = content.get('content', '')
                            else:
                                text = str(content) if content else ''

                            if text:
                                message_data = {
                                    'role': 'assistant',
                                    'content': text[:500],  # Truncate for efficiency
                                }
                                session_messages.append(message_data)

                    except json.JSONDecodeError:
                        continue

            if session_messages:
                sessions.append({
                    'file': str(jsonl_file),
                    'messages': session_messages,
                })

        except (IOError, OSError):
            continue

    return sessions, all_messages


def analyze_proficiency(claude_dir: Path, tool_data: dict = None) -> ProficiencyAssessment:
    """
    Main entry point - analyze prompting proficiency across all dimensions.

    Args:
        claude_dir: Path to ~/.claude directory
        tool_data: Optional dict with tool_frequency data

    Returns:
        ProficiencyAssessment with all scores and recommendations
    """
    assessment = ProficiencyAssessment()

    # Extract data
    sessions, messages = extract_sessions_and_messages(claude_dir)

    if not sessions and not messages:
        return assessment

    # Analyze each dimension
    prompt_results = analyze_prompt_engineering(messages, sessions)
    assessment.prompt_engineering_score = prompt_results['score']
    assessment.prompt_clarity_score = prompt_results['clarity']
    assessment.prompt_specificity_score = prompt_results['specificity']
    assessment.prompt_technique_score = prompt_results['technique']
    assessment.prompt_iteration_efficiency = prompt_results['iteration']
    assessment.prompt_gap_rate = prompt_results['gap_rate']

    context_results = analyze_context_engineering(sessions, messages)
    assessment.context_engineering_score = context_results['score']
    assessment.context_efficiency_score = context_results['efficiency']
    assessment.context_position_awareness = context_results['position']
    assessment.context_compression_skill = context_results['compression']

    memory_results = analyze_memory_engineering(sessions, messages)
    assessment.memory_engineering_score = memory_results['score']
    assessment.memory_continuity_score = memory_results['continuity']
    assessment.memory_isolation_score = memory_results['isolation']
    assessment.memory_redundancy_score = memory_results['redundancy']

    tool_results = analyze_tool_use(sessions, tool_data or {})
    assessment.tool_use_score = tool_results['score']
    assessment.tool_discovery_score = tool_results['discovery']
    assessment.tool_composition_score = tool_results['composition']
    assessment.tool_parallelism_score = tool_results['parallelism']
    assessment.tool_recovery_score = tool_results['recovery']

    # Calculate overall score (weighted average)
    assessment.overall_proficiency = int(
        0.30 * assessment.prompt_engineering_score +
        0.25 * assessment.context_engineering_score +
        0.20 * assessment.memory_engineering_score +
        0.25 * assessment.tool_use_score
    )

    # Determine proficiency level
    if assessment.overall_proficiency >= 80:
        assessment.proficiency_level = "expert"
    elif assessment.overall_proficiency >= 65:
        assessment.proficiency_level = "advanced"
    elif assessment.overall_proficiency >= 45:
        assessment.proficiency_level = "intermediate"
    else:
        assessment.proficiency_level = "novice"

    # Generate insights
    (
        assessment.top_strength,
        assessment.top_strength_description,
        assessment.primary_weakness,
        assessment.primary_weakness_description
    ) = identify_strengths_weaknesses(assessment)

    assessment.recommendations = generate_recommendations(assessment)

    return assessment


def proficiency_to_dict(assessment: ProficiencyAssessment) -> dict:
    """Convert assessment to JSON-serializable dict."""
    return {
        # Overall
        'overall_proficiency': assessment.overall_proficiency,
        'proficiency_level': assessment.proficiency_level,

        # Dimension scores
        'prompt_engineering_score': assessment.prompt_engineering_score,
        'context_engineering_score': assessment.context_engineering_score,
        'memory_engineering_score': assessment.memory_engineering_score,
        'tool_use_score': assessment.tool_use_score,

        # Prompt Engineering breakdown
        'prompt_clarity_score': assessment.prompt_clarity_score,
        'prompt_specificity_score': assessment.prompt_specificity_score,
        'prompt_technique_score': assessment.prompt_technique_score,
        'prompt_iteration_efficiency': assessment.prompt_iteration_efficiency,
        'prompt_gap_rate': round(assessment.prompt_gap_rate, 3),

        # Context Engineering breakdown
        'context_efficiency_score': assessment.context_efficiency_score,
        'context_position_awareness': assessment.context_position_awareness,
        'context_compression_skill': assessment.context_compression_skill,

        # Memory Engineering breakdown
        'memory_continuity_score': assessment.memory_continuity_score,
        'memory_isolation_score': assessment.memory_isolation_score,
        'memory_redundancy_score': assessment.memory_redundancy_score,

        # Tool Use breakdown
        'tool_discovery_score': assessment.tool_discovery_score,
        'tool_composition_score': assessment.tool_composition_score,
        'tool_parallelism_score': assessment.tool_parallelism_score,
        'tool_recovery_score': assessment.tool_recovery_score,

        # Insights
        'top_strength': assessment.top_strength,
        'top_strength_description': assessment.top_strength_description,
        'primary_weakness': assessment.primary_weakness,
        'primary_weakness_description': assessment.primary_weakness_description,
        'recommendations': assessment.recommendations,
    }


# CLI for testing
if __name__ == '__main__':
    import sys

    claude_dir = Path.home() / '.claude'
    if len(sys.argv) > 1:
        claude_dir = Path(sys.argv[1])

    print(f"Analyzing proficiency from {claude_dir}...")

    assessment = analyze_proficiency(claude_dir)

    print(f"\n{'='*60}")
    print(f"PROMPTING PROFICIENCY ASSESSMENT")
    print(f"{'='*60}")

    print(f"\nOverall: {assessment.overall_proficiency}/100 ({assessment.proficiency_level.upper()})")

    print(f"\n--- Dimension Scores ---")
    print(f"Prompt Engineering:  {assessment.prompt_engineering_score}/100")
    print(f"  - Clarity:         {assessment.prompt_clarity_score}")
    print(f"  - Specificity:     {assessment.prompt_specificity_score}")
    print(f"  - Technique:       {assessment.prompt_technique_score}")
    print(f"  - Iteration:       {assessment.prompt_iteration_efficiency}")
    print(f"  - Gap Rate:        {assessment.prompt_gap_rate:.1%}")

    print(f"\nContext Engineering: {assessment.context_engineering_score}/100")
    print(f"  - Efficiency:      {assessment.context_efficiency_score}")
    print(f"  - Position:        {assessment.context_position_awareness}")
    print(f"  - Compression:     {assessment.context_compression_skill}")

    print(f"\nMemory Engineering:  {assessment.memory_engineering_score}/100")
    print(f"  - Continuity:      {assessment.memory_continuity_score}")
    print(f"  - Isolation:       {assessment.memory_isolation_score}")
    print(f"  - Redundancy:      {assessment.memory_redundancy_score}")

    print(f"\nTool Use:            {assessment.tool_use_score}/100")
    print(f"  - Discovery:       {assessment.tool_discovery_score}")
    print(f"  - Composition:     {assessment.tool_composition_score}")
    print(f"  - Parallelism:     {assessment.tool_parallelism_score}")
    print(f"  - Recovery:        {assessment.tool_recovery_score}")

    print(f"\n--- Insights ---")
    print(f"Top Strength: {assessment.top_strength}")
    print(f"  {assessment.top_strength_description}")
    print(f"\nPrimary Weakness: {assessment.primary_weakness}")
    print(f"  {assessment.primary_weakness_description}")

    print(f"\n--- Recommendations ---")
    for i, rec in enumerate(assessment.recommendations, 1):
        print(f"{i}. {rec}")
