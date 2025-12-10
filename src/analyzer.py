
import os
import glob
import json
import pandas as pd
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict

class ClaudeAnalyzer:
    def __init__(self, base_dir=os.path.expanduser("~/.claude")):
        self.base_dir = base_dir
        self.history_df = pd.DataFrame()
        self.project_stats = {}
        self.todos_df = pd.DataFrame()
        self.debug_stats = {}
        self.statsig_stats = {}
        self.global_metrics = {}

    def load_data(self):
        print("⏳ Loading history...")
        self._load_history()
        print("⏳ Loading project data (this might take a moment)...")
        self._load_projects()
        print("⏳ Loading TODOs...")
        self._load_todos()
        print("⏳ Loading Debug logs...")
        self._load_debug()
        print("⏳ Loading Statsig data...")
        self._load_statsig()
        
        self._calculate_global_metrics()
        print("✅ Data loading complete.")

    def _load_history(self):
        history_path = os.path.join(self.base_dir, "history.jsonl")
        if not os.path.exists(history_path):
            return

        data = []
        with open(history_path, 'r') as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        if data:
            self.history_df = pd.DataFrame(data)
            if 'timestamp' in self.history_df.columns:
                self.history_df['timestamp'] = pd.to_datetime(self.history_df['timestamp'], unit='ms')

    def _load_projects(self):
        # Recursive glob for project JSON files
        # Looking for {uuid}.jsonl and agent-{uuid}.jsonl
        pattern = os.path.join(self.base_dir, "projects", "**", "*.jsonl")
        files = glob.glob(pattern, recursive=True)
        
        all_sessions = []
        metrics = {
            "total_files": len(files),
            "sidechains": 0,
            "main_chains": 0,
            "total_cost": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "cache_creation": 0,
            "cache_read": 0,
            "tools_used": Counter(),
            "models_used": set(),
            "deepest_nesting": (0, "")
        }

        for fpath in files:
            is_sidechain = "agent-" in os.path.basename(fpath)
            if is_sidechain:
                metrics["sidechains"] += 1
            else:
                metrics["main_chains"] += 1
            
            # Directory depth analysis
            dir_depth = fpath.count(os.sep)
            if dir_depth > metrics["deepest_nesting"][0]:
                metrics["deepest_nesting"] = (dir_depth, fpath)

            try:
                with open(fpath, 'r') as f:
                    for line in f:
                        if not line.strip(): continue
                        try:
                            record = json.loads(line)
                            
                            # Cost & Tokens
                            if "costUSD" in record:
                                metrics["total_cost"] += record.get("costUSD", 0)
                            
                            usage = record.get("usage", {})
                            metrics["total_input_tokens"] += usage.get("input_tokens", 0)
                            metrics["total_output_tokens"] += usage.get("output_tokens", 0)
                            
                            cache = usage.get("cache_creation", {})
                            metrics["cache_creation"] += cache.get("input_tokens", 0) if isinstance(cache, dict) else 0 # Handle if cache is dict or int if schema varies
                            
                            # cache_read might be in usage directly or nested
                            metrics["cache_read"] += usage.get("cache_read_input_tokens", 0)

                            # Models
                            if "model" in record.get("message", {}):
                                metrics["models_used"].add(record["message"]["model"])

                            # Tools
                            if "tool_use" in record:
                                # Sometimes tool_use is a block or list
                                pass # Simplified for now, would need deep parsing of content blocks
                            
                            # Naive tool parse from text content if structured logs aren't perfect
                            # Or parse 'type': 'tool_use' if available in specific schema versions
                            
                        except:
                            continue
            except:
                continue
        
        self.project_stats = metrics

    def _load_todos(self):
        pattern = os.path.join(self.base_dir, "todos", "*.json")
        files = glob.glob(pattern)
        
        todos = []
        for fpath in files:
            try:
                with open(fpath, 'r') as f:
                    content = json.load(f)
                    if isinstance(content, list):
                        todos.extend(content)
            except:
                continue
        
        if todos:
            self.todos_df = pd.DataFrame(todos)

    def _load_debug(self):
        # Parse debug logs for errors/timeouts
        pattern = os.path.join(self.base_dir, "debug", "*.txt")
        files = glob.glob(pattern)
        
        chaos_score = 0
        plugin_loads = 0
        
        for fpath in files:
            try:
                with open(fpath, 'r') as f:
                    content = f.read()
                    chaos_score += content.count("[ERROR]")
                    chaos_score += content.count("timeout")
                    chaos_score += content.count("Exception")
                    plugin_loads += content.count("Loading skills from")
            except:
                continue
        
        self.debug_stats = {
            "chaos_score": chaos_score,
            "plugins_loaded": plugin_loads
        }

    def _load_statsig(self):
        # Look for statsig cache
        evals_path = glob.glob(os.path.join(self.base_dir, "statsig", "statsig.cached.evaluations.*.json"))
        
        buckets = []
        if evals_path:
            try:
                with open(evals_path[0], 'r') as f:
                    data = json.load(f)
                    # This is usually a hashed map, so we might just count keys or look for known strings
                    # For "viral" effect, we'll just count the number of gates
                    buckets = list(data.keys()) if isinstance(data, dict) else []
            except:
                pass
        
        self.statsig_stats = {
            "feature_gates": len(buckets),
            "sample_gates": buckets[:5]
        }

    def _calculate_global_metrics(self):
        # 1. Total Interactions
        self.global_metrics['total_commands'] = len(self.history_df)
        
        # 2. Daily Rhythm (Ballmer Peak)
        if not self.history_df.empty:
            self.history_df['hour'] = self.history_df['timestamp'].dt.hour
            peak_hour = self.history_df['hour'].mode()[0]
            self.global_metrics['ballmer_peak'] = int(peak_hour)
            
            # Late night coding?
            late_night = len(self.history_df[self.history_df['hour'].isin([0, 1, 2, 3, 4])])
            self.global_metrics['owl_score'] = late_night / len(self.history_df)

        # 3. Yapping Index (Input / Output tokens) -> proxy measure
        # Using project stats
        total_tokens = self.project_stats['total_input_tokens'] + self.project_stats['total_output_tokens']
        if self.project_stats['total_output_tokens'] > 0:
            self.global_metrics['yapping_index'] = self.project_stats['total_input_tokens'] / self.project_stats['total_output_tokens']
        else:
            self.global_metrics['yapping_index'] = 0

        # 4. Agentic Awareness
        total_chains = self.project_stats['main_chains'] + self.project_stats['sidechains']
        self.global_metrics['agentic_score'] = (self.project_stats['sidechains'] / total_chains) if total_chains > 0 else 0

        # 5. Graveyard (TODOs)
        if not self.todos_df.empty and 'status' in self.todos_df.columns:
            counts = self.todos_df['status'].value_counts()
            pending = counts.get('pending', 0)
            completed = counts.get('completed', 0)
            total = pending + completed
            self.global_metrics['graveyard_ratio'] = (pending / total) if total > 0 else 0
        else:
            self.global_metrics['graveyard_ratio'] = 0

        # 6. Cost Inferno
        self.global_metrics['total_cost'] = self.project_stats['total_cost']

    def get_context(self):
        return {
            "history": self.history_df.to_dict(orient='records'),
            "project_stats": self.project_stats,
            "todos_stats": self.todos_df.to_dict(orient='records'),
            "debug_stats": self.debug_stats,
            "statsig_stats": self.statsig_stats,
            "global_metrics": self.global_metrics
        }

if __name__ == "__main__":
    analyzer = ClaudeAnalyzer()
    analyzer.load_data()
    print(json.dumps(analyzer.global_metrics, indent=2))
