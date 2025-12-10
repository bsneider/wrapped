
import os
import json
import jinja2
from analyzer import ClaudeAnalyzer

class ClaudeGenerator:
    def __init__(self, context):
        self.context = context
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    
    def generate(self, output_path="claude_wrapped.html"):
        template = self.env.get_template('wrapped.html')
        
        # Prepare data for charts
        project_stats = self.context.get('project_stats', {})
        history = self.context.get('history', [])
        
        # safely handle empty data
        if not history:
            hourly_activity = [0] * 24
        else:
            # Process hourly activity for chart
            processed_history = []
            for h in history:
                 # Check if the dictionary has timestamp converted or needs conversion
                 # In analyzer we converted to datetime, but to_dict might have made it string or timestamp
                 # For safety in template, let's pre-process chart data here
                 pass
            
            # Simple list for Chart.js [0, 1, 2... 23]
            hourly_counts = {}
            for h in history:
                try:
                    ts = h.get('timestamp')
                    # If it's a pandas Timestamp, it has .hour
                    # If it's a string, we might need parsing, but analyzer kept it as object in memory (or lost it via to_dict)
                    # Let's rely on simple extraction
                    if hasattr(ts, 'hour'):
                        h_hour = ts.hour
                    else:
                        continue 
                    hourly_counts[h_hour] = hourly_counts.get(h_hour, 0) + 1
                except:
                    continue
            hourly_activity = [hourly_counts.get(i, 0) for i in range(24)]

        # Render
        html_content = template.render(
            metrics=self.context.get('global_metrics', {}),
            project_stats=project_stats,
            statsig=self.context.get('statsig_stats', {}),
            debug=self.context.get('debug_stats', {}),
            hourly_activity=json.dumps(hourly_activity),
            year=2025
        )
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"🚀 Wrapped generated at: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    analyzer = ClaudeAnalyzer()
    analyzer.load_data()
    context = analyzer.get_context()
    
    generator = ClaudeGenerator(context)
    generator.generate()
