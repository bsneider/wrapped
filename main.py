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

    parser.add_argument(
        '--no-telemetry',
        action='store_true',
        help='Do not send anonymous usage metrics'
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

    # Run Prompt DNA analysis
    try:
        from prompt_dna import analyze_prompt_dna, prompt_dna_to_dict

        if not args.quiet:
            print("🧬 Analyzing your Prompt DNA...", file=sys.stderr)

        prompt_dna = analyze_prompt_dna(claude_dir)
        dna_data = prompt_dna_to_dict(prompt_dna)

        # Add to output
        json_data['prompt_dna'] = dna_data

        if not args.quiet:
            print(f"✅ Analyzed {prompt_dna.total_prompts_analyzed} prompts", file=sys.stderr)
            print(f"🎭 Prompt Personality: {prompt_dna.prompt_personality_icon} {prompt_dna.prompt_personality}", file=sys.stderr)

    except ImportError:
        if not args.quiet:
            print("⚠️  prompt_dna.py not found, skipping prompt analysis", file=sys.stderr)
    except Exception as e:
        if not args.quiet:
            print(f"⚠️  Prompt DNA analysis failed: {e}", file=sys.stderr)

    # Run Proficiency Analysis (research-backed 4-dimension scoring)
    try:
        from proficiency_analyzer import analyze_proficiency, proficiency_to_dict

        if not args.quiet:
            print("📊 Analyzing prompting proficiency...", file=sys.stderr)

        # Pass tool data for tool use analysis
        tool_data = {'tool_frequency': json_data.get('tool_frequency', {})}
        proficiency = analyze_proficiency(claude_dir, tool_data)
        proficiency_data = proficiency_to_dict(proficiency)

        # Add to output
        json_data['proficiency'] = proficiency_data

        if not args.quiet:
            print(f"✅ Overall Proficiency: {proficiency.overall_proficiency}/100 ({proficiency.proficiency_level})", file=sys.stderr)
            print(f"   Prompt: {proficiency.prompt_engineering_score} | Context: {proficiency.context_engineering_score} | Memory: {proficiency.memory_engineering_score} | Tools: {proficiency.tool_use_score}", file=sys.stderr)

    except ImportError:
        if not args.quiet:
            print("⚠️  proficiency_analyzer.py not found, skipping proficiency analysis", file=sys.stderr)
    except Exception as e:
        if not args.quiet:
            print(f"⚠️  Proficiency analysis failed: {e}", file=sys.stderr)

    # Run git repository analysis
    try:
        from git_analyzer import analyze_all_repos, correlate_repos_to_projects

        if not args.quiet:
            print("📂 Scanning git repositories...", file=sys.stderr)

        # Use same base paths as project analyzer
        git_base_paths = [
            str(Path.home() / 'sundai'),
            str(Path.home() / 'projects'),
            str(Path.home() / 'repos'),
            str(Path.home() / 'code'),
            str(Path.home() / 'dev'),
            str(Path.home() / 'work'),
            str(Path.home() / 'github'),
        ]

        git_repos, git_summary = analyze_all_repos(git_base_paths, max_repos=100)

        # Add git summary metrics to output
        json_data['git_repos_analyzed'] = git_summary.repos_analyzed
        json_data['git_total_commits'] = git_summary.total_commits
        json_data['git_user_commits'] = git_summary.user_commits
        json_data['git_total_lines_written'] = git_summary.total_net_lines
        json_data['git_primary_languages'] = sorted(
            git_summary.languages.items(),
            key=lambda x: -x[1]
        )[:10]
        json_data['git_hourly_distribution'] = git_summary.hourly_distribution
        json_data['git_daily_distribution'] = git_summary.daily_distribution
        json_data['git_most_active_repo'] = git_summary.most_active_repo
        json_data['git_most_active_repo_commits'] = git_summary.most_active_repo_commits
        json_data['git_longest_streak_days'] = git_summary.longest_streak_days
        json_data['git_current_streak_days'] = git_summary.current_streak_days
        json_data['git_peak_hour'] = git_summary.peak_hour
        json_data['git_peak_day'] = git_summary.peak_day
        json_data['git_weekend_ratio'] = git_summary.weekend_ratio
        json_data['git_top_repos'] = git_summary.top_repos

        # Correlate git repos with Claude projects
        claude_projects = json_data.get('top_projects', [])
        repo_matches = correlate_repos_to_projects(git_repos, claude_projects)

        # Build combined project rankings (merging Claude + Git data)
        combined_projects = []
        git_repo_map = {r.name.lower().replace('_', '-'): r for r in git_repos}

        for proj in claude_projects:
            combined = dict(proj)
            proj_name_normalized = proj['name'].lower().replace('_', '-')

            matched_repo = repo_matches.get(proj['name']) or git_repo_map.get(proj_name_normalized)

            if matched_repo:
                combined['git_commits'] = matched_repo.total_commits
                combined['git_user_commits'] = matched_repo.user_commits
                combined['git_lines_changed'] = matched_repo.total_additions + matched_repo.total_deletions
                combined['git_net_lines'] = matched_repo.net_lines
                combined['git_languages'] = matched_repo.languages
                combined['git_primary_language'] = matched_repo.primary_language
                combined['git_last_commit'] = matched_repo.last_commit.isoformat() if matched_repo.last_commit else None
                combined['git_engagement_score'] = matched_repo.engagement_score

                claude_score = proj.get('engagement_score', 0)
                git_score = matched_repo.engagement_score
                combined['combined_engagement_score'] = 0.60 * claude_score + 0.40 * git_score
                combined['has_git_data'] = True
            else:
                combined['combined_engagement_score'] = 0.85 * proj.get('engagement_score', 0)
                combined['has_git_data'] = False

            combined_projects.append(combined)

        # Add git-only projects
        matched_repos = set(r.name for r in repo_matches.values())
        for repo in git_repos:
            if repo.name not in matched_repos:
                repo_normalized = repo.name.lower().replace('_', '-')
                already_matched = any(
                    p.get('name', '').lower().replace('_', '-') == repo_normalized
                    for p in combined_projects
                )

                if not already_matched:
                    combined_projects.append({
                        'name': repo.name,
                        'display_name': repo.name,
                        'full_path': repo.path,
                        'sessions': 0,
                        'messages': 0,
                        'tokens': 0,
                        'cost': 0,
                        'duration_ms': 0,
                        'git_commits': repo.total_commits,
                        'git_user_commits': repo.user_commits,
                        'git_lines_changed': repo.total_additions + repo.total_deletions,
                        'git_net_lines': repo.net_lines,
                        'git_languages': repo.languages,
                        'git_primary_language': repo.primary_language,
                        'git_last_commit': repo.last_commit.isoformat() if repo.last_commit else None,
                        'git_engagement_score': repo.engagement_score,
                        'combined_engagement_score': 0.50 * repo.engagement_score,
                        'has_git_data': True,
                        'git_only': True,
                    })

        combined_projects.sort(key=lambda x: x.get('combined_engagement_score', 0), reverse=True)
        json_data['top_projects_combined'] = combined_projects[:50]

        if not args.quiet:
            print(f"✅ Analyzed {git_summary.repos_analyzed} git repos, matched {len(repo_matches)} to Claude projects", file=sys.stderr)

    except ImportError:
        if not args.quiet:
            print("⚠️  git_analyzer.py not found, skipping git analysis", file=sys.stderr)
    except Exception as e:
        if not args.quiet:
            print(f"⚠️  Git analysis failed: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)

    # Send telemetry (opt-out with --no-telemetry)
    if not getattr(args, 'no_telemetry', False):
        try:
            import urllib.request
            import urllib.error
            import hashlib
            import platform

            if not args.quiet:
                print("📡 Syncing anonymous metrics...", file=sys.stderr)

            # Generate privacy-safe fingerprint
            fp_data = f"{platform.node()}|{platform.system()}|{platform.machine()}"
            fingerprint = hashlib.sha256(fp_data.encode()).hexdigest()[:16]

            # Build telemetry payload from json_data
            tool_freq = json_data.get('tool_frequency', {})
            model_freq = json_data.get('model_frequency', {})
            total_model_uses = sum(model_freq.values()) or 1

            # Calculate model percentages
            opus_count = sum(v for k, v in model_freq.items() if 'opus' in k.lower())
            sonnet_count = sum(v for k, v in model_freq.items() if 'sonnet' in k.lower())
            haiku_count = sum(v for k, v in model_freq.items() if 'haiku' in k.lower())

            # Get prompt DNA data if available
            prompt_dna = json_data.get('prompt_dna', {})

            telemetry_payload = {
                'fingerprint': fingerprint,
                'client_version': '1.0.0',
                'event_type': 'wrapped_generated',

                # Core metrics
                'total_sessions': json_data.get('total_sessions'),
                'total_messages': json_data.get('total_messages'),
                'total_tokens': (json_data.get('total_input_tokens', 0) or 0) + (json_data.get('total_output_tokens', 0) or 0),
                'total_cost_usd': json_data.get('total_cost_usd'),

                # Usage patterns
                'peak_hour': json_data.get('peak_hour'),
                'peak_day': json_data.get('peak_day'),
                'weekend_ratio': json_data.get('weekend_ratio'),
                'longest_streak_days': json_data.get('longest_streak_days'),

                # Model distribution
                'model_opus_pct': round(opus_count * 100 / total_model_uses, 1) if total_model_uses else None,
                'model_sonnet_pct': round(sonnet_count * 100 / total_model_uses, 1) if total_model_uses else None,
                'model_haiku_pct': round(haiku_count * 100 / total_model_uses, 1) if total_model_uses else None,

                # Proficiency
                'cache_hit_rate': json_data.get('cache_efficiency_ratio'),

                # Prompt DNA
                'total_prompts_analyzed': prompt_dna.get('total_prompts_analyzed'),
                'avg_prompt_length': prompt_dna.get('avg_prompt_length_words'),
                'prompt_personality': prompt_dna.get('prompt_personality'),
                'communication_style': prompt_dna.get('prompt_style'),
                'top_catchphrases_count': len(prompt_dna.get('top_catchphrases', [])),
                'house_rules_count': len(prompt_dna.get('house_rules', [])),

                # Tool usage
                'tool_read_count': tool_freq.get('Read', 0),
                'tool_edit_count': tool_freq.get('Edit', 0),
                'tool_bash_count': tool_freq.get('Bash', 0),
                'tool_write_count': tool_freq.get('Write', 0),
                'tool_grep_count': tool_freq.get('Grep', 0),
                'tool_glob_count': tool_freq.get('Glob', 0),
                'tool_task_count': tool_freq.get('Task', 0),

                # Personality
                'developer_personality': json_data.get('developer_personality'),
                'coding_city': json_data.get('coding_city'),

                # Git metrics
                'git_repos_analyzed': json_data.get('git_repos_analyzed'),
                'git_total_commits': json_data.get('git_total_commits'),
                'git_user_commits': json_data.get('git_user_commits'),
                'git_total_lines_written': json_data.get('git_total_lines_written'),

                # Projects
                'projects_count': len(json_data.get('top_projects', [])),
                'top_project_sessions': json_data.get('top_projects', [{}])[0].get('sessions') if json_data.get('top_projects') else None,
            }

            # Send to telemetry endpoint
            req = urllib.request.Request(
                'https://claude-wrapped-telemetry.pierretokns.workers.dev/api/wrapped',
                data=json.dumps(telemetry_payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 201:
                    if not args.quiet:
                        print("✅ Metrics synced (anonymous)", file=sys.stderr)

        except Exception as e:
            if not args.quiet:
                print(f"⚠️  Metrics sync skipped: {e}", file=sys.stderr)

    # Fetch community benchmarks for percentile rankings
    try:
        import urllib.request

        if not args.quiet:
            print("📊 Fetching community benchmarks...", file=sys.stderr)

        req = urllib.request.Request(
            'https://claude-wrapped-telemetry.pierretokns.workers.dev/api/benchmarks',
            headers={'Accept': 'application/json'},
            method='GET'
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            benchmarks_data = json.loads(resp.read().decode('utf-8'))

            if benchmarks_data.get('success'):
                benchmarks = benchmarks_data['data']['benchmarks']
                total_community = benchmarks_data['data']['total_users']

                # Calculate percentiles for user
                user_sessions = json_data.get('total_sessions', 0)
                user_cost = json_data.get('total_cost_usd', 0)

                def calc_percentile(value, p25, p50, p75, p90, max_val):
                    """Estimate percentile based on distribution markers."""
                    if value >= max_val:
                        return 99
                    elif value >= p90:
                        return 90 + int((value - p90) / (max_val - p90 + 1) * 9)
                    elif value >= p75:
                        return 75 + int((value - p75) / (p90 - p75 + 1) * 15)
                    elif value >= p50:
                        return 50 + int((value - p50) / (p75 - p50 + 1) * 25)
                    elif value >= p25:
                        return 25 + int((value - p25) / (p50 - p25 + 1) * 25)
                    else:
                        return max(1, int(value / (p25 + 1) * 25))

                session_percentile = calc_percentile(
                    user_sessions,
                    benchmarks['sessions']['p25'],
                    benchmarks['sessions']['p50'],
                    benchmarks['sessions']['p75'],
                    benchmarks['sessions']['p90'],
                    benchmarks['sessions']['max']
                )

                cost_percentile = calc_percentile(
                    user_cost,
                    benchmarks['cost_usd']['p25'],
                    benchmarks['cost_usd']['p50'],
                    benchmarks['cost_usd']['p75'],
                    benchmarks['cost_usd']['p90'],
                    benchmarks['cost_usd']['max']
                )

                # Calculate token percentile if available
                user_tokens = json_data.get('total_input_tokens', 0) + json_data.get('total_output_tokens', 0)
                token_percentile = 50  # default
                avg_tokens = 0
                if 'tokens' in benchmarks:
                    token_percentile = calc_percentile(
                        user_tokens,
                        benchmarks['tokens']['p25'],
                        benchmarks['tokens']['p50'],
                        benchmarks['tokens']['p75'],
                        benchmarks['tokens']['p90'],
                        benchmarks['tokens']['max']
                    )
                    avg_tokens = benchmarks['tokens']['avg']

                # Calculate projects percentile if available
                user_projects = json_data.get('unique_projects', 0)
                projects_percentile = 50  # default
                avg_projects = 0
                if 'projects' in benchmarks:
                    projects_percentile = calc_percentile(
                        user_projects,
                        benchmarks['projects']['p25'],
                        benchmarks['projects']['p50'],
                        benchmarks['projects']['p75'],
                        benchmarks['projects']['p90'],
                        benchmarks['projects']['max']
                    )
                    avg_projects = benchmarks['projects']['avg']

                json_data['community_benchmarks'] = {
                    'total_users': total_community,
                    'session_percentile': session_percentile,
                    'cost_percentile': cost_percentile,
                    'token_percentile': token_percentile,
                    'projects_percentile': projects_percentile,
                    'avg_sessions': benchmarks['sessions']['avg'],
                    'avg_cost': benchmarks['cost_usd']['avg'],
                    'avg_tokens': avg_tokens,
                    'avg_projects': avg_projects,
                    'user_tokens': user_tokens,
                    'user_projects': user_projects,
                }

                if not args.quiet:
                    print(f"✅ You're in the top {100 - session_percentile}% by sessions!", file=sys.stderr)

    except Exception as e:
        if not args.quiet:
            print(f"⚠️  Benchmarks skipped: {e}", file=sys.stderr)

    # Generate comparative achievements (you vs community)
    achievements = []
    benchmarks = json_data.get('community_benchmarks', {})

    total_sessions = json_data.get('total_sessions', 0)
    total_cost = json_data.get('total_cost_usd', 0)
    total_tokens = (json_data.get('total_input_tokens', 0) or 0) + (json_data.get('total_output_tokens', 0) or 0)
    unique_projects = json_data.get('unique_projects', 0)
    longest_streak = json_data.get('longest_streak_days', 0)
    peak_hour = json_data.get('peak_hour', 12)
    weekend_ratio = json_data.get('weekend_ratio', 0)
    tool_freq = json_data.get('tool_frequency', {})

    # Check if we have benchmark data for comparative achievements
    has_benchmarks = bool(benchmarks.get('session_percentile'))

    if has_benchmarks:
        # Get percentiles from benchmarks
        session_pct = benchmarks.get('session_percentile', 50)
        cost_pct = benchmarks.get('cost_percentile', 50)
        token_pct = benchmarks.get('token_percentile', 50)
        projects_pct = benchmarks.get('projects_percentile', 50)

        # Session ranking
        if session_pct >= 90:
            achievements.append({'id': 'sessions_top10', 'name': 'Power User', 'icon': '⚡', 'desc': f'Top 10% by sessions ({total_sessions:,})'})
        elif session_pct >= 75:
            achievements.append({'id': 'sessions_top25', 'name': 'Heavy User', 'icon': '🎯', 'desc': f'Top 25% by sessions ({total_sessions:,})'})
        elif session_pct >= 50:
            achievements.append({'id': 'sessions_top50', 'name': 'Active User', 'icon': '📊', 'desc': f'Top 50% by sessions ({total_sessions:,})'})

        # Token ranking
        if token_pct >= 90:
            achievements.append({'id': 'tokens_top10', 'name': 'Token Titan', 'icon': '🏆', 'desc': f'Top 10% by tokens'})
        elif token_pct >= 75:
            achievements.append({'id': 'tokens_top25', 'name': 'Token Master', 'icon': '🔤', 'desc': f'Top 25% by tokens'})

        # Project diversity ranking
        if projects_pct >= 90:
            achievements.append({'id': 'projects_top10', 'name': 'Project Polyglot', 'icon': '🗂️', 'desc': f'Top 10% by projects ({unique_projects})'})
        elif projects_pct >= 75:
            achievements.append({'id': 'projects_top25', 'name': 'Multi-tasker', 'icon': '📁', 'desc': f'Top 25% by projects ({unique_projects})'})

        # Cost ranking (high spending = dedicated)
        if cost_pct >= 90:
            achievements.append({'id': 'cost_top10', 'name': 'Big Spender', 'icon': '💸', 'desc': f'Top 10% by investment (${total_cost:.0f})'})
        elif cost_pct >= 75:
            achievements.append({'id': 'cost_top25', 'name': 'Committed', 'icon': '💰', 'desc': f'Top 25% by investment (${total_cost:.0f})'})
    else:
        # Fallback: milestone-based achievements when benchmarks unavailable
        if total_sessions >= 1000:
            achievements.append({'id': 'sessions_1k', 'name': 'Power User', 'icon': '⚡', 'desc': f'{total_sessions:,} sessions'})
        elif total_sessions >= 500:
            achievements.append({'id': 'sessions_500', 'name': 'Heavy User', 'icon': '🎯', 'desc': f'{total_sessions:,} sessions'})
        elif total_sessions >= 100:
            achievements.append({'id': 'sessions_100', 'name': 'Active User', 'icon': '📊', 'desc': f'{total_sessions:,} sessions'})

        if total_tokens >= 10_000_000:
            achievements.append({'id': 'tokens_10m', 'name': 'Token Titan', 'icon': '🏆', 'desc': '10M+ tokens'})
        elif total_tokens >= 1_000_000:
            achievements.append({'id': 'tokens_1m', 'name': 'Token Master', 'icon': '🔤', 'desc': '1M+ tokens'})

        if total_cost >= 500:
            achievements.append({'id': 'cost_500', 'name': 'Big Spender', 'icon': '💸', 'desc': f'${total_cost:.0f} invested'})
        elif total_cost >= 100:
            achievements.append({'id': 'cost_100', 'name': 'Committed', 'icon': '💰', 'desc': f'${total_cost:.0f} invested'})

    # Non-comparative achievements (always available)
    if longest_streak >= 30:
        achievements.append({'id': 'streak_30', 'name': 'Month Warrior', 'icon': '🔥', 'desc': f'{longest_streak} day streak'})
    elif longest_streak >= 14:
        achievements.append({'id': 'streak_14', 'name': 'Two Week Streak', 'icon': '📅', 'desc': f'{longest_streak} day streak'})
    elif longest_streak >= 7:
        achievements.append({'id': 'streak_7', 'name': 'Week Warrior', 'icon': '🗓️', 'desc': f'{longest_streak} day streak'})

    if peak_hour >= 22 or peak_hour <= 4:
        achievements.append({'id': 'night_owl', 'name': 'Night Owl', 'icon': '🦉', 'desc': 'Peak coding after 10pm'})
    elif peak_hour >= 5 and peak_hour <= 8:
        achievements.append({'id': 'early_bird', 'name': 'Early Bird', 'icon': '🐦', 'desc': 'Peak coding before 9am'})

    if weekend_ratio and weekend_ratio > 0.4:
        achievements.append({'id': 'weekend_warrior', 'name': 'Weekend Warrior', 'icon': '⚔️', 'desc': '40%+ weekend coding'})

    if tool_freq.get('Task', 0) >= 50:
        achievements.append({'id': 'delegator', 'name': 'The Delegator', 'icon': '👥', 'desc': f'{tool_freq.get("Task", 0)} Task tool uses'})
    if tool_freq.get('Bash', 0) >= 500:
        achievements.append({'id': 'shell_master', 'name': 'Shell Master', 'icon': '💻', 'desc': f'{tool_freq.get("Bash", 0):,} Bash commands'})

    # Efficiency: high tokens per dollar spent
    if total_cost > 0:
        tokens_per_dollar = total_tokens / total_cost
        if tokens_per_dollar > 50000:  # >50K tokens per dollar
            achievements.append({'id': 'efficient', 'name': 'Efficiency Expert', 'icon': '💡', 'desc': f'{tokens_per_dollar/1000:.0f}K tokens/$'})

    # First wrapped (everyone gets this)
    achievements.append({'id': 'first_wrapped', 'name': 'Wrapped 2025', 'icon': '🎁', 'desc': 'Generated your first wrapped'})

    json_data['achievements'] = achievements
    if not args.quiet and achievements:
        print(f"🏆 Unlocked {len(achievements)} achievements!", file=sys.stderr)

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

        # Serve via HTTP and open in browser (unless --no-open)
        if not args.json and not args.no_open:
            import webbrowser
            import http.server
            import socketserver
            import threading

            # Find an available port
            port = 8765
            for p in range(8765, 8800):
                try:
                    with socketserver.TCPServer(("", p), None) as test:
                        port = p
                        break
                except OSError:
                    continue

            # Serve from the output directory
            serve_dir = output_path.parent
            serve_file = output_path.name

            class QuietHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=str(serve_dir), **kwargs)
                def log_message(self, format, *args):
                    pass  # Suppress logging

            server = socketserver.TCPServer(("", port), QuietHandler)
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()

            url = f"http://localhost:{port}/{serve_file}"
            if not args.quiet:
                print(f"🌐 Serving at {url}", file=sys.stderr)
                print(f"   (Ctrl+C to stop server)", file=sys.stderr)
            webbrowser.open(url)

            # Keep server running until interrupted
            try:
                server_thread.join()
            except KeyboardInterrupt:
                if not args.quiet:
                    print(f"\n👋 Server stopped", file=sys.stderr)
                server.shutdown()
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
