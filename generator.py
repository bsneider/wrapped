#!/usr/bin/env python3
"""
Claude Wrapped HTML Generator
Creates a stunning synthwave-themed year-in-review report.
Maximum vibes. Maximum roast energy.
"""

import json
import sys
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


def get_bio_rhythm_icon(peak_hour: int) -> str:
    """Get appropriate icon for time of day."""
    if peak_hour < 0:
        return "⏰"
    if 0 <= peak_hour <= 4:
        return "🌙"  # Late night/early morning - moon
    if 5 <= peak_hour <= 8:
        return "🌅"  # Early morning - sunrise
    if 9 <= peak_hour <= 11:
        return "☀️"  # Morning - sun
    if 12 <= peak_hour <= 14:
        return "🌞"  # Midday - bright sun
    if 15 <= peak_hour <= 17:
        return "🌤️"  # Afternoon - sun with cloud
    if 18 <= peak_hour <= 20:
        return "🌆"  # Evening - sunset
    return "🌙"  # Night - moon


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
    bio_rhythm_icon = get_bio_rhythm_icon(peak_hour)
    
    # Format numbers - use abbreviated format for large numbers
    sessions_formatted = format_number(total_sessions)
    messages_formatted = format_number(total_messages)
    tokens_formatted = format_tokens(total_tokens)
    cost_formatted = format_cost(total_cost)
    longest_session = format_duration(data.get('longest_session_duration_ms', 0))
    
    # Developer personality and coding city
    dev_personality = data.get('developer_personality', 'The Coder')
    personality_desc = data.get('personality_description', '')
    coding_city = data.get('coding_city', '')
    coding_city_desc = data.get('coding_city_description', '')
    
    # Top projects - prefer combined (Claude + Git) rankings when available
    top_projects = data.get('top_projects_combined', []) or data.get('top_projects', [])
    
    # Prepare chart data
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
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
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
            cursor: help;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .tombstone:hover {{
            transform: translateY(-3px);
            box-shadow: 0 5px 20px rgba(255, 0, 110, 0.3);
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

        /* Tooltip for tombstones */
        .tombstone-tooltip {{
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid var(--neon-pink);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.9);
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.2s, visibility 0.2s;
            z-index: 100;
            pointer-events: none;
        }}

        .tombstone-tooltip::after {{
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 6px solid transparent;
            border-top-color: var(--neon-pink);
        }}

        .tombstone:hover .tombstone-tooltip {{
            opacity: 1;
            visibility: visible;
        }}

        /* Context Health section */
        .context-health {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }}

        .context-metric {{
            background: linear-gradient(135deg, rgba(0, 245, 255, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(0, 245, 255, 0.3);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .context-metric::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple));
        }}

        .context-metric-value {{
            font-family: 'Orbitron', monospace;
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .context-metric-label {{
            font-size: 0.85rem;
            color: rgba(255,255,255,0.7);
            margin-top: 0.5rem;
        }}

        .context-metric-detail {{
            font-size: 0.75rem;
            color: rgba(255,255,255,0.5);
            margin-top: 0.25rem;
            font-family: 'JetBrains Mono', monospace;
        }}

        .context-health-bar {{
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            margin-top: 1rem;
            overflow: hidden;
        }}

        .context-health-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple), var(--neon-pink));
            border-radius: 4px;
            transition: width 0.5s ease;
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

        .project-stats .no-claude {{
            background: rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.4);
            font-style: italic;
        }}

        .project-git-stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            font-size: 0.8rem;
            color: rgba(0, 245, 255, 0.7);
            margin-top: 0.3rem;
        }}

        .project-git-stats span {{
            background: rgba(0, 245, 255, 0.1);
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            border: 1px solid rgba(0, 245, 255, 0.2);
        }}

        .source-badge {{
            font-size: 0.9rem;
            margin-right: 0.3rem;
        }}

        .project-card.git-only {{
            border-color: rgba(0, 245, 255, 0.3);
            background: linear-gradient(145deg, rgba(0, 245, 255, 0.05) 0%, rgba(17, 24, 39, 0.9) 100%);
        }}

        .project-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .project-category {{
            font-size: 0.7rem;
            padding: 0.15rem 0.5rem;
            background: rgba(139, 92, 246, 0.3);
            border-radius: 8px;
            color: var(--neon-purple);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .project-tech-stack {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.3rem;
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .project-tech-tag {{
            font-size: 0.65rem;
            padding: 0.1rem 0.4rem;
            background: rgba(0, 245, 255, 0.15);
            border: 1px solid rgba(0, 245, 255, 0.3);
            border-radius: 4px;
            color: var(--neon-cyan);
            font-family: 'JetBrains Mono', monospace;
        }}

        .project-components {{
            display: flex;
            gap: 0.3rem;
            margin-left: auto;
        }}

        .project-component-tag {{
            font-size: 1rem;
            cursor: help;
        }}

        .project-summary {{
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.7);
            font-style: italic;
            margin: 0.3rem 0;
            padding-left: 0.5rem;
            border-left: 2px solid var(--neon-purple);
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

        .frameworks-subsection {{
            margin-bottom: 1.5rem;
        }}

        .frameworks-subsection:last-child {{
            margin-bottom: 0;
        }}

        .concepts-title {{
            font-family: 'Orbitron', monospace;
            font-size: 1rem;
            color: var(--neon-green);
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        .concept-tag {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, rgba(57, 255, 20, 0.15), rgba(0, 245, 255, 0.1));
            border: 1px solid var(--neon-green);
            border-radius: 12px;
            padding: 0.6rem 1rem;
            transition: all 0.2s;
        }}

        .concept-tag:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(57, 255, 20, 0.3);
        }}

        .concept-icon {{
            font-size: 1.2rem;
        }}

        .concept-name {{
            font-family: 'JetBrains Mono', monospace;
            color: var(--neon-green);
            font-size: 0.9rem;
        }}

        .concept-count {{
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
            height: 280px;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 2px;
            padding: 30px 20px 20px 20px;
            background: linear-gradient(180deg, transparent 0%, rgba(139, 92, 246, 0.05) 100%);
            border-radius: 16px;
            margin-bottom: 1rem;
            overflow-x: auto;
            overflow-y: hidden;
            /* 3D Perspective */
            perspective: 1000px;
            transform-style: preserve-3d;
        }}

        .skyline-container::before {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: linear-gradient(180deg, transparent 0%, rgba(139, 92, 246, 0.15) 50%, rgba(0, 245, 255, 0.1) 100%);
            transform: rotateX(60deg) translateZ(-20px);
            transform-origin: bottom;
            border-radius: 0 0 16px 16px;
        }}

        .skyline-container::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--neon-cyan), var(--neon-purple), var(--neon-pink), transparent);
            animation: skyline-glow 3s ease-in-out infinite;
            z-index: 5;
        }}

        @keyframes skyline-glow {{
            0%, 100% {{ opacity: 0.5; }}
            50% {{ opacity: 1; }}
        }}

        .skyline-bar {{
            flex-shrink: 0;
            width: 10px;
            min-height: 5px;
            position: relative;
            cursor: pointer;
            transition: all 0.3s ease;
            animation: skyline-rise 1s ease-out forwards;
            transform-origin: bottom center;
            opacity: 0;
            /* 3D building effect */
            transform-style: preserve-3d;
            border-radius: 2px 2px 0 0;
        }}

        /* 3D front face */
        .skyline-bar::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: inherit;
            border-radius: inherit;
            transform: translateZ(4px);
        }}

        /* 3D right side face */
        .skyline-bar .bar-side {{
            position: absolute;
            top: 0;
            right: -4px;
            width: 4px;
            height: 100%;
            background: rgba(0, 0, 0, 0.3);
            transform: rotateY(90deg) translateZ(0px);
            transform-origin: left;
        }}

        /* 3D top face */
        .skyline-bar .bar-top {{
            position: absolute;
            top: -4px;
            left: 0;
            width: 100%;
            height: 4px;
            background: rgba(255, 255, 255, 0.2);
            transform: rotateX(90deg) translateZ(0px);
            transform-origin: bottom;
        }}

        /* Different colors for different metrics */
        .skyline-bar.metric-sessions {{
            background: linear-gradient(180deg, var(--neon-cyan) 0%, #0891b2 100%);
            box-shadow: 0 0 10px rgba(0, 245, 255, 0.3);
        }}

        .skyline-bar.metric-tokens {{
            background: linear-gradient(180deg, var(--neon-purple) 0%, #7c3aed 100%);
            box-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
        }}

        .skyline-bar.metric-cost {{
            background: linear-gradient(180deg, var(--neon-pink) 0%, #db2777 100%);
            box-shadow: 0 0 10px rgba(255, 0, 110, 0.3);
        }}

        .skyline-bar:hover {{
            filter: brightness(1.4);
            box-shadow: 0 0 25px currentColor, 0 0 50px currentColor;
            transform: scaleY(1.05) scaleX(1.3) translateZ(10px);
            z-index: 10;
        }}

        .skyline-bar .bar-label {{
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%) translateZ(5px);
            font-size: 0.65rem;
            color: rgba(255,255,255,0.7);
            white-space: nowrap;
            opacity: 0;
            transition: opacity 0.2s;
            pointer-events: none;
            padding-bottom: 8px;
            text-shadow: 0 0 10px rgba(0,0,0,0.8);
        }}

        .skyline-bar:hover .bar-label {{
            opacity: 1;
        }}

        /* Reflection effect */
        .skyline-reflection {{
            position: absolute;
            bottom: -40px;
            left: 20px;
            right: 20px;
            height: 40px;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            gap: 2px;
            opacity: 0.15;
            transform: scaleY(-1);
            filter: blur(2px);
            mask-image: linear-gradient(to bottom, rgba(0,0,0,0.5) 0%, transparent 100%);
            -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,0.5) 0%, transparent 100%);
        }}

        @keyframes skyline-rise {{
            0% {{ transform: scaleY(0) translateZ(0); opacity: 0; }}
            100% {{ transform: scaleY(1) translateZ(4px); opacity: 1; }}
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

        /* 3D Skyline tooltip */
        .skyline-3d-tooltip {{
            position: fixed;
            background: rgba(10, 10, 15, 0.95);
            border: 1px solid var(--neon-purple);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.85rem;
            z-index: 1000;
            pointer-events: none;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.2s, visibility 0.2s;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 20px rgba(139,92,246,0.3);
        }}

        /* Ring tooltip */
        .ring-tooltip {{
            position: fixed;
            background: rgba(10, 10, 15, 0.95);
            border: 1px solid var(--neon-cyan);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.85rem;
            z-index: 1000;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 20px rgba(0,245,255,0.2);
        }}

        .ring-tooltip.visible {{
            opacity: 1;
        }}

        .ring-tooltip-day {{
            font-family: 'Orbitron', monospace;
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}

        .ring-tooltip-stats {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: rgba(255,255,255,0.8);
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

        /* Global custom tooltip for title attributes */
        .custom-tooltip {{
            position: fixed;
            background: rgba(10, 10, 20, 0.95);
            border: 1px solid var(--neon-cyan);
            border-radius: 8px;
            padding: 0.6rem 0.9rem;
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.95);
            max-width: 300px;
            z-index: 10000;
            pointer-events: none;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.15s ease, visibility 0.15s ease;
            box-shadow: 0 4px 20px rgba(0, 245, 255, 0.2);
            line-height: 1.4;
        }}

        .custom-tooltip.visible {{
            opacity: 1;
            visibility: visible;
        }}

        .custom-tooltip::before {{
            content: '';
            position: absolute;
            top: 100%;
            left: 20px;
            border: 6px solid transparent;
            border-top-color: var(--neon-cyan);
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
            <div class="stat-card" title="Total Claude Code sessions started. Each session is a separate conversation with Claude.">
                <div class="stat-value">{sessions_formatted}</div>
                <div class="stat-label">Sessions</div>
            </div>
            <div class="stat-card" title="Total messages exchanged between you and Claude across all sessions.">
                <div class="stat-value">{messages_formatted}</div>
                <div class="stat-label">Messages</div>
            </div>
            <div class="stat-card" title="Total tokens processed (input + output). Tokens are how AI models measure text - roughly 4 characters or 0.75 words per token.">
                <div class="stat-value">{tokens_formatted}</div>
                <div class="stat-label">Tokens</div>
            </div>
            <div class="stat-card" title="Unique project directories where you used Claude Code.">
                <div class="stat-value">{data.get('unique_projects', 0)}</div>
                <div class="stat-label">Projects</div>
            </div>
            <div class="stat-card" title="Duration of your longest continuous coding session with Claude.">
                <div class="stat-value">{longest_session}</div>
                <div class="stat-label">Longest Session</div>
            </div>
            <div class="stat-card" title="Maximum number of consecutive days you used Claude Code.">
                <div class="stat-value">{longest_streak}</div>
                <div class="stat-label">Day Streak</div>
            </div>
        </section>
        
        <!-- The Money -->
        <section class="chart-section money-section" aria-labelledby="money-title">
            <div class="chart-title" id="money-title"><span aria-hidden="true">💸</span> The Damage</div>
            <div class="money-value" role="text" aria-label="Total cost: {cost_formatted}">{cost_formatted}</div>
            <p class="burrito-equivalent">That's <span>${total_cost:,.2f}</span> worth of burritos (<span>{int(burritos):,}</span> at $12 each).</p>
        </section>
        
        <!-- Verdicts -->
        <section class="verdict-section" aria-label="Your coding verdicts and statistics">
            <div class="verdict-grid" role="list">
                <!-- Yapping Index -->
                <article class="verdict-card pink" role="listitem" aria-labelledby="yapping-title" title="The Yapping Index measures how much you write compared to Claude. Higher ratio = you're writing more than Claude responds.">
                    <div class="verdict-icon" aria-hidden="true">🗣️</div>
                    <div class="verdict-subtitle">The Yapping Index</div>
                    <div class="verdict-title" id="yapping-title">{yapping_title}</div>
                    <div class="verdict-desc">{yapping_desc}</div>
                    <div class="verdict-stat" title="Ratio of your tokens to Claude's tokens. 1.0x = equal, >1 = you write more, <1 = Claude writes more">{data.get('user_to_assistant_token_ratio', 0):.2f}x ratio</div>
                </article>

                <!-- Cache Efficiency -->
                <article class="verdict-card cyan" role="listitem" aria-labelledby="cache-title" title="Context Reuse measures how often Claude reuses cached context from previous turns. Higher % = cheaper API calls because tokens don't need to be re-processed.">
                    <div class="verdict-icon" aria-hidden="true">💾</div>
                    <div class="verdict-subtitle">Context Reuse</div>
                    <div class="verdict-title" id="cache-title">{cache_title}</div>
                    <div class="verdict-desc">{cache_desc}</div>
                    <div class="verdict-stat" title="Percentage of input tokens that were served from cache instead of being fully processed">{data.get('cache_efficiency_ratio', 0)*100:.1f}% cached</div>
                </article>

                <!-- Bio Rhythm -->
                <article class="verdict-card purple" role="listitem" aria-labelledby="bio-title" title="Your coding bio rhythm based on when you're most active with Claude Code.">
                    <div class="verdict-icon" aria-hidden="true">{bio_rhythm_icon}</div>
                    <div class="verdict-subtitle">Bio Rhythm</div>
                    <div class="verdict-title" id="bio-title">{time_title}</div>
                    <div class="verdict-desc">{time_desc}</div>
                </article>
            </div>
        </section>
        
        <!-- Developer Personality & Coding City -->
        <section class="verdict-section">
            <div class="verdict-grid">
                <!-- Developer Personality -->
                <div class="verdict-card pink" style="grid-column: span 1;" title="Your developer personality is determined by your coding patterns, tool preferences, and interaction style with Claude.">
                    <div class="verdict-icon">🎭</div>
                    <div class="verdict-subtitle">Your Developer Personality</div>
                    <div class="verdict-title">{dev_personality}</div>
                    <div class="verdict-desc">{personality_desc}</div>
                </div>

                <!-- Coding City -->
                <div class="verdict-card cyan" style="grid-column: span 1;" title="Your coding city is matched based on your tech stack, coding style, and the vibe of your projects.">
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
        
        <!-- 🌟 MEGA CHART: 3D Token Skyline 🌟 -->
        <section class="chart-section year-in-code" aria-labelledby="skyline-chart-title">
            <div class="chart-title" id="skyline-chart-title"><span aria-hidden="true">🏙️</span> Your 3D Coding Skyline</div>
            <p style="text-align: center; color: rgba(255,255,255,0.5); margin-bottom: 1rem; font-size: 0.9rem;">
                X = Days of Week, Y = Activity, Z = Weeks. Drag to rotate. Scroll to zoom. Click bars for details.
            </p>
            <div class="heatmap-controls" role="group" aria-label="Metric selection">
                <button class="heatmap-btn active" data-metric="sessions" style="border-color: var(--neon-cyan); color: var(--neon-cyan);" aria-pressed="true" title="View by number of Claude Code sessions started each day">📊 Sessions</button>
                <button class="heatmap-btn" data-metric="tokens" style="border-color: var(--neon-purple); color: var(--neon-purple);" aria-pressed="false" title="View by total tokens (input + output) processed each day">🔤 Tokens</button>
                <button class="heatmap-btn" data-metric="cost" style="border-color: var(--neon-pink); color: var(--neon-pink);" aria-pressed="false" title="View by estimated API cost in USD each day">💰 Cost</button>
            </div>
            <div class="skyline-wrapper">
                <div class="skyline-total">
                    <div class="skyline-total-value" id="skylineTotalValue">0</div>
                    <div class="skyline-total-label" id="skylineTotalLabel">Total Sessions</div>
                </div>
                <div id="skyline3D" style="width: 100%; height: 400px; border-radius: 16px; overflow: hidden; background: linear-gradient(180deg, rgba(10,10,15,0.9) 0%, rgba(20,20,35,0.9) 100%);" role="img" aria-label="3D visualization of coding activity over time"></div>
                <div id="skyline3DTooltip" class="skyline-3d-tooltip"></div>
            </div>
            <div class="heatmap-stats" id="heatmapStats">
                <div class="heatmap-stat" title="Total number of unique days you used Claude Code.">
                    <div class="heatmap-stat-value" id="statTotalDays">0</div>
                    <div class="heatmap-stat-label">Active Days</div>
                </div>
                <div class="heatmap-stat" title="The day of the week when you're most active with Claude Code.">
                    <div class="heatmap-stat-value" id="statBestDay">-</div>
                    <div class="heatmap-stat-label">Most Productive Day</div>
                </div>
                <div class="heatmap-stat" title="The month with the highest activity based on the selected metric.">
                    <div class="heatmap-stat-value" id="statBestMonth">-</div>
                    <div class="heatmap-stat-label">Best Month</div>
                </div>
            </div>

            <!-- Activity Ring: Weekly Pattern - Using Chart.js for interactivity -->
            <div class="chart-title" style="margin-top: 3rem;"><span>🎯</span> Weekly Activity Ring</div>
            <div class="chart-container" style="max-width: 400px; margin: 0 auto;">
                <canvas id="weekdayRingChart" role="img" aria-label="Weekly activity distribution showing sessions per day of the week"></canvas>
            </div>
        </section>
        
        <!-- The Graveyard -->
        <section class="chart-section">
            <div class="chart-title"><span>🪦</span> The Graveyard of Good Intentions</div>
            <div class="graveyard">
                <div class="tombstone">
                    <div class="tombstone-tooltip">Sessions that lasted less than 2 minutes.<br>Sometimes you just need to check one thing...</div>
                    <div class="tombstone-value">{rage_quits}</div>
                    <div class="tombstone-label">Rage Quits<br><small>(&lt;2 min sessions)</small></div>
                </div>
                <div class="tombstone">
                    <div class="tombstone-tooltip">Total API errors encountered across all sessions.<br>Network issues, rate limits, and other failures.</div>
                    <div class="tombstone-value">{data.get('total_errors', 0)}</div>
                    <div class="tombstone-label">API<br>Errors</div>
                </div>
                <div class="tombstone">
                    <div class="tombstone-tooltip">Todo items created by subagents that were<br>never associated with a parent session.</div>
                    <div class="tombstone-value">{orphan_todos}</div>
                    <div class="tombstone-label">Orphaned<br>Agent Tasks</div>
                </div>
                <div class="tombstone">
                    <div class="tombstone-tooltip">Times the context window filled up and<br>Claude had to summarize the conversation.</div>
                    <div class="tombstone-value">{context_collapses}</div>
                    <div class="tombstone-label">Context<br>Collapses</div>
                </div>
                <div class="tombstone">
                    <div class="tombstone-tooltip">Percentage of todos that were created<br>but never marked as completed.</div>
                    <div class="tombstone-value">{100-todo_completion:.0f}%</div>
                    <div class="tombstone-label">Todos Never<br>Completed</div>
                </div>
            </div>
        </section>

        <!-- Context Health -->
        <section class="chart-section">
            <div class="chart-title"><span>🧠</span> Context Engineering Report</div>
            <div class="context-health">
                <div class="context-metric" title="Sessions where the context window filled up and Claude had to summarize the conversation to continue.">
                    <div class="context-metric-value">{data.get('sessions_with_compaction', 0)}</div>
                    <div class="context-metric-label">Sessions w/ Compaction</div>
                    <div class="context-metric-detail">{data.get('sessions_with_compaction', 0) / max(data.get('total_sessions', 1), 1) * 100:.1f}% of all sessions</div>
                </div>
                <div class="context-metric" title="The highest number of times context was compacted in a single session. More compactions = longer/more complex conversations.">
                    <div class="context-metric-value">{data.get('max_compactions_in_session', 0)}</div>
                    <div class="context-metric-label">Max Compactions</div>
                    <div class="context-metric-detail">Most in a single session</div>
                </div>
                <div class="context-metric" title="Sessions with 3+ compactions indicate marathon coding sessions with extensive back-and-forth. These are your deep work sessions.">
                    <div class="context-metric-value">{data.get('multi_compaction_sessions', 0)}</div>
                    <div class="context-metric-label">Deep Dive Sessions</div>
                    <div class="context-metric-detail">3+ compactions (marathon coding)</div>
                </div>
                <div class="context-metric" title="Ratio of input tokens to output tokens. High (>5x) = context-heavy reading/exploration. Low (<2x) = output-heavy code generation.">
                    <div class="context-metric-value">{data.get('input_output_ratio', 0):.1f}x</div>
                    <div class="context-metric-label">Input/Output Ratio</div>
                    <div class="context-metric-detail">{'Context-heavy' if data.get('input_output_ratio', 0) > 5 else 'Balanced' if data.get('input_output_ratio', 0) > 2 else 'Output-heavy'} usage</div>
                </div>
                <div class="context-metric" title="Average tokens per message. <500 = concise messages, 500-2000 = normal, >2000 = verbose (large code blocks or detailed explanations).">
                    <div class="context-metric-value">{format_number(data.get('avg_tokens_per_message', 0))}</div>
                    <div class="context-metric-label">Avg Tokens/Message</div>
                    <div class="context-metric-detail">{'Verbose' if data.get('avg_tokens_per_message', 0) > 2000 else 'Concise' if data.get('avg_tokens_per_message', 0) < 500 else 'Normal'} messages</div>
                </div>
                <div class="context-metric" title="Average tokens consumed before the context window fills and needs to be compacted. Higher = better context management.">
                    <div class="context-metric-value">{int(data.get('tokens_per_compaction', 0) / 1000)}K</div>
                    <div class="context-metric-label">Tokens per Compaction</div>
                    <div class="context-metric-detail">Avg tokens before context reset</div>
                </div>
            </div>
        </section>

        <!-- Tool Belt -->
        <section class="chart-section">
            <div class="chart-title"><span>🛠️</span> Your Tool Belt</div>
            <p style="text-align: center; color: rgba(255,255,255,0.5); margin-bottom: 1rem; font-size: 0.9rem;">
                Claude Code tools you use most: Read, Edit, Bash, Grep, and any custom MCP tools (mcp__*).
            </p>
            <div class="chart-container">
                <canvas id="toolChart"></canvas>
            </div>
        </section>
        
        <!-- Streaks -->
        <section class="chart-section">
            <div class="chart-title"><span>🔥</span> Streaks</div>
            <div class="streak-display">
                <div class="streak-item" title="Maximum consecutive days you used Claude Code without missing a day.">
                    <div class="streak-value">{longest_streak}</div>
                    <div class="streak-label">Longest Streak (Days)</div>
                </div>
                <div class="streak-item" title="How many consecutive days you've been using Claude Code up to today (or your last active day).">
                    <div class="streak-value">{current_streak}</div>
                    <div class="streak-label">Current Streak</div>
                </div>
                <div class="streak-item" title="Number of sessions that lasted more than 2 hours. These are your deep work sessions where you really dug in.">
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

        // Weekday Activity Ring Chart (using Chart.js for full interactivity)
        new Chart(document.getElementById('weekdayRingChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                datasets: [{{
                    data: {json.dumps(weekday_values)},
                    backgroundColor: [neonCyan, '#00d4e6', neonPurple, '#a78bfa', neonPink, '#ff4d8d', neonOrange],
                    borderWidth: 2,
                    borderColor: 'rgba(10, 10, 15, 0.8)',
                    hoverBorderWidth: 3,
                    hoverBorderColor: '#fff',
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                cutout: '60%',
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            color: 'rgba(255,255,255,0.8)',
                            font: {{ family: "'JetBrains Mono', monospace", size: 11 }},
                            padding: 15,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }}
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(10, 10, 15, 0.95)',
                        titleColor: neonCyan,
                        bodyColor: 'rgba(255,255,255,0.9)',
                        borderColor: neonPurple,
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 12,
                        titleFont: {{ family: "'Orbitron', monospace", weight: 'bold', size: 14 }},
                        bodyFont: {{ family: "'JetBrains Mono', monospace", size: 12 }},
                        callbacks: {{
                            label: function(context) {{
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return [
                                    `Sessions: ${{context.parsed}}`,
                                    `Share: ${{percentage}}% of week`
                                ];
                            }}
                        }}
                    }}
                }},
                animation: {{
                    animateRotate: true,
                    animateScale: true,
                    duration: 1500,
                    easing: 'easeOutQuart'
                }}
            }}
        }});

        // 🌟 TRUE 3D TOKEN SKYLINE with Three.js 🌟
        (function() {{
            const sessionsData = {json.dumps(sessions_by_date)};
            const tokensData = {json.dumps(data.get('tokens_by_date', {}))};
            const costData = {json.dumps(data.get('cost_by_date', {}))};

            const container = document.getElementById('skyline3D');
            const tooltip = document.getElementById('skyline3DTooltip');
            const statTotalDays = document.getElementById('statTotalDays');
            const statBestDay = document.getElementById('statBestDay');
            const statBestMonth = document.getElementById('statBestMonth');
            const skylineTotalValue = document.getElementById('skylineTotalValue');
            const skylineTotalLabel = document.getElementById('skylineTotalLabel');

            if (!container || typeof THREE === 'undefined') {{
                console.warn('Three.js or container not available');
                return;
            }}

            let currentMetric = 'sessions';
            let scene, camera, renderer, controls;
            let bars = [];
            let selectedBar = null;

            // Collect all dates with data and sort them
            const allDates = [...new Set([
                ...Object.keys(sessionsData),
                ...Object.keys(tokensData),
                ...Object.keys(costData)
            ])].filter(d => sessionsData[d] > 0 || tokensData[d] > 0 || costData[d] > 0).sort();

            // Organize data by week (Z-axis) and day of week (X-axis)
            function organizeByWeekAndDay() {{
                const weekData = [];
                let currentWeek = [];
                let lastWeekNum = -1;

                allDates.forEach(dateStr => {{
                    const date = new Date(dateStr);
                    const dayOfWeek = date.getDay(); // 0=Sun, 6=Sat
                    const weekNum = getWeekNumber(date);

                    if (lastWeekNum !== -1 && weekNum !== lastWeekNum) {{
                        weekData.push(currentWeek);
                        currentWeek = [];
                    }}

                    currentWeek.push({{ dateStr, dayOfWeek }});
                    lastWeekNum = weekNum;
                }});

                if (currentWeek.length > 0) weekData.push(currentWeek);
                return weekData;
            }}

            function getWeekNumber(date) {{
                const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
                const dayNum = d.getUTCDay() || 7;
                d.setUTCDate(d.getUTCDate() + 4 - dayNum);
                const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
                return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
            }}

            function getData(metric) {{
                return metric === 'sessions' ? sessionsData :
                       metric === 'tokens' ? tokensData : costData;
            }}

            function getColor(metric) {{
                const colors = {{
                    sessions: {{ main: 0x00f5ff, secondary: 0x0891b2 }},  // Cyan
                    tokens: {{ main: 0x8b5cf6, secondary: 0x7c3aed }},    // Purple
                    cost: {{ main: 0xff006e, secondary: 0xdb2777 }}        // Pink
                }};
                return colors[metric] || colors.sessions;
            }}

            function formatValue(value, metric) {{
                if (metric === 'tokens') {{
                    if (value >= 1000000) return (value / 1000000).toFixed(1) + 'M';
                    if (value >= 1000) return (value / 1000).toFixed(1) + 'K';
                    return value.toString();
                }}
                if (metric === 'cost') return '$' + parseFloat(value).toFixed(2);
                return value.toString();
            }}

            // Initialize Three.js scene
            function initScene() {{
                const width = container.clientWidth;
                const height = container.clientHeight;

                // Scene
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x0a0a0f);

                // Camera
                camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
                camera.position.set(15, 12, 20);
                camera.lookAt(0, 0, 0);

                // Renderer
                renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                // OrbitControls
                if (THREE.OrbitControls) {{
                    controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.enableDamping = true;
                    controls.dampingFactor = 0.05;
                    controls.minDistance = 10;
                    controls.maxDistance = 50;
                    controls.maxPolarAngle = Math.PI / 2;
                }}

                // Lighting
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
                scene.add(ambientLight);

                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                directionalLight.position.set(10, 20, 10);
                scene.add(directionalLight);

                const pointLight = new THREE.PointLight(0x8b5cf6, 0.5, 50);
                pointLight.position.set(-10, 10, -10);
                scene.add(pointLight);

                // Add grid helper (ground plane)
                const gridHelper = new THREE.GridHelper(30, 30, 0x8b5cf6, 0x1a1a2e);
                gridHelper.position.y = -0.1;
                scene.add(gridHelper);

                // Add city skyline silhouette in background
                addCitySkyline();

                // Add axis labels
                addAxisLabels();

                // Raycaster for click/hover detection
                const raycaster = new THREE.Raycaster();
                const mouse = new THREE.Vector2();

                container.addEventListener('mousemove', (e) => {{
                    const rect = container.getBoundingClientRect();
                    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

                    raycaster.setFromCamera(mouse, camera);
                    const intersects = raycaster.intersectObjects(bars.map(b => b.mesh));

                    if (intersects.length > 0) {{
                        const barData = bars.find(b => b.mesh === intersects[0].object);
                        if (barData) {{
                            showTooltip(e, barData);
                            container.style.cursor = 'pointer';
                        }}
                    }} else {{
                        hideTooltip();
                        container.style.cursor = 'grab';
                    }}
                }});

                container.addEventListener('click', (e) => {{
                    const rect = container.getBoundingClientRect();
                    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
                    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

                    raycaster.setFromCamera(mouse, camera);
                    const intersects = raycaster.intersectObjects(bars.map(b => b.mesh));

                    if (intersects.length > 0) {{
                        const barData = bars.find(b => b.mesh === intersects[0].object);
                        if (barData) {{
                            highlightBar(barData);
                        }}
                    }}
                }});

                // Handle resize
                window.addEventListener('resize', () => {{
                    const w = container.clientWidth;
                    const h = container.clientHeight;
                    camera.aspect = w / h;
                    camera.updateProjectionMatrix();
                    renderer.setSize(w, h);
                }});
            }}

            // City skyline building definitions - iconic silhouettes
            const citySkylines = {{
                'Tokyo': [
                    {{ height: 12, width: 1.5, depth: 1.5, x: -12, name: 'Tokyo Tower' }},
                    {{ height: 15, width: 2, depth: 2, x: -8, name: 'Tokyo Skytree' }},
                    {{ height: 8, width: 3, depth: 2, x: -4, name: 'Mode Gakuen Tower' }},
                    {{ height: 10, width: 2.5, depth: 2, x: 0, name: 'Shinjuku Tower' }},
                    {{ height: 7, width: 2, depth: 2, x: 4, name: 'Roppongi Hills' }},
                    {{ height: 9, width: 2, depth: 1.5, x: 8, name: 'Shibuya Scramble' }},
                ],
                'San Francisco': [
                    {{ height: 14, width: 2, depth: 2, x: -10, name: 'Transamerica Pyramid', pyramid: true }},
                    {{ height: 11, width: 2.5, depth: 2, x: -5, name: 'Salesforce Tower' }},
                    {{ height: 8, width: 2, depth: 2, x: 0, name: '555 California' }},
                    {{ height: 6, width: 8, depth: 1, x: 6, name: 'Golden Gate Tower', bridge: true }},
                    {{ height: 7, width: 2, depth: 2, x: 12, name: 'Coit Tower' }},
                ],
                'New York': [
                    {{ height: 16, width: 2, depth: 2, x: -10, name: 'Empire State' }},
                    {{ height: 14, width: 3, depth: 2, x: -5, name: 'One WTC' }},
                    {{ height: 12, width: 2.5, depth: 2, x: 0, name: 'Chrysler Building', spire: true }},
                    {{ height: 10, width: 2, depth: 2, x: 5, name: '432 Park' }},
                    {{ height: 8, width: 3, depth: 2, x: 10, name: 'Flatiron' }},
                ],
                'Berlin': [
                    {{ height: 12, width: 1, depth: 1, x: -8, name: 'TV Tower', antenna: true }},
                    {{ height: 6, width: 6, depth: 2, x: -2, name: 'Brandenburg Gate' }},
                    {{ height: 8, width: 3, depth: 2, x: 4, name: 'Reichstag', dome: true }},
                    {{ height: 7, width: 2, depth: 2, x: 10, name: 'Potsdamer Platz' }},
                ],
                'London': [
                    {{ height: 13, width: 2, depth: 2, x: -10, name: 'The Shard', pyramid: true }},
                    {{ height: 7, width: 3, depth: 3, x: -4, name: 'Gherkin', oval: true }},
                    {{ height: 6, width: 4, depth: 2, x: 2, name: 'Tower Bridge' }},
                    {{ height: 10, width: 2, depth: 2, x: 8, name: 'Big Ben', clock: true }},
                ],
                'Stockholm': [
                    {{ height: 8, width: 2, depth: 2, x: -8, name: 'City Hall', spire: true }},
                    {{ height: 6, width: 3, depth: 2, x: -2, name: 'Royal Palace' }},
                    {{ height: 7, width: 2, depth: 2, x: 4, name: 'Ericsson Globe', dome: true }},
                    {{ height: 5, width: 2, depth: 2, x: 10, name: 'Gamla Stan' }},
                ],
                'Seoul': [
                    {{ height: 14, width: 2, depth: 2, x: -10, name: 'Lotte World Tower' }},
                    {{ height: 10, width: 1.5, depth: 1.5, x: -4, name: 'N Seoul Tower', antenna: true }},
                    {{ height: 8, width: 3, depth: 2, x: 2, name: '63 Building' }},
                    {{ height: 9, width: 2, depth: 2, x: 8, name: 'IFC Seoul' }},
                ],
                'Singapore': [
                    {{ height: 11, width: 4, depth: 2, x: -8, name: 'Marina Bay Sands', mbs: true }},
                    {{ height: 8, width: 2, depth: 2, x: -2, name: 'UOB Plaza' }},
                    {{ height: 10, width: 2, depth: 2, x: 4, name: 'One Raffles' }},
                    {{ height: 6, width: 2, depth: 2, x: 10, name: 'Esplanade', dome: true }},
                ],
                'Austin': [
                    {{ height: 9, width: 2, depth: 2, x: -8, name: 'Frost Bank Tower' }},
                    {{ height: 7, width: 3, depth: 2, x: -2, name: 'State Capitol', dome: true }},
                    {{ height: 10, width: 2, depth: 2, x: 4, name: 'The Independent' }},
                    {{ height: 6, width: 2, depth: 2, x: 10, name: 'Zilker Tower' }},
                ],
                'Tel Aviv': [
                    {{ height: 10, width: 2, depth: 2, x: -8, name: 'Azrieli Center' }},
                    {{ height: 8, width: 2, depth: 2, x: -2, name: 'Shalom Tower' }},
                    {{ height: 9, width: 2, depth: 2, x: 4, name: 'Sarona Tower' }},
                    {{ height: 7, width: 3, depth: 2, x: 10, name: 'Rothschild' }},
                ],
                'Zurich': [
                    {{ height: 6, width: 2, depth: 2, x: -8, name: 'Grossmunster', spire: true }},
                    {{ height: 8, width: 3, depth: 2, x: -2, name: 'Prime Tower' }},
                    {{ height: 5, width: 2, depth: 2, x: 4, name: 'Fraumunster', spire: true }},
                    {{ height: 7, width: 2, depth: 2, x: 10, name: 'Swiss Re' }},
                ],
            }};

            function addCitySkyline() {{
                // Extract city name from the coding city string
                const codingCity = '{coding_city}';
                let cityKey = 'London'; // default

                for (const city of Object.keys(citySkylines)) {{
                    if (codingCity.includes(city)) {{
                        cityKey = city;
                        break;
                    }}
                }}

                const buildings = citySkylines[cityKey] || citySkylines['London'];
                const buildingMaterial = new THREE.MeshStandardMaterial({{
                    color: 0x1a1a2e,
                    emissive: 0x8b5cf6,
                    emissiveIntensity: 0.1,
                    transparent: true,
                    opacity: 0.6,
                }});

                buildings.forEach(b => {{
                    // Main building body
                    const geometry = new THREE.BoxGeometry(b.width, b.height, b.depth);
                    const mesh = new THREE.Mesh(geometry, buildingMaterial);
                    mesh.position.set(b.x, b.height / 2, -18); // Behind the data
                    scene.add(mesh);

                    // Add special features
                    if (b.spire || b.antenna) {{
                        const spireGeo = new THREE.CylinderGeometry(0.1, 0.2, b.height * 0.3, 8);
                        const spire = new THREE.Mesh(spireGeo, buildingMaterial);
                        spire.position.set(b.x, b.height + b.height * 0.15, -18);
                        scene.add(spire);
                    }}
                    if (b.dome) {{
                        const domeGeo = new THREE.SphereGeometry(b.width * 0.4, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2);
                        const dome = new THREE.Mesh(domeGeo, buildingMaterial);
                        dome.position.set(b.x, b.height, -18);
                        scene.add(dome);
                    }}
                    if (b.pyramid) {{
                        const pyramidGeo = new THREE.ConeGeometry(b.width * 0.7, b.height * 0.3, 4);
                        const pyramid = new THREE.Mesh(pyramidGeo, buildingMaterial);
                        pyramid.position.set(b.x, b.height + b.height * 0.15, -18);
                        scene.add(pyramid);
                    }}
                }});

                // Add city name label
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = 256;
                canvas.height = 64;
                ctx.fillStyle = 'rgba(139, 92, 246, 0.8)';
                ctx.font = 'bold 24px Orbitron';
                ctx.textAlign = 'center';
                ctx.fillText(cityKey.toUpperCase(), 128, 40);

                const texture = new THREE.CanvasTexture(canvas);
                const labelMaterial = new THREE.SpriteMaterial({{ map: texture, transparent: true }});
                const label = new THREE.Sprite(labelMaterial);
                label.scale.set(8, 2, 1);
                label.position.set(0, 18, -18);
                scene.add(label);
            }}

            function addAxisLabels() {{
                // Day labels on X axis
                const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
                days.forEach((day, i) => {{
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = 64;
                    canvas.height = 32;
                    ctx.fillStyle = 'rgba(255,255,255,0.7)';
                    ctx.font = 'bold 16px Orbitron';
                    ctx.textAlign = 'center';
                    ctx.fillText(day, 32, 20);

                    const texture = new THREE.CanvasTexture(canvas);
                    const material = new THREE.SpriteMaterial({{ map: texture, transparent: true }});
                    const sprite = new THREE.Sprite(material);
                    sprite.scale.set(2, 1, 1);
                    sprite.position.set((i - 3) * 1.5, -0.5, -8);
                    scene.add(sprite);
                }});
            }}

            function showTooltip(e, barData) {{
                const date = new Date(barData.dateStr);
                const formattedDate = date.toLocaleDateString('en-US', {{
                    weekday: 'short', month: 'short', day: 'numeric', year: 'numeric'
                }});

                tooltip.innerHTML = `
                    <div style="font-family: Orbitron; color: #00f5ff; font-size: 0.9rem; margin-bottom: 0.5rem;">${{formattedDate}}</div>
                    <div style="display: grid; grid-template-columns: auto auto; gap: 0.25rem 0.75rem;">
                        <span style="color: rgba(255,255,255,0.6);">Sessions:</span>
                        <span style="color: #00f5ff; font-family: 'JetBrains Mono';">${{sessionsData[barData.dateStr] || 0}}</span>
                        <span style="color: rgba(255,255,255,0.6);">Tokens:</span>
                        <span style="color: #8b5cf6; font-family: 'JetBrains Mono';">${{formatValue(tokensData[barData.dateStr] || 0, 'tokens')}}</span>
                        <span style="color: rgba(255,255,255,0.6);">Cost:</span>
                        <span style="color: #ff006e; font-family: 'JetBrains Mono';">${{formatValue(costData[barData.dateStr] || 0, 'cost')}}</span>
                    </div>
                `;

                tooltip.style.left = (e.clientX + 15) + 'px';
                tooltip.style.top = (e.clientY - 10) + 'px';
                tooltip.style.opacity = '1';
                tooltip.style.visibility = 'visible';
            }}

            function hideTooltip() {{
                tooltip.style.opacity = '0';
                tooltip.style.visibility = 'hidden';
            }}

            function highlightBar(barData) {{
                // Reset previous selection
                if (selectedBar) {{
                    selectedBar.mesh.material.emissiveIntensity = 0.3;
                }}
                selectedBar = barData;
                barData.mesh.material.emissiveIntensity = 1.0;
            }}

            function buildSkyline(metric) {{
                // Clear existing bars
                bars.forEach(b => scene.remove(b.mesh));
                bars = [];

                const data = getData(metric);
                const weekData = organizeByWeekAndDay();
                const allValues = allDates.map(d => data[d] || 0);
                const maxValue = Math.max(...allValues, 1);
                const total = allValues.reduce((a, b) => a + b, 0);

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

                const colors = getColor(metric);
                const barSpacing = 1.5;
                const barSize = 1.0;

                // Create bars organized by week (Z) and day (X)
                weekData.forEach((week, weekIndex) => {{
                    week.forEach((item) => {{
                        const value = data[item.dateStr] || 0;
                        if (value === 0) return;

                        const height = Math.max(0.2, (value / maxValue) * 8);
                        const x = (item.dayOfWeek - 3) * barSpacing; // Center around 0
                        const z = (weekIndex - weekData.length / 2) * barSpacing;

                        // Create bar geometry
                        const geometry = new THREE.BoxGeometry(barSize, height, barSize);
                        const material = new THREE.MeshStandardMaterial({{
                            color: colors.main,
                            emissive: colors.main,
                            emissiveIntensity: 0.3,
                            metalness: 0.3,
                            roughness: 0.5
                        }});

                        const mesh = new THREE.Mesh(geometry, material);
                        mesh.position.set(x, height / 2, z);

                        scene.add(mesh);
                        bars.push({{ mesh, dateStr: item.dateStr, value, dayOfWeek: item.dayOfWeek, week: weekIndex }});
                    }});
                }});

                // Update stats
                updateStats(metric);

                // Animate camera to good viewing position
                if (controls) {{
                    controls.reset();
                }}
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

            // Animation loop
            function animate() {{
                requestAnimationFrame(animate);
                if (controls) controls.update();
                renderer.render(scene, camera);
            }}

            // Button handlers
            document.querySelectorAll('.heatmap-btn').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    document.querySelectorAll('.heatmap-btn').forEach(b => {{
                        b.classList.remove('active');
                        b.setAttribute('aria-pressed', 'false');
                    }});
                    btn.classList.add('active');
                    btn.setAttribute('aria-pressed', 'true');
                    currentMetric = btn.dataset.metric;
                    buildSkyline(currentMetric);
                }});
            }});

            // Initialize and start
            setTimeout(() => {{
                initScene();
                buildSkyline('sessions');
                animate();
            }}, 2600);
        }})();

        // Custom tooltip for all title attributes
        (function() {{
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            document.body.appendChild(tooltip);

            let currentTarget = null;
            let hideTimeout = null;

            document.addEventListener('mouseover', function(e) {{
                const target = e.target.closest('[title]');
                if (target && target.getAttribute('title')) {{
                    clearTimeout(hideTimeout);
                    const titleText = target.getAttribute('title');
                    // Store and remove title to prevent native tooltip
                    target.setAttribute('data-tooltip', titleText);
                    target.removeAttribute('title');

                    tooltip.textContent = titleText;
                    tooltip.classList.add('visible');

                    const rect = target.getBoundingClientRect();
                    let left = rect.left;
                    let top = rect.top - tooltip.offsetHeight - 10;

                    // Keep tooltip in viewport
                    if (top < 10) top = rect.bottom + 10;
                    if (left + tooltip.offsetWidth > window.innerWidth - 10) {{
                        left = window.innerWidth - tooltip.offsetWidth - 10;
                    }}
                    if (left < 10) left = 10;

                    tooltip.style.left = left + 'px';
                    tooltip.style.top = top + 'px';
                    currentTarget = target;
                }}
            }});

            document.addEventListener('mouseout', function(e) {{
                const target = e.target.closest('[data-tooltip]');
                if (target) {{
                    // Restore title attribute
                    const titleText = target.getAttribute('data-tooltip');
                    target.setAttribute('title', titleText);
                    target.removeAttribute('data-tooltip');

                    hideTimeout = setTimeout(() => {{
                        tooltip.classList.remove('visible');
                        currentTarget = null;
                    }}, 100);
                }}
            }});
        }})();
    </script>
</body>
</html>'''
    
    return html_content


def generate_model_tags(model_items: list) -> str:
    """Generate HTML for model usage tags."""
    if not model_items:
        return '<div class="tool-item"><span class="tool-name">No models tracked</span></div>'

    # Model descriptions for tooltips
    model_tooltips = {
        'opus': 'Claude Opus - Most capable model for complex analysis and creative tasks',
        'sonnet': 'Claude Sonnet - Balanced model for everyday coding tasks',
        'haiku': 'Claude Haiku - Fastest model for quick edits and simple tasks',
        '3-5': 'Claude 3.5 - Previous generation model',
        '4': 'Claude 4 - Latest generation model',
    }

    tags = []
    for model, count in model_items:
        # Clean up model name for display
        display_name = model.replace('claude-', '').replace('-20250', ' (')
        if '(' in display_name:
            display_name += ')'

        # Generate tooltip based on model name
        tooltip = f"Used {count} times"
        for key, desc in model_tooltips.items():
            if key in model.lower():
                tooltip = f"{desc}. Used {count} times."
                break

        tags.append(f'<div class="tool-item" title="{html.escape(tooltip)}"><span class="tool-name">{html.escape(display_name)}</span><span class="tool-count">{count}</span></div>')

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

        # Deduplicate groups by normalizing keys to lowercase
        # Also dedupe across group types (e.g., cluster:cloudflare vs framework:cloudflare)
        normalized_groups = {}
        seen_names = {}  # Track which group names we've seen (regardless of type)

        for key, proj_names in smart_groups.items():
            norm_key = key.lower()
            # Extract just the name part (after the colon)
            if ':' in norm_key:
                group_type, group_name = norm_key.split(':', 1)
            else:
                group_type, group_name = '', norm_key

            # If we've seen this name before, merge into the existing group
            if group_name in seen_names:
                existing_key = seen_names[group_name]
                normalized_groups[existing_key] = list(set(normalized_groups[existing_key] + proj_names))
            elif norm_key in normalized_groups:
                # Same full key, merge
                normalized_groups[norm_key] = list(set(normalized_groups[norm_key] + proj_names))
            else:
                normalized_groups[norm_key] = proj_names
                seen_names[group_name] = norm_key

        sorted_groups = sorted(
            normalized_groups.items(),
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
    for i, proj in enumerate(projects[:20]):  # Show top 20
        # Use display_name if available, otherwise name
        name = html.escape(proj.get('display_name', proj.get('name', 'Unknown')))
        sessions = proj.get('sessions', 0)
        messages = proj.get('messages', 0)
        tokens = format_number(proj.get('tokens', 0))
        cost = format_cost(proj.get('cost', 0))

        # Get tech stack info
        frameworks = proj.get('frameworks', [])
        components = proj.get('components', [])
        category = proj.get('category', '')
        summary = proj.get('summary', '')

        # Build tech stack display (show top 5 frameworks)
        tech_tags = []
        for fw in frameworks[:5]:
            tech_tags.append(f'<span class="project-tech-tag">{html.escape(fw)}</span>')
        tech_html = f'<div class="project-tech-stack">{" ".join(tech_tags)}</div>' if tech_tags else ''

        # Component badges (show up to 3)
        component_icons = {
            'chrome-extension': '🧩', 'vscode-extension': '💻', 'web-frontend': '🌐',
            'mobile-app': '📱', 'desktop-app': '🖥️', 'api-server': '⚙️',
            'graphql-api': '◈', 'websocket-server': '🔌', 'ml-pipeline': '🧠',
            'data-ingestion': '📥', 'knowledge-graph': '🕸️', 'kubernetes': '☸️',
            'docker-compose': '🐳', 'ci-cd-pipeline': '🔄', 'cli-tool': '⌨️',
            'sdk-library': '📚', 'mcp-server': '🔗', 'agent-system': '🤖',
        }
        component_tags = []
        for comp in components[:3]:
            icon = component_icons.get(comp, '📦')
            component_tags.append(f'<span class="project-component-tag" title="{html.escape(comp)}">{icon}</span>')
        component_html = f'<div class="project-components">{" ".join(component_tags)}</div>' if component_tags else ''

        # Category badge
        category_html = f'<span class="project-category">{html.escape(category)}</span>' if category else ''

        # Summary line
        summary_html = f'<div class="project-summary">{html.escape(summary)}</div>' if summary else ''

        # Rank badge
        if i == 0:
            badge = '🥇'
        elif i == 1:
            badge = '🥈'
        elif i == 2:
            badge = '🥉'
        else:
            badge = f'#{i+1}'

        # Git metrics
        has_git = proj.get('has_git_data', False)
        git_only = proj.get('git_only', False)
        git_commits = proj.get('git_commits', 0)
        git_lines = proj.get('git_net_lines', 0)
        git_lang = proj.get('git_primary_language', '')

        # Source indicator
        if has_git and sessions > 0:
            source_badge = '<span class="source-badge source-both" title="Claude + Git">🔗</span>'
        elif git_only:
            source_badge = '<span class="source-badge source-git" title="Git only">📂</span>'
        else:
            source_badge = '<span class="source-badge source-claude" title="Claude only">💬</span>'

        # Git stats line
        if has_git and git_commits > 0:
            git_stats_html = f'''
                <div class="project-git-stats">
                    <span title="Git commits">📝 {git_commits} commits</span>
                    <span title="Net lines of code">📊 {format_number(git_lines)} lines</span>
                    {f'<span title="Primary language">💻 {html.escape(git_lang)}</span>' if git_lang else ''}
                </div>
            '''
        else:
            git_stats_html = ''

        # Claude stats (only show if has Claude sessions)
        if sessions > 0:
            claude_stats_html = f'''
                <div class="project-stats">
                    <span>{sessions} sessions</span>
                    <span>{messages} msgs</span>
                    <span>{tokens} tokens</span>
                    <span>{cost}</span>
                </div>
            '''
        else:
            claude_stats_html = '<div class="project-stats"><span class="no-claude">No Claude sessions</span></div>'

        cards.append(f'''
            <div class="project-card {'git-only' if git_only else ''}">
                <div class="project-rank">{badge}</div>
                <div class="project-header">
                    <div class="project-name">{source_badge} {name}</div>
                    {category_html}
                    {component_html}
                </div>
                {summary_html}
                {claude_stats_html}
                {git_stats_html}
                {tech_html}
            </div>
        ''')

    return grouped_html + '\n'.join(cards)


def generate_frameworks_html(data: dict) -> str:
    """Generate HTML for detected frameworks/tools section."""
    top_frameworks = data.get('top_frameworks', [])
    top_concepts = data.get('top_coding_concepts', [])

    sections = []

    # Framework icons
    framework_icons = {
        # AI/LLM Frameworks
        'claude-flow': '🌊', 'sparc': '⚡', 'agentic-engineering': '🤖',
        'coscientist': '🔬', 'mcp': '🔌', 'langchain': '🔗', 'crewai': '👥',
        'autogen': '🤖', 'llamaindex': '🦙',
        # Web Frameworks
        'nextjs': '▲', 'react': '⚛️', 'vue': '💚', 'svelte': '🔥',
        'fastapi': '⚡', 'express': '🚂', 'flask': '🧪', 'django': '🎸', 'hono': '🔥',
        # Cloud Providers
        'cloudflare': '☁️', 'vercel': '▲', 'aws': '🟠', 'gcp': '🔵', 'azure': '🔷',
        'bigquery': '📊', 'terraform': '🏗️',
        # Databases & Vector Stores
        'docker': '🐳', 'kubernetes': '☸️', 'postgresql': '🐘',
        'supabase': '⚡', 'mongodb': '🍃', 'redis': '🔴', 'prisma': '◭',
        'elasticsearch': '🔍', 'pinecone': '🌲', 'weaviate': '🕸️',
        'qdrant': '📍', 'chromadb': '🎨', 'neo4j': '🔵',
        # External APIs & Data Sources
        'pubmed': '📚', 'arxiv': '📄', 'semantic-scholar': '🎓',
        'openalex': '📖', 'wikipedia': '📗',
        'twitter-api': '🐦', 'github-api': '🐙', 'notion-api': '📝',
        'slack-api': '💬', 'discord-api': '🎮',
        # AI/ML
        'anthropic': '🤖', 'openai': '🤖', 'huggingface': '🤗',
        'pytorch': '🔥', 'tensorflow': '🧠',
        # Build Tools
        'tailwindcss': '💨', 'typescript': '💙', 'vite': '⚡', 'bun': '🍞',
        'webpack': '📦', 'turborepo': '🚀', 'pnpm': '📦',
        # Testing
        'jest': '🃏', 'vitest': '⚡', 'pytest': '🧪', 'playwright': '🎭', 'cypress': '🌲',
        # Other
        'graphql': '◈', 'websocket': '🔌', 'stripe': '💳',
        'auth0': '🔐', 'clerk': '👤', 'zod': '✅',
    }

    # Framework descriptions for tooltips
    framework_tooltips = {
        # AI/LLM
        'claude-flow': 'Multi-agent orchestration framework', 'sparc': 'Structured Problem Analysis framework',
        'mcp': 'Model Context Protocol for tool integration', 'langchain': 'LLM application framework',
        'crewai': 'Multi-agent collaboration framework', 'autogen': 'Multi-agent conversation framework',
        'llamaindex': 'Data framework for LLM apps', 'langgraph': 'Graph-based agent orchestration',
        # Web
        'nextjs': 'React framework for production', 'react': 'UI component library',
        'vue': 'Progressive JavaScript framework', 'svelte': 'Compiled frontend framework',
        'fastapi': 'High-performance Python web framework', 'express': 'Node.js web framework',
        'flask': 'Lightweight Python web framework', 'django': 'Full-stack Python framework',
        # Cloud
        'aws': 'Amazon Web Services cloud platform', 'gcp': 'Google Cloud Platform',
        'azure': 'Microsoft Azure cloud platform', 'cloudflare': 'Edge computing platform',
        'vercel': 'Frontend deployment platform', 'bigquery': 'Google data warehouse',
        # Databases
        'postgresql': 'Open-source relational database', 'supabase': 'Open-source Firebase alternative',
        'mongodb': 'NoSQL document database', 'redis': 'In-memory data store',
        'pinecone': 'Vector database for AI', 'chromadb': 'Open-source embeddings database',
        'neo4j': 'Graph database', 'elasticsearch': 'Search and analytics engine',
        # Modern AI databases
        'falkordb': 'GraphRAG-optimized graph database', 'surrealdb': 'Multi-model database for AI',
        'duckdb': 'Embedded analytics database', 'lancedb': 'Multimodal vector database',
        'graphiti': 'Temporal knowledge graph framework', 'mem0': 'AI memory layer',
        'kuzu': 'Embedded graph database', 'edgedb': 'Graph-relational database',
        'tidb': 'Distributed SQL with vector search', 'zep': 'LLM memory service',
        # External Data
        'pubmed': 'Biomedical literature database', 'arxiv': 'Physics/CS preprint server',
        'biorxiv': 'Biology preprint server', 'medrxiv': 'Health sciences preprint server',
        # AI/ML
        'anthropic': 'Claude AI API', 'openai': 'GPT API', 'huggingface': 'ML model hub',
        'pytorch': 'Deep learning framework', 'tensorflow': 'ML platform',
        # Tools
        'docker': 'Container platform', 'kubernetes': 'Container orchestration',
        'terraform': 'Infrastructure as code', 'prisma': 'TypeScript ORM',
        'vite': 'Frontend build tool', 'tailwindcss': 'Utility-first CSS framework',
    }

    if top_frameworks:
        items = []
        for framework, count in top_frameworks[:10]:
            icon = framework_icons.get(framework, '📦')
            tooltip = framework_tooltips.get(framework, f'{framework} framework/tool')
            items.append(f'''
                <div class="framework-tag" title="{html.escape(tooltip)}. Detected {count} times in your code.">
                    <span class="framework-icon">{icon}</span>
                    <span class="framework-name">{html.escape(framework)}</span>
                    <span class="framework-count">{count}</span>
                </div>
            ''')
        sections.append(f'''
            <div class="frameworks-subsection">
                <div class="frameworks-title">Frameworks & Tools</div>
                <div class="frameworks-grid">{"".join(items)}</div>
            </div>
        ''')

    # Coding concepts icons
    concept_icons = {
        'testing': '🧪', 'linting': '✨', 'ci-cd': '🔄', 'documentation': '📚',
        'authentication': '🔐', 'authorization': '🛡️', 'encryption': '🔒',
        'caching': '💾', 'optimization': '🚀', 'async-patterns': '⚡',
        'microservices': '🔀', 'serverless': '☁️', 'monorepo': '📦',
        'type-safety': '💙', 'functional': 'λ', 'reactive': '🔄',
        'clean-architecture': '🏗️', 'dependency-injection': '💉',
    }

    # Concept descriptions for tooltips
    concept_tooltips = {
        'testing': 'Unit, integration, and end-to-end testing practices',
        'linting': 'Code style and quality enforcement tools',
        'ci-cd': 'Continuous integration and deployment pipelines',
        'documentation': 'Code documentation and API specs',
        'authentication': 'User identity verification (OAuth, JWT, sessions)',
        'authorization': 'Access control and permissions (RBAC, ACL)',
        'encryption': 'Data protection and security practices',
        'caching': 'Performance optimization via data caching',
        'optimization': 'Code and performance optimization techniques',
        'async-patterns': 'Asynchronous programming patterns',
        'microservices': 'Distributed service architecture',
        'serverless': 'Cloud functions and event-driven compute',
        'monorepo': 'Single repository for multiple projects',
        'type-safety': 'Static type checking and type inference',
        'functional': 'Functional programming patterns',
        'reactive': 'Reactive programming with observables',
        'clean-architecture': 'Hexagonal/onion architecture patterns',
        'dependency-injection': 'Inversion of control patterns',
        'event-driven': 'Event sourcing and message-driven architecture',
        'streaming': 'Data streaming and chunked processing',
    }

    if top_concepts:
        items = []
        for concept, count in top_concepts[:8]:
            icon = concept_icons.get(concept, '💡')
            tooltip = concept_tooltips.get(concept, f'{concept.replace("-", " ").title()} pattern')
            items.append(f'''
                <div class="concept-tag" title="{html.escape(tooltip)}. Found {count} times.">
                    <span class="concept-icon">{icon}</span>
                    <span class="concept-name">{html.escape(concept)}</span>
                    <span class="concept-count">{count}</span>
                </div>
            ''')
        sections.append(f'''
            <div class="frameworks-subsection">
                <div class="concepts-title">Coding Patterns & Practices</div>
                <div class="frameworks-grid">{"".join(items)}</div>
            </div>
        ''')

    if not sections:
        return ''

    return f'''
        <div class="frameworks-section">
            {"".join(sections)}
        </div>
    '''


def generate_command_cards(data: dict) -> str:
    """Generate HTML for commands, agents, and skills used."""

    top_commands = data.get('top_commands', [])
    top_agents = data.get('top_agents', [])
    top_skills = data.get('top_skills', [])
    top_task_agent_types = data.get('top_task_agent_types', [])

    # Command tooltips
    cmd_tooltips = {
        'help': 'Get help with Claude Code commands',
        'clear': 'Clear the conversation history',
        'compact': 'Summarize conversation to save context',
        'init': 'Initialize Claude Code settings in a project',
        'review': 'Review code changes or pull requests',
        'bug': 'Report or debug an issue',
        'config': 'Configure Claude Code settings',
    }

    # Agent type tooltips
    agent_type_tooltips = {
        'Explore': 'Fast codebase exploration agent for searching files and code',
        'Plan': 'Software architect agent for designing implementation plans',
        'general-purpose': 'General-purpose agent for complex multi-step tasks',
        'claude-code-guide': 'Agent that answers questions about Claude Code features',
    }

    sections = []

    # Commands section
    if top_commands:
        cmd_items = ''.join([
            f'<span class="cmd-tag" title="{html.escape(cmd_tooltips.get(cmd, "Custom slash command"))}. Used {count} times.">/{html.escape(cmd)}<span class="cmd-count">{count}</span></span>'
            for cmd, count in top_commands[:6]
        ])
        sections.append(f'''
            <div class="command-card" title="Slash commands let you trigger specific Claude Code actions quickly.">
                <div class="command-card-title">📋 Slash Commands</div>
                <div class="command-tags">{cmd_items}</div>
            </div>
        ''')

    # Agents section
    if top_agents:
        agent_items = ''.join([
            f'<span class="agent-tag" title="Custom agent that you\'ve called {count} times.">@{html.escape(agent)}<span class="cmd-count">{count}</span></span>'
            for agent, count in top_agents[:6]
        ])
        sections.append(f'''
            <div class="command-card" title="Agents are specialized AI assistants you can invoke with @mentions.">
                <div class="command-card-title">🤖 Agents Used</div>
                <div class="command-tags">{agent_items}</div>
            </div>
        ''')

    # Task Agent Types section (Explore, Plan, general-purpose, etc.)
    if top_task_agent_types:
        type_items = ''.join([
            f'<span class="task-type-tag" title="{html.escape(agent_type_tooltips.get(agent_type, "Specialized subagent type"))}. Spawned {count} times.">{html.escape(agent_type)}<span class="cmd-count">{count}</span></span>'
            for agent_type, count in top_task_agent_types[:6]
        ])
        sections.append(f'''
            <div class="command-card" title="Task subagents are spawned by Claude to handle specific types of work autonomously.">
                <div class="command-card-title">🚀 Task Subagents</div>
                <div class="command-tags">{type_items}</div>
            </div>
        ''')

    # Skills section
    if top_skills:
        skill_items = ''.join([
            f'<span class="skill-tag" title="Specialized skill activated {count} times.">{html.escape(skill)}<span class="cmd-count">{count}</span></span>'
            for skill, count in top_skills[:6]
        ])
        sections.append(f'''
            <div class="command-card" title="Skills are specialized capabilities that extend Claude Code's functionality.">
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
