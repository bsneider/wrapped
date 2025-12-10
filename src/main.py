
from analyzer import ClaudeAnalyzer
from generator import ClaudeGenerator
import webbrowser
import os

def main():
    print("🚀 Starting Claude Wrapped 2025...")
    
    # 1. Analyze
    analyzer = ClaudeAnalyzer()
    analyzer.load_data()
    context = analyzer.get_context()
    
    # 2. Generate
    generator = ClaudeGenerator(context)
    output_path = "claude_wrapped.html"
    generator.generate(output_path)
    
    # 3. Launch
    abs_path = os.path.abspath(output_path)
    print(f"✨ Opening your Wrapped experience: file://{abs_path}")
    webbrowser.open(f"file://{abs_path}")

if __name__ == "__main__":
    main()
