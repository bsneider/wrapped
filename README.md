# 🎆 Claude Wrapped 2025

> Your year of AI-assisted chaos, quantified. With style.

![Claude Wrapped](https://img.shields.io/badge/Claude-Wrapped-ff006e?style=for-the-badge&logo=anthropic)
![Python](https://img.shields.io/badge/Python-3.9+-00f5ff?style=for-the-badge&logo=python)
![Vibes](https://img.shields.io/badge/Vibes-Immaculate-8b5cf6?style=for-the-badge)

Generate a stunning, synthwave-themed year-in-review report for your Claude CLI usage. Discover your coding patterns, get roasted by your own data, and unlock God Mode with the Konami code.

## ✨ Features

### 📊 Deep Analytics

- **The Yapping Index** - Are you a micromanager or a delegator?
- **Cache Efficiency Score** - How well do you reuse context?
- **Bio-Rhythm Analysis** - When do you REALLY code?
- **The Graveyard** - Rage quits, abandoned projects, orphaned todos
- **Tool Belt** - Your most-used Claude tools
- **Model Promiscuity** - How many models have you flirted with?
- **Streak Tracking** - Longest and current coding streaks
- **The Damage** - Total API cost (in USD and burritos 🌯)

### 🎭 NEW: Developer Personality

Get matched to a personality type based on your coding patterns:
- **The Night Architect** - Building empires while the world sleeps
- **The Terminal Wizard** - Command line is your canvas
- **The Chaos Pilot** - Thriving in entropy
- **The Efficiency Expert** - Every token counts
- **The Deep Diver** - Marathon sessions, massive context
- And more!

### 🏙️ NEW: Coding City Match

Like Spotify's "Sound Town" - get matched to a tech city!
- Tokyo 🇯🇵 - The city that never sleeps
- Stockholm 🇸🇪 - Early riser productivity
- Berlin 🇩🇪 - Techno-fueled marathons
- San Francisco 🇺🇸 - Startup energy
- And more!

### 📁 NEW: Top Projects Explorer

See your most active projects with:
- Session counts
- Message totals
- Token usage
- Ranked by activity

### 🎨 Aesthetic

- Synthwave/Cyberpunk color palette
- Glassmorphism cards
- Animated backgrounds
- Neon gradients everywhere
- Chart.js visualizations
- Responsive design
- **Auto-opens in browser** when finished!

### 🥚 Easter Eggs

- **Konami Code** (↑↑↓↓←→←→BA) - Unlock God Mode with raw stats
- **7x Tap Title** - Mobile-friendly God Mode trigger
- **Karpathy Quotes** - Wisdom from the prophet himself

## 🚀 Quick Start

```bash
# Clone and enter
git clone https://github.com/anthropics/claude-wrapped.git
cd claude-wrapped

# Run it (opens in browser automatically!)
python main.py -o wrapped.html
```

That's it! **Zero dependencies** - pure Python 3.9+.

## 📖 Usage

```bash
# Generate and auto-open in browser
python main.py -o wrapped.html

# Skip auto-open
python main.py -o wrapped.html --no-open

# Get raw JSON data
python main.py --json > data.json

# Custom Claude directory
python main.py -d /path/to/.claude -o report.html

# Quiet mode (no banner)
python main.py -q -o report.html
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `-d, --claude-dir` | Path to .claude directory (default: ~/.claude) |
| `-o, --output` | Output file path (default: stdout) |
| `--json` | Output raw JSON instead of HTML |
| `--no-open` | Don't auto-open browser |
| `-q, --quiet` | Suppress banner and progress messages |

## 💰 Accurate Cost Tracking

Calculates costs from token usage with comprehensive model pricing:

| Model | Input | Output |
|-------|-------|--------|
| Opus 4.5 | $5/1M | $25/1M |
| Opus 4/4.1 | $15/1M | $75/1M |
| Sonnet 4/4.5 | $3/1M | $15/1M |
| Haiku 4.5 | $1/1M | $5/1M |
| Haiku 3.5 | $0.80/1M | $4/1M |
| Haiku 3 | $0.25/1M | $1.25/1M |

Cache pricing automatically included!

## 📁 What Gets Analyzed

```
~/.claude/
├── projects/           # Conversation sessions per project
│   └── **/*.jsonl      # Supports worktrees too!
├── todos/              # Task management files
├── statsig/            # Feature flag exposure
└── settings.json       # Your preferences
```

## 🎮 God Mode

**Desktop:** `↑ ↑ ↓ ↓ ← → ← → B A`  
**Mobile:** Tap the title 7 times quickly

Shows raw stats: exact token counts, precise costs, error counts, and more!

## 📄 License

MIT License - Go wild, just don't blame us for your API bill.

---

<p align="center">
  <b>Beat Google. Ship vibes.</b><br>
  <sub>Made with 💜 and spite</sub>
</p>
