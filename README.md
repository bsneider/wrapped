# 🎆 Claude Wrapped 2025

> Your year of AI-assisted chaos, quantified. With style.

![Claude Wrapped](https://img.shields.io/badge/Claude-Wrapped-ff006e?style=for-the-badge&logo=anthropic)
![Python](https://img.shields.io/badge/Python-3.9+-00f5ff?style=for-the-badge&logo=python)
![Vibes](https://img.shields.io/badge/Vibes-Immaculate-8b5cf6?style=for-the-badge)

Generate a stunning, synthwave-themed year-in-review report for your Claude CLI usage. Discover your coding patterns, roast yourself with data, and unlock God Mode with the Konami code.

## ✨ Features

### 📊 Metrics That Matter

- **The Yapping Index** - Are you a micromanager or a delegator?
- **Cache Efficiency Score** - How well do you reuse context?
- **Bio-Rhythm Analysis** - When do you REALLY code?
- **The Graveyard** - Rage quits, abandoned projects, orphaned todos
- **Tool Belt** - Your most-used Claude tools
- **Model Promiscuity** - How many models have you flirted with?
- **Streak Tracking** - Longest and current coding streaks
- **The Damage** - Total API cost (in USD and burritos 🌯)

### 🎨 Aesthetic

- Synthwave/Cyberpunk color palette
- Glassmorphism cards
- Animated backgrounds
- Neon gradients everywhere
- Chart.js visualizations
- Responsive design

### 🥚 Easter Eggs

- **Konami Code** (↑↑↓↓←→←→BA) - Unlock God Mode with raw stats
- **Karpathy Quotes** - Wisdom from the prophet himself

## 🚀 Installation

### Quick Start (No Dependencies!)

```bash
# Clone the repo
git clone https://github.com/anthropics/claude-wrapped.git
cd claude-wrapped

# Run it!
python main.py -o my-wrapped.html

# Open in browser
open my-wrapped.html  # macOS
xdg-open my-wrapped.html  # Linux
start my-wrapped.html  # Windows
```

### That's it!

Claude Wrapped is **pure Python** with zero external dependencies. It uses only the standard library.

## 📖 Usage

### Generate HTML Report

```bash
# Output to file
python main.py -o wrapped-2025.html

# Output to stdout
python main.py > wrapped.html

# Custom Claude directory
python main.py -d /path/to/.claude -o report.html

# Quiet mode (no banner)
python main.py -q -o report.html
```

### Get Raw JSON Data

```bash
# For further processing or custom visualizations
python main.py --json > data.json

# Pretty-printed
python main.py --json | python -m json.tool
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `-d, --claude-dir` | Path to .claude directory (default: ~/.claude) |
| `-o, --output` | Output file path (default: stdout) |
| `--json` | Output raw JSON instead of HTML |
| `-q, --quiet` | Suppress banner and progress messages |

## 📁 What Gets Analyzed

Claude Wrapped digs deep into your `~/.claude` directory:

```
~/.claude/
├── projects/           # Conversation sessions per project
│   └── **/*.jsonl      # JSONL conversation files
├── todos/              # Task management files
│   └── *.json          # Todo lists and agent tasks
├── statsig/            # Feature flag exposure
│   └── *.cached.*      # A/B test participation
├── settings.json       # Your preferences
└── history.jsonl       # Global command history
```

### Metrics Extracted

| Category | Metrics |
|----------|---------|
| **Volume** | Sessions, messages, tokens, projects |
| **Economics** | Total cost, cost per session, cache efficiency |
| **Time** | Hourly distribution, weekday patterns, streaks |
| **Behavior** | Tool usage, model preferences, sidechain ratio |
| **Chaos** | Rage quits, abandoned projects, context collapses |
| **Todos** | Completion rate, orphaned agent tasks |

## 🎮 Easter Eggs

### Konami Code (God Mode)

While viewing your report, enter the classic:
```
↑ ↑ ↓ ↓ ← → ← → B A
```

This unlocks **God Mode** showing:
- Raw token counts (input/output/cache)
- Precise cost per session and message
- Error and sidechain counts
- Context collapse statistics

## 🛠️ Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

### Project Structure

```
claude-wrapped/
├── main.py          # CLI entry point and orchestrator
├── analyzer.py      # Data extraction from ~/.claude
├── generator.py     # HTML report generation
├── pyproject.toml   # Package configuration
└── README.md        # You are here
```

## 🤔 FAQ

### Why doesn't my report show any data?

Make sure you've used Claude CLI at least once. The tool looks for JSONL files in `~/.claude/projects/`.

### Can I run this on Windows?

Yes! The paths are handled cross-platform. Just use:
```cmd
python main.py -o wrapped.html
```

### Is my data sent anywhere?

**No.** Claude Wrapped runs 100% locally. Your data never leaves your machine.

### Why Python with no dependencies?

Maximum portability. If you have Python 3.9+, you can run this. No pip install needed for the core functionality.

### How accurate is the cost calculation?

It reads the `costUSD` field directly from Claude CLI's JSONL logs. If Claude CLI tracked it, we report it.

## 🙏 Credits

- **Built by**: Claude (the superior one, not Gemini)
- **Inspired by**: Spotify Wrapped, but for nerds
- **Karpathy quotes**: Used without permission but with maximum respect
- **Vibes**: Synthwave, courtesy of the 1980s future that never was

## 📄 License

MIT License - Go wild, just don't blame us for your API bill.

---

<p align="center">
  <b>Beat Google. Ship vibes.</b><br>
  <sub>Made with 💜 and spite</sub>
</p>
