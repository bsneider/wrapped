#!/usr/bin/env python3
"""
Claude Wrapped HTML Generator
Creates a stunning synthwave-themed year-in-review report.
Maximum vibes. Maximum roast energy.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import html


# Karpathy quotes for loading screens and easter eggs
KARPATHY_QUOTES = [
    "The hottest new programming language is English.",
    "I don't write code anymore, I mass-supervise.",
    "The best code is no code at all.",
    "Gradient descent can write code better than you.",
    "Just prompt it, bro.",
    "Neural networks are just spicy linear algebra.",
    "The real 10x engineer was the LLM we trained along the way.",
]

LOADING_MESSAGES = [
    "Aligning chakras...",
    "Downloading more RAM...",
    "Consulting Karpathy...",
    "Compiling vibes...",
    "Tokenizing your sins...",
    "Calculating regret coefficients...",
    "Summoning the context window...",
    "Defragmenting your ambitions...",
    "Reticulating splines...",
    "Warming up the GPU...",
]


def format_duration(ms: float) -> str:
    """Format milliseconds to human readable duration."""
    if ms < 1000:
        return f"{ms:.0f}ms"
    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = seconds / 60
    if minutes < 60:
        return f"{minutes:.1f}m"
    hours = minutes / 60
    if hours < 24:
        return f"{hours:.1f}h"
    days = hours / 24
    return f"{days:.1f}d"


def format_number(n: int) -> str:
    """Format large numbers with K/M/B suffix for display."""
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        val = n / 1000
        if val == int(val):
            return f"{int(val)}K"
        return f"{val:.1f}K"
    if n < 1_000_000_000:
        val = n / 1_000_000
        # Show cleaner numbers: 94M not 94.00M, but 94.5M when needed
        if val == int(val):
            return f"{int(val)}M"
        elif val * 10 == int(val * 10):
            return f"{val:.1f}M"
        return f"{val:.2f}M"
    val = n / 1_000_000_000
    if val == int(val):
        return f"{int(val)}B"
    return f"{val:.2f}B"


def format_number_full(n: int) -> str:
    """Format large numbers with commas for impressive display (e.g., 94,000,000)."""
    return f"{n:,}"


def format_tokens(tokens: int) -> str:
    """Format token count with abbreviated display (94M not 94.00M)."""
    if tokens < 1000:
        return str(tokens)
    if tokens < 1_000_000:
        val = tokens / 1000
        return f"{int(round(val))}K"
    if tokens < 1_000_000_000:
        val = tokens / 1_000_000
        return f"{int(round(val))}M"
    val = tokens / 1_000_000_000
    return f"{int(round(val))}B"


def format_cost(cost: float) -> str:
    """Format USD cost."""
    if cost < 0.01:
        return f"${cost:.4f}"
    if cost < 1:
        return f"${cost:.2f}"
    if cost < 1000:
        return f"${cost:.2f}"
    if cost < 1_000_000:
        return f"${cost/1000:.1f}K"
    return f"${cost/1_000_000:.2f}M"


def get_yapping_verdict(ratio: float) -> tuple[str, str]:
    """Get verdict based on user/assistant token ratio."""
    if ratio > 2:
        return "The Micromanager", "You wrote novels, Claude wrote haikus. Trust issues much?"
    if ratio > 1:
        return "The Collaborator", "Healthy back-and-forth. You might actually be normal."
    if ratio > 0.5:
        return "The Delegator", "You point, Claude codes. This is the way."
    return "The Whisperer", "Minimal input, maximum output. Peak efficiency unlocked."


def get_cache_verdict(ratio: float) -> tuple[str, str]:
    """Get verdict based on cache efficiency."""
    if ratio > 0.8:
        return "Cache Wizard", "Your context reuse is *chef's kiss*. Tokens bow before you."
    if ratio > 0.5:
        return "Cache Conscious", "Decent efficiency. Your wallet thanks you."
    if ratio > 0.2:
        return "Cache Curious", "Room for improvement. You're leaving tokens on the table."
    return "Cache Chaos", "Every conversation starts from scratch. Your API bill weeps."


def get_time_roast(hour_dist: dict) -> tuple[str, str, int]:
    """Analyze time distribution for roasts."""
    if not hour_dist:
        return "Time Traveler", "No timestamps found. Do you even exist?", -1

    # Find peak hour (keys may be strings from JSON)
    peak_hour = max(hour_dist.items(), key=lambda x: x[1])[0]
    if isinstance(peak_hour, str):
        peak_hour = int(peak_hour)

    if 0 <= peak_hour <= 4:
        return "The Vampire", f"Peak coding at {peak_hour}:00. Sleep is for the weak, apparently.", peak_hour
    if 5 <= peak_hour <= 8:
        return "The Early Bird", f"Peak coding at {peak_hour}:00. Disgusting morning person energy.", peak_hour
    if 9 <= peak_hour <= 17:
        return "The Professional", f"Peak coding at {peak_hour}:00. Normal human hours. Boring, but healthy.", peak_hour
    if 18 <= peak_hour <= 21:
        return "The Night Owl", f"Peak coding at {peak_hour}:00. Post-dinner debugging sessions.", peak_hour
    return "The Insomniac", f"Peak coding at {peak_hour}:00. The witching hour calls.", peak_hour


def generate_html(data: dict) -> str:
    """Generate the full HTML report."""
    
    # Extract key metrics
    total_sessions = data.get('total_sessions', 0)
    total_messages = data.get('total_messages', 0)
    total_tokens = data.get('total_input_tokens', 0) + data.get('total_output_tokens', 0)
    total_cost = data.get('total_cost_usd', 0)
    
    # Get verdicts
    yapping_title, yapping_desc = get_yapping_verdict(data.get('user_to_assistant_token_ratio', 1))
    cache_title, cache_desc = get_cache_verdict(data.get('cache_efficiency_ratio', 0))
    time_title, time_desc, peak_hour = get_time_roast(data.get('hourly_distribution', {}))
    
    # Format numbers - use abbreviated format for large numbers
    sessions_formatted = format_number(total_sessions)
    messages_formatted = format_number(total_messages)
    tokens_formatted = format_tokens(total_tokens)
    cost_formatted = format_cost(total_cost)
    avg_session = format_duration(data.get('average_session_duration_ms', 0))
    longest_session = format_duration(data.get('longest_session_duration_ms', 0))
    
    # Developer personality and coding city
    dev_personality = data.get('developer_personality', 'The Coder')
    personality_desc = data.get('personality_description', '')
    coding_city = data.get('coding_city', '')
    coding_city_desc = data.get('coding_city_description', '')
    
    # Top projects
    top_projects = data.get('top_projects', [])
    
    # Prepare chart data
    hourly_data = data.get('hourly_distribution', {})
    hourly_labels = [str(i) for i in range(24)]
    hourly_values = [hourly_data.get(i, hourly_data.get(str(i), 0)) for i in range(24)]
    
    weekday_data = data.get('weekday_distribution', {})
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_values = [weekday_data.get(day, 0) for day in weekday_order]
    
    tool_data = data.get('tool_frequency', {})
    tool_items = sorted(tool_data.items(), key=lambda x: x[1], reverse=True)[:10]
    tool_labels = [t[0] for t in tool_items]
    tool_values = [t[1] for t in tool_items]
    
    model_data = data.get('model_frequency', {})
    model_items = sorted(model_data.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Sessions by date for heatmap
    sessions_by_date = data.get('sessions_by_date', {})
    
    # Calculate some fun stats
    todo_completion = data.get('todo_completion_rate', 0) * 100
    orphan_todos = data.get('orphan_agent_todos', 0)
    rage_quits = data.get('shortest_sessions', 0)
    marathons = data.get('marathon_sessions', 0)
    context_collapses = data.get('total_summaries', 0)
    errors = data.get('total_errors', 0)
    sidechains = data.get('total_sidechains', 0)
    
    # Cost in burritos (assuming $12 burrito)
    burritos = total_cost / 12
    
    # Streak info
    longest_streak = data.get('longest_streak_days', 0)
    current_streak = data.get('current_streak_days', 0)
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Wrapped 2025</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --neon-pink: #ff006e;
            --neon-cyan: #00f5ff;
            --neon-purple: #8b5cf6;
            --neon-orange: #ff9500;
            --neon-green: #39ff14;
            --dark-bg: #0a0a0f;
            --card-bg: rgba(20, 20, 35, 0.8);
            --glass-border: rgba(255, 255, 255, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Rajdhani', sans-serif;
            background: var(--dark-bg);
            color: #fff;
            min-height: 100vh;
            overflow-x: hidden;
        }}
        
        /* Animated background */
        .bg-grid {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(90deg, rgba(139, 92, 246, 0.03) 1px, transparent 1px),
                linear-gradient(rgba(139, 92, 246, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: grid-move 20s linear infinite;
            pointer-events: none;
            z-index: 0;
        }}
        
        @keyframes grid-move {{
            0% {{ transform: perspective(500px) rotateX(60deg) translateY(0); }}
            100% {{ transform: perspective(500px) rotateX(60deg) translateY(50px); }}
        }}
        
        .glow-orb {{
            position: fixed;
            border-radius: 50%;
            filter: blur(80px);
            opacity: 0.4;
            pointer-events: none;
            z-index: 0;
        }}
        
        .orb-1 {{
            width: 400px;
            height: 400px;
            background: var(--neon-pink);
            top: -100px;
            left: -100px;
            animation: float 8s ease-in-out infinite;
        }}
        
        .orb-2 {{
            width: 300px;
            height: 300px;
            background: var(--neon-cyan);
            bottom: -50px;
            right: -50px;
            animation: float 10s ease-in-out infinite reverse;
        }}
        
        .orb-3 {{
            width: 250px;
            height: 250px;
            background: var(--neon-purple);
            top: 50%;
            left: 50%;
            animation: float 12s ease-in-out infinite;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translate(0, 0); }}
            50% {{ transform: translate(30px, 30px); }}
        }}
        
        /* Loading screen */
        #loading {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--dark-bg);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            transition: opacity 0.5s, visibility 0.5s;
        }}
        
        #loading.hidden {{
            opacity: 0;
            visibility: hidden;
        }}
        
        .loading-text {{
            font-family: 'Orbitron', monospace;
            font-size: 1.5rem;
            color: var(--neon-cyan);
            text-shadow: 0 0 20px var(--neon-cyan);
            animation: pulse 1.5s ease-in-out infinite;
        }}
        
        .loading-bar {{
            width: 300px;
            height: 4px;
            background: rgba(255,255,255,0.1);
            border-radius: 2px;
            margin-top: 2rem;
            overflow: hidden;
        }}
        
        .loading-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--neon-pink), var(--neon-cyan), var(--neon-purple));
            animation: loading 2s ease-in-out infinite;
        }}
        
        @keyframes loading {{
            0% {{ width: 0%; margin-left: 0; }}
            50% {{ width: 70%; margin-left: 0; }}
            100% {{ width: 0%; margin-left: 100%; }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        /* Main content */
        .container {{
            position: relative;
            z-index: 1;
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        /* Hero section */
        .hero {{
            text-align: center;
            padding: 4rem 2rem;
            margin-bottom: 3rem;
        }}
        
        .hero h1 {{
            font-family: 'Orbitron', monospace;
            font-size: clamp(3rem, 10vw, 6rem);
            font-weight: 900;
            background: linear-gradient(135deg, var(--neon-pink), var(--neon-cyan), var(--neon-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: none;
            filter: drop-shadow(0 0 30px rgba(139, 92, 246, 0.5));
            margin-bottom: 1rem;
            letter-spacing: 0.1em;
        }}
        
        .hero .year {{
            font-family: 'Orbitron', monospace;
            font-size: 1.5rem;
            color: var(--neon-cyan);
            text-shadow: 0 0 20px var(--neon-cyan);
            letter-spacing: 0.5em;
        }}
        
        .hero .subtitle {{
            font-size: 1.2rem;
            color: rgba(255,255,255,0.6);
            margin-top: 1rem;
            font-weight: 300;
        }}
        
        /* Stats grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        
        .stat-card {{
            background: var(--card-bg);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(139, 92, 246, 0.2);
        }}
        
        .stat-value {{
            font-family: 'Orbitron', monospace;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            color: rgba(255,255,255,0.6);
            margin-top: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        /* Verdict cards */
        .verdict-section {{
            margin-bottom: 3rem;
        }}
        
        .verdict-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
        }}
        
        .verdict-card {{
            background: var(--card-bg);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 2.5rem;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }}
        
        .verdict-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--neon-pink), var(--neon-cyan));
        }}
        
        .verdict-card.pink::before {{
            background: linear-gradient(90deg, var(--neon-pink), var(--neon-orange));
        }}
        
        .verdict-card.cyan::before {{
            background: linear-gradient(90deg, var(--neon-cyan), var(--neon-green));
        }}
        
        .verdict-card.purple::before {{
            background: linear-gradient(90deg, var(--neon-purple), var(--neon-pink));
        }}
        
        .verdict-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        
        .verdict-title {{
            font-family: 'Orbitron', monospace;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: var(--neon-cyan);
            text-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
        }}
        
        .verdict-subtitle {{
            font-size: 1rem;
            color: rgba(255,255,255,0.5);
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        .verdict-desc {{
            font-size: 1.1rem;
            color: rgba(255,255,255,0.8);
            line-height: 1.6;
        }}
        
        .verdict-stat {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 2rem;
            color: var(--neon-pink);
            margin-top: 1rem;
        }}
        
        /* Chart sections */
        .chart-section {{
            background: var(--card-bg);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 2rem;
            margin-bottom: 2rem;
            backdrop-filter: blur(10px);
        }}
        
        .chart-title {{
            font-family: 'Orbitron', monospace;
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
            color: var(--neon-cyan);
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        
        .chart-title span {{
            font-size: 1.5rem;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
        }}
        
        /* Bio rhythm chart */
        .bio-rhythm {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            height: 200px;
            padding: 1rem 0;
        }}
        
        .hour-bar {{
            flex: 1;
            margin: 0 2px;
            border-radius: 4px 4px 0 0;
            transition: all 0.3s;
            position: relative;
        }}
        
        .hour-bar:hover {{
            filter: brightness(1.3);
        }}
        
        .hour-bar::after {{
            content: attr(data-hour);
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.7rem;
            color: rgba(255,255,255,0.4);
        }}
        
        /* Graveyard section */
        .graveyard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }}
        
        .tombstone {{
            background: linear-gradient(180deg, #2a2a3a 0%, #1a1a2a 100%);
            border-radius: 20px 20px 0 0;
            padding: 1.5rem;
            text-align: center;
            position: relative;
        }}
        
        .tombstone::before {{
            content: '🪦';
            font-size: 2rem;
            position: absolute;
            top: -15px;
            left: 50%;
            transform: translateX(-50%);
        }}
        
        .tombstone-value {{
            font-family: 'Orbitron', monospace;
            font-size: 2rem;
            color: var(--neon-pink);
        }}
        
        .tombstone-label {{
            font-size: 0.8rem;
            color: rgba(255,255,255,0.5);
            margin-top: 0.5rem;
        }}
        
        /* Tool belt */
        .tool-belt {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            justify-content: center;
        }}
        
        .tool-item {{
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid var(--neon-purple);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .tool-name {{
            font-family: 'JetBrains Mono', monospace;
            color: var(--neon-cyan);
        }}
        
        .tool-count {{
            background: var(--neon-pink);
            color: #000;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
        }}
        
        /* Projects grid */
        .projects-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1rem;
        }}
        
        .project-card {{
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
            position: relative;
        }}
        
        .project-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(139, 92, 246, 0.2);
            border-color: var(--neon-purple);
        }}
        
        .project-rank {{
            position: absolute;
            top: -10px;
            left: -10px;
            font-size: 1.5rem;
            background: var(--card-bg);
            padding: 0.3rem 0.6rem;
            border-radius: 8px;
            border: 1px solid var(--neon-cyan);
        }}
        
        .project-name {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem;
            color: var(--neon-cyan);
            margin-bottom: 0.75rem;
            word-break: break-word;
        }}
        
        .project-stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.6);
        }}
        
        .project-stats span {{
            background: rgba(255, 255, 255, 0.1);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }}

        /* Project Groups (related projects with same folder prefix) */
        .project-groups-section {{
            margin-bottom: 2rem;
        }}

        .project-groups-title {{
            font-family: 'Orbitron', monospace;
            font-size: 1rem;
            color: var(--neon-purple);
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        .project-groups-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}

        .project-group-card {{
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(255, 0, 110, 0.05));
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            padding: 1rem;
        }}

        .project-group-header {{
            font-family: 'Orbitron', monospace;
            font-size: 1rem;
            color: var(--neon-purple);
            margin-bottom: 0.5rem;
        }}

        .project-group-items {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.7);
            line-height: 1.4;
            margin-bottom: 0.5rem;
        }}

        .project-group-count {{
            font-size: 0.75rem;
            color: var(--neon-cyan);
        }}

        /* Frameworks section */
        .frameworks-section {{
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .frameworks-title {{
            font-family: 'Orbitron', monospace;
            font-size: 1rem;
            color: var(--neon-orange);
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        .frameworks-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            justify-content: center;
        }}

        .framework-tag {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, rgba(255, 149, 0, 0.15), rgba(255, 0, 110, 0.1));
            border: 1px solid var(--neon-orange);
            border-radius: 12px;
            padding: 0.6rem 1rem;
            transition: all 0.2s;
        }}

        .framework-tag:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 149, 0, 0.3);
        }}

        .framework-icon {{
            font-size: 1.2rem;
        }}

        .framework-name {{
            font-family: 'JetBrains Mono', monospace;
            color: var(--neon-orange);
            font-size: 0.9rem;
        }}

        .framework-count {{
            background: rgba(255, 255, 255, 0.2);
            padding: 0.15rem 0.5rem;
            border-radius: 8px;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.8);
        }}
        
        /* Command/Agent/Skill cards */
        .command-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1rem;
        }}
        
        .command-card {{
            background: rgba(0, 245, 255, 0.05);
            border: 1px solid rgba(0, 245, 255, 0.2);
            border-radius: 16px;
            padding: 1.25rem;
        }}
        
        .command-card-title {{
            font-family: 'Orbitron', monospace;
            font-size: 1rem;
            color: var(--neon-cyan);
            margin-bottom: 1rem;
        }}
        
        .command-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        
        .cmd-tag, .agent-tag, .skill-tag, .task-type-tag {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
        }}

        .cmd-tag {{
            background: rgba(255, 0, 110, 0.15);
            border: 1px solid var(--neon-pink);
            color: var(--neon-pink);
        }}

        .agent-tag {{
            background: rgba(139, 92, 246, 0.15);
            border: 1px solid var(--neon-purple);
            color: var(--neon-purple);
        }}

        .skill-tag {{
            background: rgba(57, 255, 20, 0.15);
            border: 1px solid var(--neon-green);
            color: var(--neon-green);
        }}

        .task-type-tag {{
            background: rgba(0, 245, 255, 0.15);
            border: 1px solid var(--neon-cyan);
            color: var(--neon-cyan);
        }}
        
        .cmd-count {{
            background: rgba(255, 255, 255, 0.2);
            padding: 0.15rem 0.4rem;
            border-radius: 10px;
            font-size: 0.75rem;
        }}
        
        /* Money section */
        .money-section {{
            text-align: center;
            padding: 3rem;
        }}
        
        .money-value {{
            font-family: 'Orbitron', monospace;
            font-size: 4rem;
            background: linear-gradient(135deg, #ffd700, #ff6b6b, #ffd700);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: money-glow 2s ease-in-out infinite;
        }}
        
        @keyframes money-glow {{
            0%, 100% {{ filter: drop-shadow(0 0 20px rgba(255, 215, 0, 0.5)); }}
            50% {{ filter: drop-shadow(0 0 40px rgba(255, 107, 107, 0.8)); }}
        }}
        
        .burrito-equivalent {{
            font-size: 1.2rem;
            color: rgba(255,255,255,0.6);
            margin-top: 1rem;
        }}
        
        .burrito-equivalent span {{
            color: var(--neon-orange);
            font-weight: 700;
        }}
        
        /* 🌟 MEGA VISUALIZATION: Token Skyline + Activity Ring 🌟 */
        .year-in-code {{
            overflow: visible;
            position: relative;
        }}

        .heatmap-controls {{
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }}

        .heatmap-btn {{
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid var(--neon-purple);
            color: var(--neon-purple);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            transition: all 0.2s;
        }}

        .heatmap-btn:hover {{
            background: rgba(139, 92, 246, 0.3);
        }}

        .heatmap-btn.active {{
            background: var(--neon-purple);
            color: #000;
        }}

        /* Token Skyline - Futuristic city visualization */
        .skyline-wrapper {{
            position: relative;
        }}

        .skyline-total {{
            text-align: center;
            margin-bottom: 1rem;
        }}

        .skyline-total-value {{
            font-family: 'Orbitron', monospace;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .skyline-total-label {{
            font-size: 0.9rem;
            color: rgba(255,255,255,0.6);
        }}

        .skyline-months {{
            display: flex;
            justify-content: space-between;
            padding: 0 20px;
            margin-bottom: 0.5rem;
            font-size: 0.75rem;
            color: rgba(255,255,255,0.5);
        }}

        .skyline-container {{
            position: relative;
            height: 250px;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 3px;
            padding: 20px;
            background: linear-gradient(180deg, transparent 0%, rgba(139, 92, 246, 0.05) 100%);
            border-radius: 16px;
            margin-bottom: 1rem;
            overflow-x: auto;
            overflow-y: hidden;
        }}

        .skyline-container::before {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--neon-cyan), var(--neon-purple), var(--neon-pink), transparent);
            animation: skyline-glow 3s ease-in-out infinite;
        }}

        @keyframes skyline-glow {{
            0%, 100% {{ opacity: 0.5; }}
            50% {{ opacity: 1; }}
        }}

        .skyline-bar {{
            flex-shrink: 0;
            width: 10px;
            min-height: 5px;
            border-radius: 3px 3px 0 0;
            position: relative;
            cursor: pointer;
            transition: all 0.3s ease;
            animation: skyline-rise 1s ease-out forwards;
            transform-origin: bottom;
            opacity: 0;
        }}

        /* Different colors for different metrics */
        .skyline-bar.metric-sessions {{
            background: linear-gradient(180deg, var(--neon-cyan) 0%, #0891b2 100%);
        }}

        .skyline-bar.metric-tokens {{
            background: linear-gradient(180deg, var(--neon-purple) 0%, #7c3aed 100%);
        }}

        .skyline-bar.metric-cost {{
            background: linear-gradient(180deg, var(--neon-pink) 0%, #db2777 100%);
        }}

        .skyline-bar:hover {{
            filter: brightness(1.4);
            box-shadow: 0 0 20px currentColor, 0 0 40px currentColor;
            transform: scaleY(1.1) scaleX(1.5);
            z-index: 10;
        }}

        .skyline-bar::after {{
            content: attr(data-label);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.65rem;
            color: rgba(255,255,255,0.7);
            white-space: nowrap;
            opacity: 0;
            transition: opacity 0.2s;
            pointer-events: none;
            padding-bottom: 4px;
        }}

        .skyline-bar:hover::after {{
            opacity: 1;
        }}

        @keyframes skyline-rise {{
            0% {{ transform: scaleY(0); opacity: 0; }}
            100% {{ transform: scaleY(1); opacity: 1; }}
        }}

        /* Activity Ring - Circular weekly pattern */
        .activity-ring-section {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 3rem;
            flex-wrap: wrap;
            margin: 2rem 0;
        }}

        .activity-ring-container {{
            position: relative;
            width: 280px;
            height: 280px;
        }}

        .activity-ring {{
            width: 100%;
            height: 100%;
            position: relative;
        }}

        .ring-segment {{
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 50% 100%);
            transition: all 0.3s;
        }}

        .ring-center {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 160px;
            height: 160px;
            background: var(--dark-bg);
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            border: 2px solid rgba(139, 92, 246, 0.3);
        }}

        .ring-center-value {{
            font-family: 'Orbitron', monospace;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .ring-center-label {{
            font-size: 0.85rem;
            color: rgba(255,255,255,0.6);
            margin-top: 0.25rem;
        }}

        .ring-legend {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}

        .ring-legend-item {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .ring-legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
        }}

        .ring-legend-label {{
            font-size: 0.9rem;
            color: rgba(255,255,255,0.7);
        }}

        .ring-legend-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            color: var(--neon-cyan);
            margin-left: auto;
        }}

        /* Heatmap tooltip */
        .heatmap-tooltip {{
            position: fixed;
            background: rgba(10, 10, 15, 0.95);
            border: 1px solid var(--neon-purple);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.85rem;
            z-index: 1000;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            max-width: 220px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}

        .heatmap-tooltip.visible {{
            opacity: 1;
        }}

        .heatmap-tooltip .tooltip-date {{
            font-family: 'Orbitron', monospace;
            color: var(--neon-cyan);
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}

        .heatmap-tooltip .tooltip-stats {{
            display: grid;
            grid-template-columns: auto auto;
            gap: 0.25rem 0.75rem;
        }}

        .heatmap-tooltip .tooltip-label {{
            color: rgba(255,255,255,0.6);
        }}

        .heatmap-tooltip .tooltip-value {{
            color: var(--neon-pink);
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Heatmap stats */
        .heatmap-stats {{
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }}

        .heatmap-stat {{
            text-align: center;
        }}

        .heatmap-stat-value {{
            font-family: 'Orbitron', monospace;
            font-size: 2rem;
            color: var(--neon-cyan);
        }}

        .heatmap-stat-label {{
            font-size: 0.85rem;
            color: rgba(255,255,255,0.6);
            margin-top: 0.25rem;
        }}
        
        /* Fire animation for token inferno */
        .fire-container {{
            display: flex;
            justify-content: center;
            align-items: flex-end;
            height: 200px;
            position: relative;
        }}
        
        .fire {{
            width: 100px;
            height: var(--fire-height, 50%);
            background: linear-gradient(0deg, 
                var(--neon-orange) 0%, 
                var(--neon-pink) 50%, 
                var(--neon-purple) 100%);
            border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
            animation: fire-dance 0.5s ease-in-out infinite alternate;
            filter: blur(2px);
            position: relative;
        }}
        
        .fire::before, .fire::after {{
            content: '';
            position: absolute;
            background: inherit;
            border-radius: inherit;
            animation: inherit;
        }}
        
        .fire::before {{
            width: 60%;
            height: 80%;
            left: 20%;
            bottom: 10%;
            animation-delay: 0.1s;
        }}
        
        .fire::after {{
            width: 40%;
            height: 60%;
            left: 30%;
            bottom: 20%;
            animation-delay: 0.2s;
        }}
        
        @keyframes fire-dance {{
            0% {{ transform: scaleY(1) scaleX(1); }}
            100% {{ transform: scaleY(1.1) scaleX(0.9); }}
        }}
        
        /* Streak section */
        .streak-display {{
            display: flex;
            justify-content: center;
            gap: 3rem;
            flex-wrap: wrap;
        }}
        
        .streak-item {{
            text-align: center;
        }}
        
        .streak-value {{
            font-family: 'Orbitron', monospace;
            font-size: 4rem;
            color: var(--neon-green);
            text-shadow: 0 0 30px var(--neon-green);
        }}
        
        .streak-label {{
            font-size: 1rem;
            color: rgba(255,255,255,0.6);
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}
        
        /* Karpathy quote */
        .quote-section {{
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(255, 0, 110, 0.2));
            border-radius: 24px;
            padding: 3rem;
            text-align: center;
            margin: 3rem 0;
            position: relative;
        }}
        
        .quote-section::before {{
            content: '"';
            font-family: Georgia, serif;
            font-size: 8rem;
            position: absolute;
            top: -20px;
            left: 30px;
            color: rgba(255,255,255,0.1);
        }}
        
        .quote-text {{
            font-size: 1.5rem;
            font-style: italic;
            color: rgba(255,255,255,0.9);
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .quote-author {{
            margin-top: 1.5rem;
            color: var(--neon-cyan);
            font-weight: 600;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 3rem;
            color: rgba(255,255,255,0.4);
            font-size: 0.9rem;
        }}
        
        .footer a {{
            color: var(--neon-cyan);
            text-decoration: none;
        }}
        
        /* Easter egg - God Mode */
        .god-mode {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            z-index: 10000;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }}
        
        .god-mode.active {{
            display: flex;
        }}
        
        .god-mode h2 {{
            font-family: 'Orbitron', monospace;
            font-size: 3rem;
            color: var(--neon-green);
            text-shadow: 0 0 30px var(--neon-green);
            margin-bottom: 2rem;
        }}
        
        .god-mode-stats {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.2rem;
            color: var(--neon-cyan);
            text-align: left;
        }}
        
        .god-mode-close {{
            margin-top: 2rem;
            padding: 1rem 2rem;
            background: var(--neon-pink);
            border: none;
            border-radius: 8px;
            color: #000;
            font-family: 'Orbitron', monospace;
            font-weight: 700;
            cursor: pointer;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            
            .hero h1 {{
                font-size: 2.5rem;
            }}
            
            .verdict-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <!-- Loading Screen -->
    <div id="loading">
        <div class="loading-text" id="loading-message">Initializing...</div>
        <div class="loading-bar">
            <div class="loading-bar-fill"></div>
        </div>
    </div>
    
    <!-- Background effects -->
    <div class="bg-grid"></div>
    <div class="glow-orb orb-1"></div>
    <div class="glow-orb orb-2"></div>
    <div class="glow-orb orb-3"></div>
    
    <!-- God Mode Easter Egg -->
    <div class="god-mode" id="godMode">
        <h2>🔓 GOD MODE UNLOCKED</h2>
        <div class="god-mode-stats">
            <p>Raw Input Tokens: {data.get('total_input_tokens', 0):,}</p>
            <p>Raw Output Tokens: {data.get('total_output_tokens', 0):,}</p>
            <p>Cache Creation: {data.get('total_cache_creation_tokens', 0):,}</p>
            <p>Cache Read: {data.get('total_cache_read_tokens', 0):,}</p>
            <p>Total API Cost: ${total_cost:.6f}</p>
            <p>Cost per Session: ${(total_cost/max(total_sessions,1)):.6f}</p>
            <p>Cost per Message: ${(total_cost/max(total_messages,1)):.8f}</p>
            <p>Errors: {errors}</p>
            <p>Sidechains: {sidechains}</p>
            <p>Context Collapses: {context_collapses}</p>
        </div>
        <button class="god-mode-close" onclick="document.getElementById('godMode').classList.remove('active')">Close</button>
    </div>
    
    <div class="container">
        <!-- Hero -->
        <section class="hero">
            <div class="year">2 0 2 5</div>
            <h1>CLAUDE WRAPPED</h1>
            <p class="subtitle">Your year of AI-assisted chaos, quantified.</p>
        </section>
        
        <!-- Quick Stats -->
        <section class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{sessions_formatted}</div>
                <div class="stat-label">Sessions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{messages_formatted}</div>
                <div class="stat-label">Messages</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{tokens_formatted}</div>
                <div class="stat-label">Tokens</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{data.get('unique_projects', 0)}</div>
                <div class="stat-label">Projects</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{longest_session}</div>
                <div class="stat-label">Longest Session</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{longest_streak}</div>
                <div class="stat-label">Day Streak</div>
            </div>
        </section>
        
        <!-- The Money -->
        <section class="chart-section money-section">
            <div class="chart-title"><span>💸</span> The Damage</div>
            <div class="money-value">{cost_formatted}</div>
            <p class="burrito-equivalent">That's <span>${total_cost:,.2f}</span> worth of burritos (<span>{int(burritos):,}</span> at $12 each).</p>
        </section>
        
        <!-- Verdicts -->
        <section class="verdict-section">
            <div class="verdict-grid">
                <!-- Yapping Index -->
                <div class="verdict-card pink">
                    <div class="verdict-icon">🗣️</div>
                    <div class="verdict-subtitle">The Yapping Index</div>
                    <div class="verdict-title">{yapping_title}</div>
                    <div class="verdict-desc">{yapping_desc}</div>
                    <div class="verdict-stat">{data.get('user_to_assistant_token_ratio', 0):.2f}x ratio</div>
                </div>
                
                <!-- Cache Efficiency -->
                <div class="verdict-card cyan">
                    <div class="verdict-icon">🧠</div>
                    <div class="verdict-subtitle">Cache Efficiency</div>
                    <div class="verdict-title">{cache_title}</div>
                    <div class="verdict-desc">{cache_desc}</div>
                    <div class="verdict-stat">{data.get('cache_efficiency_ratio', 0)*100:.1f}% reuse</div>
                </div>
                
                <!-- Bio Rhythm -->
                <div class="verdict-card purple">
                    <div class="verdict-icon">🌙</div>
                    <div class="verdict-subtitle">Bio Rhythm</div>
                    <div class="verdict-title">{time_title}</div>
                    <div class="verdict-desc">{time_desc}</div>
                </div>
            </div>
        </section>
        
        <!-- Developer Personality & Coding City -->
        <section class="verdict-section">
            <div class="verdict-grid">
                <!-- Developer Personality -->
                <div class="verdict-card pink" style="grid-column: span 1;">
                    <div class="verdict-icon">🎭</div>
                    <div class="verdict-subtitle">Your Developer Personality</div>
                    <div class="verdict-title">{dev_personality}</div>
                    <div class="verdict-desc">{personality_desc}</div>
                </div>
                
                <!-- Coding City -->
                <div class="verdict-card cyan" style="grid-column: span 1;">
                    <div class="verdict-icon">🏙️</div>
                    <div class="verdict-subtitle">Your Coding City</div>
                    <div class="verdict-title">{coding_city}</div>
                    <div class="verdict-desc">{coding_city_desc}</div>
                </div>
            </div>
        </section>
        
        <!-- Top Projects Explorer -->
        <section class="chart-section">
            <div class="chart-title"><span>📁</span> Top Projects</div>
            <div class="projects-grid">
                {generate_top_projects_html(top_projects, data.get('project_groups', {}), data.get('smart_project_groups', {}))}
            </div>
        </section>
        
        <!-- Bio Rhythm Chart -->
        <section class="chart-section">
            <div class="chart-title"><span>⏰</span> When You Code</div>
            <div class="chart-container">
                <canvas id="hourlyChart"></canvas>
            </div>
        </section>
        
        <!-- Weekday Distribution -->
        <section class="chart-section">
            <div class="chart-title"><span>📅</span> Weekday Warrior</div>
            <div class="chart-container">
                <canvas id="weekdayChart"></canvas>
            </div>
        </section>
        
        <!-- 🌟 MEGA CHART: Token Skyline 🌟 -->
        <section class="chart-section year-in-code">
            <div class="chart-title"><span>🏙️</span> Your Coding Skyline</div>
            <p style="text-align: center; color: rgba(255,255,255,0.5); margin-bottom: 1rem; font-size: 0.9rem;">
                Each bar is a day. Hover for details. Different colors = different metrics.
            </p>
            <div class="heatmap-controls">
                <button class="heatmap-btn active" data-metric="sessions" style="border-color: var(--neon-cyan); color: var(--neon-cyan);">📊 Sessions</button>
                <button class="heatmap-btn" data-metric="tokens" style="border-color: var(--neon-purple); color: var(--neon-purple);">🔤 Tokens</button>
                <button class="heatmap-btn" data-metric="cost" style="border-color: var(--neon-pink); color: var(--neon-pink);">💰 Cost</button>
            </div>
            <div class="skyline-wrapper">
                <div class="skyline-total">
                    <div class="skyline-total-value" id="skylineTotalValue">0</div>
                    <div class="skyline-total-label" id="skylineTotalLabel">Total Sessions</div>
                </div>
                <div class="skyline-months" id="skylineMonths"></div>
                <div class="skyline-container" id="skylineContainer"></div>
            </div>
            <div class="heatmap-tooltip" id="heatmapTooltip"></div>
            <div class="heatmap-stats" id="heatmapStats">
                <div class="heatmap-stat">
                    <div class="heatmap-stat-value" id="statTotalDays">0</div>
                    <div class="heatmap-stat-label">Active Days</div>
                </div>
                <div class="heatmap-stat">
                    <div class="heatmap-stat-value" id="statBestDay">-</div>
                    <div class="heatmap-stat-label">Most Productive Day</div>
                </div>
                <div class="heatmap-stat">
                    <div class="heatmap-stat-value" id="statBestMonth">-</div>
                    <div class="heatmap-stat-label">Best Month</div>
                </div>
            </div>

            <!-- Activity Ring: Weekly Pattern -->
            <div class="chart-title" style="margin-top: 3rem;"><span>🎯</span> Weekly Activity Ring</div>
            <div class="activity-ring-section">
                <div class="activity-ring-container">
                    <canvas id="activityRing" width="280" height="280"></canvas>
                    <div class="ring-center">
                        <div class="ring-center-value" id="ringTotal">0</div>
                        <div class="ring-center-label">Total Sessions</div>
                    </div>
                </div>
                <div class="ring-legend" id="ringLegend"></div>
            </div>
        </section>
        
        <!-- The Graveyard -->
        <section class="chart-section">
            <div class="chart-title"><span>🪦</span> The Graveyard of Good Intentions</div>
            <div class="graveyard">
                <div class="tombstone">
                    <div class="tombstone-value">{rage_quits}</div>
                    <div class="tombstone-label">Rage Quits<br><small>(&lt;2 min sessions)</small></div>
                </div>
                <div class="tombstone">
                    <div class="tombstone-value">{len(data.get('abandoned_projects', []))}</div>
                    <div class="tombstone-label">Abandoned<br>Projects</div>
                </div>
                <div class="tombstone">
                    <div class="tombstone-value">{orphan_todos}</div>
                    <div class="tombstone-label">Orphaned<br>Agent Tasks</div>
                </div>
                <div class="tombstone">
                    <div class="tombstone-value">{context_collapses}</div>
                    <div class="tombstone-label">Context<br>Collapses</div>
                </div>
                <div class="tombstone">
                    <div class="tombstone-value">{100-todo_completion:.0f}%</div>
                    <div class="tombstone-label">Todos Never<br>Completed</div>
                </div>
            </div>
        </section>
        
        <!-- Tool Belt -->
        <section class="chart-section">
            <div class="chart-title"><span>🛠️</span> Your Tool Belt</div>
            <div class="chart-container">
                <canvas id="toolChart"></canvas>
            </div>
        </section>
        
        <!-- Streaks -->
        <section class="chart-section">
            <div class="chart-title"><span>🔥</span> Streaks</div>
            <div class="streak-display">
                <div class="streak-item">
                    <div class="streak-value">{longest_streak}</div>
                    <div class="streak-label">Longest Streak (Days)</div>
                </div>
                <div class="streak-item">
                    <div class="streak-value">{current_streak}</div>
                    <div class="streak-label">Current Streak</div>
                </div>
                <div class="streak-item">
                    <div class="streak-value">{marathons}</div>
                    <div class="streak-label">Marathon Sessions (&gt;2h)</div>
                </div>
            </div>
        </section>
        
        <!-- Models Used -->
        <section class="chart-section">
            <div class="chart-title"><span>🤖</span> Model Promiscuity</div>
            <div class="tool-belt">
                {generate_model_tags(model_items)}
            </div>
        </section>
        
        <!-- Commands, Agents & Skills -->
        <section class="chart-section">
            <div class="chart-title"><span>⚡</span> Commands, Agents & Skills</div>
            <div class="command-grid">
                {generate_command_cards(data)}
            </div>
            {generate_frameworks_html(data)}
        </section>

        <!-- Karpathy Quote -->
        <section class="quote-section">
            <p class="quote-text">{KARPATHY_QUOTES[hash(str(total_tokens)) % len(KARPATHY_QUOTES)]}</p>
            <p class="quote-author">— Andrei Karpathy (probably)</p>
        </section>
        
        <!-- Footer -->
        <footer class="footer">
            <p>Generated with 💜 by Claude Wrapped</p>
            <p style="margin-top: 0.5rem; font-size: 0.8rem;">
                <em>Tip: Konami code (↑↑↓↓←→←→BA) or tap the title 7x for God Mode</em>
            </p>
        </footer>
    </div>
    
    <script>
        // Loading screen
        const loadingMessages = {json.dumps(LOADING_MESSAGES)};
        let msgIndex = 0;
        const loadingEl = document.getElementById('loading-message');
        
        const loadingInterval = setInterval(() => {{
            loadingEl.textContent = loadingMessages[msgIndex % loadingMessages.length];
            msgIndex++;
        }}, 400);
        
        setTimeout(() => {{
            clearInterval(loadingInterval);
            document.getElementById('loading').classList.add('hidden');
        }}, 2500);
        
        // Konami code easter egg (keyboard)
        const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'KeyB', 'KeyA'];
        let konamiIndex = 0;
        
        document.addEventListener('keydown', (e) => {{
            if (e.code === konamiCode[konamiIndex]) {{
                konamiIndex++;
                if (konamiIndex === konamiCode.length) {{
                    document.getElementById('godMode').classList.add('active');
                    konamiIndex = 0;
                }}
            }} else {{
                konamiIndex = 0;
            }}
        }});
        
        // Mobile easter egg: tap the title 7 times quickly to unlock God Mode
        let tapCount = 0;
        let tapTimer = null;
        const heroTitle = document.querySelector('.hero h1');
        
        if (heroTitle) {{
            heroTitle.style.cursor = 'pointer';
            heroTitle.addEventListener('click', () => {{
                tapCount++;
                
                // Reset tap count after 2 seconds of no taps
                if (tapTimer) clearTimeout(tapTimer);
                tapTimer = setTimeout(() => {{
                    tapCount = 0;
                }}, 2000);
                
                // 7 taps unlocks God Mode
                if (tapCount >= 7) {{
                    document.getElementById('godMode').classList.add('active');
                    tapCount = 0;
                    // Add a little feedback
                    heroTitle.style.transform = 'scale(1.1)';
                    setTimeout(() => {{
                        heroTitle.style.transform = 'scale(1)';
                    }}, 200);
                }}
            }});
        }}
        
        // Charts
        const neonPink = '#ff006e';
        const neonCyan = '#00f5ff';
        const neonPurple = '#8b5cf6';
        const neonOrange = '#ff9500';
        const neonGreen = '#39ff14';
        
        // Hourly chart
        new Chart(document.getElementById('hourlyChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(hourly_labels)},
                datasets: [{{
                    label: 'Sessions',
                    data: {json.dumps(hourly_values)},
                    backgroundColor: (ctx) => {{
                        const hour = ctx.dataIndex;
                        if (hour >= 0 && hour <= 5) return neonPurple;
                        if (hour >= 6 && hour <= 11) return neonOrange;
                        if (hour >= 12 && hour <= 17) return neonCyan;
                        return neonPink;
                    }},
                    borderRadius: 4,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                }},
                scales: {{
                    x: {{
                        grid: {{ color: 'rgba(255,255,255,0.05)' }},
                        ticks: {{ color: 'rgba(255,255,255,0.5)' }}
                    }},
                    y: {{
                        grid: {{ color: 'rgba(255,255,255,0.05)' }},
                        ticks: {{ color: 'rgba(255,255,255,0.5)' }}
                    }}
                }}
            }}
        }});
        
        // Weekday chart
        new Chart(document.getElementById('weekdayChart'), {{
            type: 'bar',
            data: {{
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{{
                    label: 'Sessions',
                    data: {json.dumps(weekday_values)},
                    backgroundColor: [neonCyan, neonCyan, neonCyan, neonCyan, neonCyan, neonPink, neonPink],
                    borderRadius: 8,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                }},
                scales: {{
                    x: {{
                        grid: {{ color: 'rgba(255,255,255,0.05)' }},
                        ticks: {{ color: 'rgba(255,255,255,0.5)' }}
                    }},
                    y: {{
                        grid: {{ color: 'rgba(255,255,255,0.05)' }},
                        ticks: {{ color: 'rgba(255,255,255,0.5)' }}
                    }}
                }}
            }}
        }});
        
        // Tool chart
        new Chart(document.getElementById('toolChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(tool_labels)},
                datasets: [{{
                    data: {json.dumps(tool_values)},
                    backgroundColor: [neonPink, neonCyan, neonPurple, neonOrange, neonGreen, '#ff6b6b', '#4ecdc4', '#ffe66d', '#95e1d3', '#f38181'],
                    borderWidth: 0,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{
                            color: 'rgba(255,255,255,0.7)',
                            font: {{ family: "'JetBrains Mono', monospace" }}
                        }}
                    }}
                }}
            }}
        }});
        
        // 🌟 TOKEN SKYLINE + ACTIVITY RING 🌟
        (function() {{
            const sessionsData = {json.dumps(sessions_by_date)};
            const tokensData = {json.dumps(data.get('tokens_by_date', {}))};
            const costData = {json.dumps(data.get('cost_by_date', {}))};
            const weekdayData = {json.dumps(dict(weekday_data))};

            const skylineContainer = document.getElementById('skylineContainer');
            const tooltip = document.getElementById('heatmapTooltip');
            const statTotalDays = document.getElementById('statTotalDays');
            const statBestDay = document.getElementById('statBestDay');
            const statBestMonth = document.getElementById('statBestMonth');
            const ringCanvas = document.getElementById('activityRing');
            const ringTotal = document.getElementById('ringTotal');
            const ringLegend = document.getElementById('ringLegend');

            let currentMetric = 'sessions';
            let bars = [];

            // Collect all dates with data and sort them
            const allDates = [...new Set([
                ...Object.keys(sessionsData),
                ...Object.keys(tokensData),
                ...Object.keys(costData)
            ])].filter(d => sessionsData[d] > 0 || tokensData[d] > 0 || costData[d] > 0).sort();

            function getData(metric) {{
                return metric === 'sessions' ? sessionsData :
                       metric === 'tokens' ? tokensData : costData;
            }}

            function formatValue(value, metric) {{
                if (metric === 'tokens') {{
                    if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M';
                    if (value >= 1000) return (value / 1000).toFixed(1) + 'K';
                    return value;
                }}
                if (metric === 'cost') return '$' + parseFloat(value).toFixed(2);
                return value;
            }}

            function showTooltip(e, dateStr) {{
                const date = new Date(dateStr);
                const formattedDate = date.toLocaleDateString('en-US', {{
                    weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
                }});

                tooltip.innerHTML = `
                    <div class="tooltip-date">${{formattedDate}}</div>
                    <div class="tooltip-stats">
                        <span class="tooltip-label">Sessions:</span>
                        <span class="tooltip-value">${{sessionsData[dateStr] || 0}}</span>
                        <span class="tooltip-label">Tokens:</span>
                        <span class="tooltip-value">${{formatValue(tokensData[dateStr] || 0, 'tokens')}}</span>
                        <span class="tooltip-label">Cost:</span>
                        <span class="tooltip-value">${{formatValue(costData[dateStr] || 0, 'cost')}}</span>
                    </div>
                `;

                tooltip.style.left = e.pageX + 15 + 'px';
                tooltip.style.top = e.pageY - 10 + 'px';
                tooltip.classList.add('visible');
            }}

            function hideTooltip() {{
                tooltip.classList.remove('visible');
            }}

            const skylineTotalValue = document.getElementById('skylineTotalValue');
            const skylineTotalLabel = document.getElementById('skylineTotalLabel');
            const skylineMonths = document.getElementById('skylineMonths');

            function buildSkyline(metric) {{
                skylineContainer.innerHTML = '';
                bars = [];
                const data = getData(metric);
                const values = allDates.map(d => data[d] || 0);
                const max = Math.max(...values, 1);
                const total = values.reduce((a, b) => a + b, 0);

                // Update total display
                if (metric === 'sessions') {{
                    skylineTotalValue.textContent = total.toLocaleString();
                    skylineTotalLabel.textContent = 'Total Sessions';
                }} else if (metric === 'tokens') {{
                    skylineTotalValue.textContent = (total / 1000000).toFixed(1) + 'M';
                    skylineTotalLabel.textContent = 'Total Tokens';
                }} else {{
                    skylineTotalValue.textContent = '$' + total.toFixed(2);
                    skylineTotalLabel.textContent = 'Total Cost';
                }}

                // Build month labels
                const months = {{}};
                allDates.forEach(d => {{
                    const m = d.substring(0, 7);
                    if (!months[m]) months[m] = true;
                }});
                skylineMonths.innerHTML = Object.keys(months).map(m => {{
                    const date = new Date(m + '-01');
                    return `<span>${{date.toLocaleDateString('en-US', {{ month: 'short' }})}}</span>`;
                }}).join('');

                allDates.forEach((dateStr, i) => {{
                    const value = data[dateStr] || 0;
                    const height = Math.max(8, (value / max) * 200); // Min height 8px, max 200px

                    const bar = document.createElement('div');
                    bar.className = `skyline-bar metric-${{metric}}`;
                    bar.style.height = height + 'px';
                    bar.style.animationDelay = (i * 40) + 'ms';
                    bar.dataset.date = dateStr;
                    bar.dataset.value = value;

                    // Add data label for hover
                    if (metric === 'sessions') {{
                        bar.dataset.label = value;
                    }} else if (metric === 'tokens') {{
                        bar.dataset.label = value >= 1000000 ? (value/1000000).toFixed(1) + 'M' : value >= 1000 ? (value/1000).toFixed(0) + 'K' : value;
                    }} else {{
                        bar.dataset.label = '$' + value.toFixed(2);
                    }}

                    bar.addEventListener('mouseenter', (e) => showTooltip(e, dateStr));
                    bar.addEventListener('mouseleave', hideTooltip);

                    skylineContainer.appendChild(bar);
                    bars.push(bar);
                }});

                // Update stats
                updateStats(metric);
            }}

            function updateStats(metric) {{
                const data = getData(metric);
                const activeDays = Object.keys(data).filter(k => data[k] > 0).length;
                statTotalDays.textContent = activeDays;

                // Find best day
                let bestDay = '';
                let bestDayValue = 0;
                for (const [date, value] of Object.entries(data)) {{
                    if (value > bestDayValue) {{
                        bestDayValue = value;
                        bestDay = date;
                    }}
                }}
                if (bestDay) {{
                    const d = new Date(bestDay);
                    statBestDay.textContent = d.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric' }});
                }}

                // Find best month
                const monthTotals = {{}};
                for (const [date, value] of Object.entries(data)) {{
                    const month = date.substring(0, 7);
                    monthTotals[month] = (monthTotals[month] || 0) + value;
                }}
                let bestMonth = '';
                let bestMonthValue = 0;
                for (const [month, value] of Object.entries(monthTotals)) {{
                    if (value > bestMonthValue) {{
                        bestMonthValue = value;
                        bestMonth = month;
                    }}
                }}
                if (bestMonth) {{
                    const d = new Date(bestMonth + '-01');
                    statBestMonth.textContent = d.toLocaleDateString('en-US', {{ month: 'long' }});
                }}
            }}

            // Activity Ring - Weekly Pattern
            function drawActivityRing() {{
                const ctx = ringCanvas.getContext('2d');
                const centerX = 140;
                const centerY = 140;
                const outerRadius = 130;
                const innerRadius = 85;

                const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
                const colors = ['#00f5ff', '#00d4e6', '#8b5cf6', '#a78bfa', '#ff006e', '#ff4d8d', '#ff9500'];
                const values = days.map(d => weekdayData[d] || 0);
                const total = values.reduce((a, b) => a + b, 0);

                ringTotal.textContent = total;

                ctx.clearRect(0, 0, 280, 280);

                if (total === 0) return;

                let startAngle = -Math.PI / 2; // Start at top

                days.forEach((day, i) => {{
                    const value = values[i];
                    if (value === 0) return;

                    const sweepAngle = (value / total) * 2 * Math.PI;
                    const endAngle = startAngle + sweepAngle;

                    // Draw arc segment
                    ctx.beginPath();
                    ctx.arc(centerX, centerY, outerRadius, startAngle, endAngle);
                    ctx.arc(centerX, centerY, innerRadius, endAngle, startAngle, true);
                    ctx.closePath();

                    // Gradient fill
                    const gradient = ctx.createRadialGradient(centerX, centerY, innerRadius, centerX, centerY, outerRadius);
                    gradient.addColorStop(0, colors[i] + '80');
                    gradient.addColorStop(1, colors[i]);
                    ctx.fillStyle = gradient;
                    ctx.fill();

                    // Glow effect
                    ctx.shadowColor = colors[i];
                    ctx.shadowBlur = 15;
                    ctx.fill();
                    ctx.shadowBlur = 0;

                    startAngle = endAngle;
                }});

                // Build legend
                ringLegend.innerHTML = days.map((day, i) => `
                    <div class="ring-legend-item">
                        <div class="ring-legend-color" style="background: ${{colors[i]}};"></div>
                        <span class="ring-legend-label">${{day.slice(0, 3)}}</span>
                        <span class="ring-legend-value">${{values[i]}}</span>
                    </div>
                `).join('');
            }}

            // Button handlers
            document.querySelectorAll('.heatmap-btn').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    document.querySelectorAll('.heatmap-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    currentMetric = btn.dataset.metric;
                    buildSkyline(currentMetric);
                }});
            }});

            // Initial render with delay for dramatic effect
            setTimeout(() => {{
                buildSkyline('sessions');
                drawActivityRing();
            }}, 2600);
        }})();
    </script>
</body>
</html>'''
    
    return html_content


def generate_model_tags(model_items: list) -> str:
    """Generate HTML for model usage tags."""
    if not model_items:
        return '<div class="tool-item"><span class="tool-name">No models tracked</span></div>'
    
    tags = []
    for model, count in model_items:
        # Clean up model name for display
        display_name = model.replace('claude-', '').replace('-20250', ' (')
        if '(' in display_name:
            display_name += ')'
        tags.append(f'<div class="tool-item"><span class="tool-name">{html.escape(display_name)}</span><span class="tool-count">{count}</span></div>')
    
    return '\n'.join(tags)


def generate_top_projects_html(projects: list, project_groups: dict = None, smart_groups: dict = None) -> str:
    """Generate HTML for top projects section with optional grouping."""
    if not projects:
        return '<div class="project-card"><div class="project-name">No projects found</div></div>'

    # If we have smart groups (from project analyzer), show those first
    grouped_html = ''
    if smart_groups:
        group_cards = []
        # Prioritize framework and cluster groups
        priority_order = ['cluster:', 'framework:', 'category:']
        sorted_groups = sorted(
            smart_groups.items(),
            key=lambda x: (
                next((i for i, p in enumerate(priority_order) if x[0].startswith(p)), len(priority_order)),
                -len(x[1])
            )
        )

        for group_key, proj_names in sorted_groups[:6]:  # Show top 6 smart groups
            if len(proj_names) < 2:
                continue

            # Parse group key for display
            if ':' in group_key:
                group_type, group_name = group_key.split(':', 1)
                if group_type == 'cluster':
                    icon = '🔗'
                    label = group_name.title()
                elif group_type == 'framework':
                    icon = '🛠️'
                    label = group_name
                else:
                    icon = '📂'
                    label = group_name.title()
            else:
                icon = '📁'
                label = group_key.title()

            # Shorten project names
            short_names = [html.escape(pn.split('-')[-1] if '-' in pn else pn) for pn in proj_names[:4]]

            group_cards.append(f'''
                <div class="project-group-card">
                    <div class="project-group-header">{icon} {html.escape(label)}</div>
                    <div class="project-group-items">{' · '.join(short_names)}{' +' + str(len(proj_names)-4) if len(proj_names) > 4 else ''}</div>
                    <div class="project-group-count">{len(proj_names)} related projects</div>
                </div>
            ''')

        if group_cards:
            grouped_html = f'<div class="project-groups-section"><div class="project-groups-title">Smart Project Groups</div><div class="project-groups-grid">{"".join(group_cards)}</div></div>'

    # Fallback to simple folder-based groups if no smart groups
    elif project_groups:
        group_cards = []
        for folder, proj_names in sorted(project_groups.items(), key=lambda x: -len(x[1])):
            if len(proj_names) > 1:
                short_names = []
                for pn in proj_names[:4]:
                    short = pn
                    if pn.lower().startswith(folder):
                        short = pn[len(folder):].lstrip('-_')
                        if not short:
                            short = pn
                    short_names.append(html.escape(short))

                group_cards.append(f'''
                    <div class="project-group-card">
                        <div class="project-group-header">📁 {html.escape(folder.title())}</div>
                        <div class="project-group-items">{' · '.join(short_names)}{' +' + str(len(proj_names)-4) if len(proj_names) > 4 else ''}</div>
                        <div class="project-group-count">{len(proj_names)} related projects</div>
                    </div>
                ''')
        if group_cards:
            grouped_html = f'<div class="project-groups-section"><div class="project-groups-title">Project Families</div><div class="project-groups-grid">{"".join(group_cards[:4])}</div></div>'

    # Individual project cards
    cards = []
    for i, proj in enumerate(projects[:8]):  # Show top 8
        # Use display_name if available, otherwise name
        name = html.escape(proj.get('display_name', proj.get('name', 'Unknown')))
        sessions = proj.get('sessions', 0)
        messages = proj.get('messages', 0)
        tokens = format_number(proj.get('tokens', 0))
        cost = format_cost(proj.get('cost', 0))

        # Rank badge
        if i == 0:
            badge = '🥇'
        elif i == 1:
            badge = '🥈'
        elif i == 2:
            badge = '🥉'
        else:
            badge = f'#{i+1}'

        cards.append(f'''
            <div class="project-card">
                <div class="project-rank">{badge}</div>
                <div class="project-name">{name}</div>
                <div class="project-stats">
                    <span>{sessions} sessions</span>
                    <span>{messages} msgs</span>
                    <span>{tokens} tokens</span>
                </div>
            </div>
        ''')

    return grouped_html + '\n'.join(cards)


def generate_frameworks_html(data: dict) -> str:
    """Generate HTML for detected frameworks/tools section."""
    top_frameworks = data.get('top_frameworks', [])

    if not top_frameworks:
        return ''

    items = []
    # Framework icons
    framework_icons = {
        'claude-flow': '🌊',
        'sparc': '⚡',
        'agentic-engineering': '🤖',
        'coscientist': '🔬',
        'mcp': '🔌',
        'langchain': '🔗',
        'crewai': '👥',
    }

    for framework, count in top_frameworks[:8]:
        icon = framework_icons.get(framework, '📦')
        items.append(f'''
            <div class="framework-tag">
                <span class="framework-icon">{icon}</span>
                <span class="framework-name">{html.escape(framework)}</span>
                <span class="framework-count">{count}</span>
            </div>
        ''')

    return f'''
        <div class="frameworks-section">
            <div class="frameworks-title">Detected Frameworks & Tools</div>
            <div class="frameworks-grid">{"".join(items)}</div>
        </div>
    '''


def generate_command_cards(data: dict) -> str:
    """Generate HTML for commands, agents, and skills used."""

    top_commands = data.get('top_commands', [])
    top_agents = data.get('top_agents', [])
    top_skills = data.get('top_skills', [])
    top_task_agent_types = data.get('top_task_agent_types', [])

    sections = []

    # Commands section
    if top_commands:
        cmd_items = ''.join([
            f'<span class="cmd-tag">/{html.escape(cmd)}<span class="cmd-count">{count}</span></span>'
            for cmd, count in top_commands[:6]
        ])
        sections.append(f'''
            <div class="command-card">
                <div class="command-card-title">📋 Slash Commands</div>
                <div class="command-tags">{cmd_items}</div>
            </div>
        ''')

    # Agents section
    if top_agents:
        agent_items = ''.join([
            f'<span class="agent-tag">@{html.escape(agent)}<span class="cmd-count">{count}</span></span>'
            for agent, count in top_agents[:6]
        ])
        sections.append(f'''
            <div class="command-card">
                <div class="command-card-title">🤖 Agents Used</div>
                <div class="command-tags">{agent_items}</div>
            </div>
        ''')

    # Task Agent Types section (Explore, Plan, general-purpose, etc.)
    if top_task_agent_types:
        type_items = ''.join([
            f'<span class="task-type-tag">{html.escape(agent_type)}<span class="cmd-count">{count}</span></span>'
            for agent_type, count in top_task_agent_types[:6]
        ])
        sections.append(f'''
            <div class="command-card">
                <div class="command-card-title">🚀 Task Subagents</div>
                <div class="command-tags">{type_items}</div>
            </div>
        ''')

    # Skills section
    if top_skills:
        skill_items = ''.join([
            f'<span class="skill-tag">{html.escape(skill)}<span class="cmd-count">{count}</span></span>'
            for skill, count in top_skills[:6]
        ])
        sections.append(f'''
            <div class="command-card">
                <div class="command-card-title">✨ Skills Activated</div>
                <div class="command-tags">{skill_items}</div>
            </div>
        ''')

    if not sections:
        return '<p style="text-align: center; color: rgba(255,255,255,0.5);">No commands, agents, or skills detected yet. Start using /commands and @agents!</p>'

    return '\n'.join(sections)


def main():
    """Main entry point."""
    import sys
    
    # Read JSON data from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    
    html_output = generate_html(data)
    print(html_output)


if __name__ == '__main__':
    main()
