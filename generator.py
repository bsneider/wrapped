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


def format_tokens(tokens: int) -> str:
    """Format token count with K/M suffix."""
    if tokens < 1000:
        return str(tokens)
    if tokens < 1000000:
        return f"{tokens/1000:.1f}K"
    return f"{tokens/1000000:.2f}M"


def format_cost(cost: float) -> str:
    """Format USD cost."""
    if cost < 0.01:
        return f"${cost:.4f}"
    if cost < 1:
        return f"${cost:.2f}"
    return f"${cost:.2f}"


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
    
    # Find peak hour
    peak_hour = max(hour_dist.items(), key=lambda x: x[1])[0]
    
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
    
    # Format numbers
    tokens_formatted = format_tokens(total_tokens)
    cost_formatted = format_cost(total_cost)
    avg_session = format_duration(data.get('average_session_duration_ms', 0))
    longest_session = format_duration(data.get('longest_session_duration_ms', 0))
    
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
                <div class="stat-value">{total_sessions:,}</div>
                <div class="stat-label">Sessions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_messages:,}</div>
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
            <p class="burrito-equivalent">That's <span>{burritos:.1f} burritos</span> you could have eaten instead.</p>
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
        
        <!-- Karpathy Quote -->
        <section class="quote-section">
            <p class="quote-text">{KARPATHY_QUOTES[hash(str(total_tokens)) % len(KARPATHY_QUOTES)]}</p>
            <p class="quote-author">— Andrei Karpathy (probably)</p>
        </section>
        
        <!-- Footer -->
        <footer class="footer">
            <p>Generated with 💜 by Claude Wrapped</p>
            <p style="margin-top: 0.5rem; font-size: 0.8rem;">
                <em>Tip: Try the Konami code for God Mode</em>
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
        
        // Konami code easter egg
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
