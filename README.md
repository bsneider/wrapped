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
uv run main.py -o wrapped.html
```

That's it! Uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python execution.

## 📖 Usage

```bash
# Generate and auto-open in browser
uv run main.py -o wrapped.html

# Skip auto-open
uv run main.py -o wrapped.html --no-open

# Get raw JSON data
uv run main.py --json > data.json

# Custom Claude directory
uv run main.py -d /path/to/.claude -o report.html

# Quiet mode (no banner)
uv run main.py -q -o report.html
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `-d, --claude-dir` | Path to .claude directory (default: ~/.claude) |
| `-o, --output` | Output file path (default: stdout) |
| `--json` | Output raw JSON instead of HTML |
| `--no-open` | Don't auto-open browser |
| `-q, --quiet` | Suppress banner and progress messages |
| `--no-telemetry` | Opt out of anonymous analytics |
| `--telemetry-preview` | Preview telemetry payload before sending |

## 📡 Telemetry & Research

By default, Claude Wrapped sends **anonymous, aggregated metrics** to help improve the tool and contribute to prompt engineering research. **No prompt content, file paths, or personally identifiable information is ever transmitted.**

### What We Collect

| Data Type | Example | NOT Collected |
|-----------|---------|---------------|
| Aggregate counts | "342 sessions" | Individual session details |
| Score distributions | "Proficiency: 72" | Your actual prompts |
| Usage patterns | "Peak hour: 21" | Specific timestamps |
| Model distribution | "65% Sonnet" | Conversation content |
| Tool usage counts | "Read: 450 uses" | File paths or code |

### Opt-Out Options

```bash
# One-time opt-out
uv run main.py -o wrapped.html --no-telemetry

# See what would be sent
uv run main.py -o wrapped.html --telemetry-preview

# Permanent opt-out (add to config)
echo '{"telemetry": false}' > ~/.claude-wrapped/config.json
```

### Why Telemetry?

- **Percentile rankings**: See how you compare to other users
- **Research**: Contribute to prompt engineering research
- **Benchmarks**: Help establish community baselines
- **Improvements**: Guide future Claude Wrapped features

See [Privacy Policy](#privacy-policy) and [Terms of Service](#terms-of-service) below.

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

## 📜 Terms of Service

**Effective Date**: December 15, 2025

By using Claude Wrapped ("the Software"), you agree to these terms:

### 1. Acceptance of Terms

By downloading, installing, or using Claude Wrapped, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service and our Privacy Policy.

### 2. Description of Service

Claude Wrapped is an open-source tool that analyzes your local Claude CLI usage data to generate personalized usage reports. The Software operates primarily on your local machine and optionally transmits anonymous, aggregated telemetry data.

### 3. Data Collection and Use

**3.1 Local Analysis**: The Software reads data from your `~/.claude` directory to generate reports. This data never leaves your machine unless you opt-in to telemetry.

**3.2 Telemetry (Opt-Out Available)**: By default, the Software sends anonymous, aggregated metrics to our servers for research purposes. You may opt-out at any time using `--no-telemetry` or via configuration file.

**3.3 Research Use**: Aggregated telemetry data may be used for:
- Academic research on prompt engineering effectiveness
- Publishing anonymized benchmark reports
- Improving the Software and related tools
- Training machine learning models on usage patterns (not prompt content)

### 4. User Responsibilities

You agree to:
- Use the Software only with data you have rights to access
- Not attempt to reverse-engineer telemetry anonymization
- Not use the Software to collect data on others without consent
- Comply with all applicable laws and regulations

### 5. Intellectual Property

The Software is provided under the MIT License. Research derived from aggregated telemetry may be published under open licenses.

### 6. Disclaimer of Warranties

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. WE DO NOT WARRANT THAT THE SOFTWARE WILL BE ERROR-FREE OR UNINTERRUPTED.

### 7. Limitation of Liability

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY ARISING FROM THE USE OF THE SOFTWARE, INCLUDING BUT NOT LIMITED TO YOUR API COSTS WITH ANTHROPIC.

### 8. Changes to Terms

We reserve the right to modify these terms. Continued use after changes constitutes acceptance.

---

## 🔒 Privacy Policy

**Effective Date**: December 15, 2025

### Overview

Claude Wrapped is designed with privacy as a core principle. We collect minimal data and provide full transparency about what is transmitted.

### What We Collect

#### Local-Only Data (Never Transmitted)
- Your conversation content and prompts
- File paths and project names
- Specific timestamps
- Code snippets or commit messages
- Personal identifiers (name, email)

#### Telemetry Data (Opt-Out Available)

| Category | Data Points | Purpose |
|----------|-------------|---------|
| **Usage Metrics** | Session count, message count, token totals | Population benchmarks |
| **Proficiency Scores** | Calculated skill scores (0-100) | Percentile rankings |
| **Patterns** | Peak hour (0-23), weekend ratio | Research on usage patterns |
| **Model Distribution** | Percentage per model family | Model preference research |
| **Tool Usage** | Count per tool type | Feature effectiveness |

### Anonymization Measures

1. **User Fingerprint**: A salted SHA-256 hash of machine data that rotates monthly. Cannot be reversed to identify you.

2. **IP Hashing**: Your IP address is hashed before storage and cannot be used to identify your location.

3. **No Correlation**: We cannot link telemetry data to your Anthropic account or any other service.

4. **Data Minimization**: We only collect what's necessary for research purposes.

### Your Rights

- **Access**: Request a copy of data associated with your fingerprint
- **Deletion**: Request deletion of your telemetry data
- **Opt-Out**: Disable telemetry at any time via `--no-telemetry`
- **Preview**: See exactly what would be sent via `--telemetry-preview`

### Data Retention

| Data Type | Retention Period |
|-----------|------------------|
| Aggregated benchmarks | Indefinite |
| User fingerprints | Never stored |

### Data Sharing

We may share:
- **Aggregated statistics** in public research reports
- **Benchmark data** with the research community
- **Anonymized datasets** for academic research

### Children's Privacy

Claude Wrapped is not intended for users under 13. We do not knowingly collect data from children.

### International Users

Telemetry servers are located in the United States. By using the Software with telemetry enabled, you consent to data transfer to the US.

### Changes to Policy

We will notify users of material changes via GitHub release notes. Continued use constitutes acceptance.

---

## 📄 License

MIT License - Go wild, just don't blame us for your API bill.

```
MIT License

Copyright (c) 2025 Claude Wrapped Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  <b>Beat Google. Ship vibes.</b><br>
  <sub>Made with 💜 and spite</sub>
</p>
