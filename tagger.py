import argparse
import sys
import os
from llm_client import analyze_readme
from storage import save_tag

def main():
    parser = argparse.ArgumentParser(description="Codebase Tagger - Quickly identify and tag local codebases using an LLM")
    parser.add_argument("--path", type=str, required=True, help="Path to the codebase to analyze")
    parser.add_argument("--csv-path", type=str, default=None, help="Path to the CSV index. Can also be set via TAGGER_CSV_PATH env var. Defaults to codebase_tags.csv in the current directory.")
    parser.add_argument("--provider", type=str, required=True, choices=["openai", "anthropic", "google", "openrouter", "ollama", "lmstudio"], help="LLM inference provider to use")
    parser.add_argument("--model", type=str, required=True, help="Specific model name (e.g. gpt-4o, gemini-2.5-flash)")

    args = parser.parse_args()

    # Determine CSV Path
    csv_path = args.csv_path or os.environ.get("TAGGER_CSV_PATH") or "codebase_tags.csv"

    # Analyze Path
    codebase_path = os.path.abspath(args.path)
    if not os.path.exists(codebase_path):
        print(f"Error: Path '{codebase_path}' does not exist.")
        sys.exit(1)

    readme_path = None
    for filename in ["README.md", "readme.md", "Readme.md"]:
        potential_path = os.path.join(codebase_path, filename)
        if os.path.exists(potential_path):
            readme_path = potential_path
            break
            
    if not readme_path:
        print(f"Error: No README.md found in '{codebase_path}'.")
        sys.exit(1)

    print(f"Reading {readme_path} ...", end="", flush=True)
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
    print(" Done.")

    print(f"Querying {args.provider} ({args.model}) ... ", end="", flush=True)
    try:
        result = analyze_readme(args.provider, args.model, readme_content)
        print("Done.")
    except Exception as e:
        print(f"Failed.\nError: {e}")
        sys.exit(1)

    tag = result.get("tag", "Unknown")
    tech_stack = result.get("tech_stack", "Unknown")
    
    print(f"\nResult:")
    print(f"  Tag: {tag}")
    print(f"  Tech Stack: {tech_stack}")
    
    print(f"\nSaving to {csv_path} ... ", end="", flush=True)
    try:
        save_tag(csv_path, codebase_path, tag, tech_stack)
        print("Done.")
    except Exception as e:
        print(f"Failed.\nError writing to CSV: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
