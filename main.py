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
    
    parser.add_argument(
        '--no-open',
        action='store_true',
        help='Do not automatically open the report in a browser'
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
        if data.developer_personality:
            print(f"🎭 Personality: {data.developer_personality}", file=sys.stderr)
        if data.coding_city:
            print(f"🏙️ Coding City: {data.coding_city}", file=sys.stderr)

    # Run project analysis for frameworks, components, and summaries
    try:
        from project_analyzer import analyze_all_projects, group_projects_smart
        from collections import defaultdict

        if not args.quiet:
            print("🔬 Analyzing projects for frameworks and technologies...", file=sys.stderr)

        # Get project base paths from common locations
        project_base_paths = [
            str(Path.home() / 'sundai'),
            str(Path.home() / 'projects'),
            str(Path.home() / 'repos'),
            str(Path.home() / 'code'),
        ]

        analyses = analyze_all_projects(
            json_data.get('top_projects', []),
            claude_dir,
            project_base_paths
        )

        # Add framework detection results
        framework_counts = defaultdict(int)
        concept_counts = defaultdict(int)
        for analysis in analyses:
            for fw, count in analysis.keyword_matches.items():
                framework_counts[fw] += count
            for concept, count in analysis.concept_matches.items():
                concept_counts[concept] += count

        json_data['detected_frameworks'] = dict(framework_counts)
        json_data['top_frameworks'] = sorted(framework_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        json_data['top_coding_concepts'] = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:15]

        # Smart project groupings
        smart_groups = group_projects_smart(analyses)
        json_data['smart_project_groups'] = smart_groups

        # Add per-project tech info (frameworks, components, summary)
        project_tech_map = {}
        for analysis in analyses:
            project_tech_map[analysis.name] = {
                'frameworks': list(analysis.keyword_matches.keys()),
                'category': analysis.category,
                'coding_concepts': list(analysis.concept_matches.keys()),
                'components': list(analysis.component_matches.keys()),
                'summary': analysis.summary,
            }

        # Update top_projects with tech info
        for proj in json_data.get('top_projects', []):
            name = proj.get('name', '')
            tech_info = project_tech_map.get(name, {})
            proj['frameworks'] = tech_info.get('frameworks', [])
            proj['category'] = tech_info.get('category', '')
            proj['coding_concepts'] = tech_info.get('coding_concepts', [])
            proj['components'] = tech_info.get('components', [])
            proj['summary'] = tech_info.get('summary', '')

        if not args.quiet:
            print(f"✅ Found {len(framework_counts)} frameworks, {len(smart_groups)} project groups", file=sys.stderr)

    except ImportError:
        if not args.quiet:
            print("⚠️  project_analyzer.py not found, skipping project analysis", file=sys.stderr)
    except Exception as e:
        if not args.quiet:
            print(f"⚠️  Project analysis failed: {e}", file=sys.stderr)
    
    # Generate output
    if args.json:
        output = json.dumps(json_data, indent=2, default=str)
    else:
        if not args.quiet:
            print("🎨 Generating HTML report...", file=sys.stderr)
        output = generate_html(json_data)
    
    # Write output
    if args.output:
        output_path = Path(args.output).resolve()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        if not args.quiet:
            print(f"✨ Report saved to {output_path}", file=sys.stderr)

        # Also copy to opus45.html in the project directory
        if not args.json:
            opus45_path = Path(__file__).parent / 'opus45.html'
            with open(opus45_path, 'w', encoding='utf-8') as f:
                f.write(output)
            if not args.quiet:
                print(f"📋 Also saved to {opus45_path}", file=sys.stderr)

        # Open in browser unless --no-open is specified
        if not args.json and not args.no_open:
            import webbrowser
            file_url = f"file://{output_path}"
            if not args.quiet:
                print(f"🌐 Opening in browser...", file=sys.stderr)
            webbrowser.open(file_url)
    else:
        print(output)
        # Also copy to opus45.html in the project directory when outputting to stdout
        if not args.json:
            opus45_path = Path(__file__).parent / 'opus45.html'
            with open(opus45_path, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"📋 Also saved to {opus45_path}", file=sys.stderr)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
