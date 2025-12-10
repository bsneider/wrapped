Claude Wrapped Implementation Plan
Goal Description
Create a "Claude Wrapped" Python script that serves as a year-in-review for the user's local Claude CLI usage. It will parse ~/.claude/history.jsonl, calculate engagement metrics, and generate a high-gloss, "vibecoding" themed HTML report with interactive charts and Andrei Karpathy quotes.

Proposed Changes
Project Structure
pyproject.toml: Define dependencies (pandas, jinja2, plotly/chartjs wrapper if needed, or just standard lib for simplicity + CDN for frontend deps).
src/analyzer.py: Logic to parse partial/messy JSONL from ~/.claude/history.jsonl.
src/generator.py: Logic to inject data into an HTML template.
src/main.py: Orchestrator.
templates/wrapped.html: The vibrant, "viral" HTML template.
src/analyzer.py
Function: load_history()
Reads ~/.claude/history.jsonl.
Handles broken lines gracefully.
Metrics:
"The Cost Inferno": Total costUSD burned. (Visualization: Animated fire pile).
"The A/B Test Subject": Feature flags bucketed into from statsig/.
"The Recursive Despair Index": Depth of TODOs referencing other TODO files.
"Context Collapse": Ratio of cache_read vs cache_creation tokens (Goldfish Memory Score).
"The Rage Quit Index": High input tokens + low output tokens + session termination.
"Model Promiscuity": Unique models used (Opus vs Sonnet vs Haiku).
"Directory Depth Demons": Deepest nested cwd analysis.
"The Tool Roulette": Probability chain of tool usage (Read -> Edit -> Undo loops).
"The Apology Index": Count of synthetic "I apologize" messages.
"The Early Adopter": Frequency of version upgrades.
src/analyzer.py
Updated Logic:
Primary Source: ~/.claude/projects/**/*.jsonl (Deep parsing for cost, tools, cache).
Secondary Source: ~/.claude/statsig/ (Feature flags and stable_id).
Tertiary Source: ~/.claude/todos/*.json (Recursive dependency checking).
Quaternary Source: ~/.claude/debug/*.txt (Chaos/Error mining).
Parsing Detail: Extract costUSD, tool_use.name, cache_creation_input_tokens, isSidechain.
Schema Handling: JSONL parsing with loose schema validation (skip malformed lines).
src/generator.py
Design Philosophy: "Vibecoding" Aesthetic.
Visuals: Neon gradients (Cyberpunk/Synthwave), glassmorphism cards, particle effects.
Tone: Self-deprecating but empowering (e.g., "You burnt 1M tokens... but the vibes were immaculate.").
Easter Eggs: Konami code to unlock "God Mode" stats.
Loading Screen: "Aligning chakras...", "Downloading more RAM...", "Consulting Karpathy...".
templates/wrapped.html
Frontend Tech: Single-file HTML with embedded Chart.js (or ApexCharts for better neon support).
Novel Charts:
"The Conversation Graveyard": 3D scatter plot of abandoned sessions (Size=Tokens, Color=Cost).
"The Cost Inferno": Flame height driven by costUSD. Interactive.
"Bio-Rhythm Circular Heatmap": 24h/Minute-precision activity map.
"Context Collapse Area Chart": Cache efficiency over time (Sandwich chart).
"Dependency Web": Force-directed graph of TODOs and Sidechains.
"The Tool Chain Sankey": Flow of Tool A -> Tool B (e.g., Read -> Edit -> Error).
Verification Plan
Automated Tests
Data Integrity Tests:
Cost Parsing: Verify costUSD aggregation matches sum of sample JSONL.
Recursion Check: Test "Recursive Despair" with a fixture containing circular TODO references.
Statsig Logic: Ensure A/B test buckets are correctly extracted from hashed filenames.
Context Collapse: Validate cache_creation vs read ratio calculation.
Manual Verification
Run Script: Execute python main.py.
"Vibe Check" Protocol:
"The Cost Inferno": Does the fire animation look "expensive"?
"The Conversation Graveyard": Can you navigate the 3D session plot without lag?
"Konami Code": Does ↑↑↓↓←→←→BA unlock the "God Mode" (Raw USD costs)?
Responsiveness: Do the neon charts pinch-to-zoom efficiently?