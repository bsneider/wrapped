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
"The Yapping Index": Ratio of user tokens to model tokens (Micromanager vs. Delegator) - Derived from projects/ logs.
"Bio-Rhythm of Code": Circular 24h heatmap of activity (finding the "Ballmer Peak").
"Impatience Meter": Average time before Ctrl+C or interrupting the model.
"The Spiral": Network graph of repetitive command sequences (loops of desperation).
"Tech Stack Footprint": Icons of languages/tools detected in shell-snapshots.
"Context Switcher": Number of distinct projects/branches worked on per day.
"Deep Work Score": Longest continuous session duration from projects/ timestamps.
"The Graveyard of Good Intentions": Ratio of pending vs completed tasks in todos/.
"The Pivot": Frequency of changing task descriptions (based on activeForm vs content).
"Ghost in the Shell": TODOs created but never worked on (0 associated commands in history).
"Agentic Awareness": Ratio of sidechain events (from agent-*.jsonl) to main thread events.
"Chaos Monkey Score": Frequency of timeouts/errors in debug/ logs.
"Plugin Power User": Count of custom skills loaded (parsed from debug logs).
src/analyzer.py
Updated Logic:
Primary Source: ~/.claude/projects/**/*.jsonl (recursive glob).
Secondary Source: ~/.claude/history.jsonl (for global commands).
Tertiary Source: ~/.claude/todos/*.json (for intent vs reality analysis).
Quaternary Source: ~/.claude/debug/*.txt (regex parsing for error keywords).
Parsing Detail: Distinguish between isSidechain: true (Agent doing work) and false (User chatting).
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
"Token Inferno": Animated fire scaling with usage intensity.
"The Context Dive": Area chart showing directory depth vs. time.
"Calendar of Chaos": GitHub-style contribution graph but color-coded by "Intensity" (red = errors/debug, green = shipping).
Verification Plan
Automated Tests
Data Integrity Tests:
Verify Context Switcher logic by mocking a sequence of cwd changes.
Test "The Graveyard" calculation with a known todos fixture.
Ensure The Yapping Index handles zero-division (e.g., empty sessions).
Manual Verification
Run Script: Execute python main.py.
"Vibe Check" Protocol:
Visuals: Does the "Token Inferno" fire animation scale up when you select a "heavy" project?
Charts: Does "Bio-Rhythm" correctly identify your late-night coding sessions?
Responsiveness: Does the "Context Dive" chart pinch-to-zoom smoothly?
Easter Eggs: Does typing ↑↑↓↓←→←→BA actually unlock the "God Mode" stats?