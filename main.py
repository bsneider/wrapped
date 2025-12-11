#!/usr/bin/env python3
"""
Claude Wrapped - Main Entry Point
Generates a stunning year-in-review HTML report for your Claude CLI usage.

Usage:
    python main.py                    # Analyze ~/.claude, output to stdout
    python main.py --output report.html   # Save to file
    python main.py --claude-dir /path/to/.claude  # Custom path
    python main.py --json             # Output raw JSON instead of HTML
"""

import argparse
import json
import sys
import os
from pathlib import Path

# Import our modules
from analyzer import analyze_claude_directory, to_json_serializable
from generator import generate_html


def print_banner():
    """Print a fancy ASCII banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗         ║
║    ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝         ║
║    ██║     ██║     ███████║██║   ██║██║  ██║█████╗           ║
║    ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝           ║
║    ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗         ║
║     ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝         ║
║                                                               ║
║    ██╗    ██╗██████╗  █████╗ ██████╗ ██████╗ ███████╗██████╗ ║
║    ██║    ██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗║
║    ██║ █╗ ██║██████╔╝███████║██████╔╝██████╔╝█████╗  ██║  ██║║
║    ██║███╗██║██╔══██╗██╔══██║██╔═══╝ ██╔═══╝ ██╔══╝  ██║  ██║║
║    ╚███╔███╔╝██║  ██║██║  ██║██║     ██║     ███████╗██████╔╝║
║     ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚═════╝ ║
║                                                               ║
║                     2 0 2 5   E D I T I O N                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Generate a Claude Wrapped year-in-review report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Generate HTML to stdout
  python main.py -o wrapped.html          # Save to file
  python main.py --json                   # Output raw JSON data
  python main.py -d /custom/path/.claude  # Use custom Claude directory
  
Easter Eggs:
  - Konami code (↑↑↓↓←→←→BA) unlocks God Mode with raw stats
  - Triple-click the title for Shame Mode (coming soon)
        """
    )
    
    parser.add_argument(
        '-d', '--claude-dir',
        type=str,
        default=os.path.expanduser('~/.claude'),
        help='Path to .claude directory (default: ~/.claude)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path (default: stdout)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON data instead of HTML'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress banner and progress messages'
    )
    
    args = parser.parse_args()
    
    # Print banner
    if not args.quiet:
        print_banner()
    
    claude_dir = Path(args.claude_dir)
    
    if not claude_dir.exists():
        print(f"❌ Error: Claude directory not found at {claude_dir}", file=sys.stderr)
        print("   Make sure you have Claude CLI installed and have used it at least once.", file=sys.stderr)
        sys.exit(1)
    
    if not args.quiet:
        print(f"🔍 Analyzing {claude_dir}...", file=sys.stderr)
    
    # Analyze the directory
    data = analyze_claude_directory(claude_dir)
    json_data = to_json_serializable(data)
    
    if not args.quiet:
        print(f"✅ Found {data.total_sessions} sessions, {data.total_messages} messages", file=sys.stderr)
        print(f"💰 Total cost: ${data.total_cost_usd:.2f}", file=sys.stderr)
        print(f"🔥 Longest streak: {data.longest_streak_days} days", file=sys.stderr)
    
    # Generate output
    if args.json:
        output = json.dumps(json_data, indent=2, default=str)
    else:
        if not args.quiet:
            print("🎨 Generating HTML report...", file=sys.stderr)
        output = generate_html(json_data)
    
    # Write output
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        if not args.quiet:
            print(f"✨ Report saved to {output_path}", file=sys.stderr)
            print(f"   Open it in your browser to see your Claude Wrapped!", file=sys.stderr)
    else:
        print(output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
