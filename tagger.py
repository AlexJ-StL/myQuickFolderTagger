import argparse
import sys
import os
from llm_client import analyze_readme
from storage import save_tag

IGNORED_DIRS = {
    "node_modules", ".venv", ".git", "__pycache__", "venv", "env",
    ".idea", ".vscode", "build", "dist", ".tox"
}

def find_repos(base_paths: list[str], recursive: bool) -> list[str]:
    """Finds all directories containing a README.md file."""
    repos = []
    
    for base_path in base_paths:
        base_path = os.path.abspath(base_path)
        
        if not os.path.exists(base_path):
            print(f"Warning: Path '{base_path}' does not exist. Skipping.")
            continue
            
        if not recursive:
            if has_readme(base_path):
                repos.append(base_path)
            else:
                print(f"Warning: No README.md found in '{base_path}'. Skipping.")
            continue

        for root, dirs, files in os.walk(base_path):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            
            if has_readme(root):
                repos.append(root)
                
    # Remove duplicates while preserving order
    return list(dict.fromkeys(repos))

def has_readme(directory: str) -> bool:
    for filename in ["README.md", "readme.md", "Readme.md"]:
        if os.path.exists(os.path.join(directory, filename)):
            return True
    return False

def get_readme_path(directory: str) -> str | None:
    for filename in ["README.md", "readme.md", "Readme.md"]:
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            return path
    return None

def process_repo(codebase_path: str, args, csv_path: str):
    readme_path = get_readme_path(codebase_path)
    if not readme_path:
        return

    print(f"\n[{codebase_path}]")
    print(f"Reading {os.path.basename(readme_path)} ...", end="", flush=True)
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
    print(" Done.")

    print(f"Querying {args.provider} ({args.model}) ... ", end="", flush=True)
    try:
        result = analyze_readme(args.provider, args.model, readme_content)
        print("Done.")
    except Exception as e:
        print(f"Failed.\nError: {e}")
        return

    tag = result.get("tag", "Unknown")
    tech_stack = result.get("tech_stack", "Unknown")
    
    print("\nResult:")
    print(f"  Tag: {tag}")
    print(f"  Tech Stack: {tech_stack}")
    
    print(f"Saving to {csv_path} ... ", end="", flush=True)
    try:
        save_tag(csv_path, codebase_path, tag, tech_stack)
        print("Done.")
    except Exception as e:
        print(f"Failed.\nError writing to CSV: {e}")

def main():
    parser = argparse.ArgumentParser(description="Codebase Tagger - Quickly identify and tag local codebases using an LLM")
    parser.add_argument("--path", type=str, nargs="+", required=True, help="One or more paths to the codebases or directories to analyze")
    parser.add_argument("--recursive", action="store_true", help="Recursively search for README.md files within the provided paths")
    parser.add_argument("--csv-path", type=str, default=None, help="Path to the CSV index. Can also be set via TAGGER_CSV_PATH env var. Defaults to codebase_tags.csv in the current directory.")
    parser.add_argument("--provider", type=str, required=True, choices=["openai", "anthropic", "google", "openrouter", "ollama", "lmstudio"], help="LLM inference provider to use")
    parser.add_argument("--model", type=str, required=True, help="Specific model name (e.g. gpt-4o, gemini-2.5-flash)")

    args = parser.parse_args()

    # Determine CSV Path
    csv_path = args.csv_path or os.environ.get("TAGGER_CSV_PATH") or "codebase_tags.csv"
    csv_path = os.path.abspath(csv_path)

    # Find repositories
    print("Searching for repositories...", end="", flush=True)
    repos = find_repos(args.path, args.recursive)
    print(f" Found {len(repos)}.")

    if not repos:
        print("No repositories found to process.")
        sys.exit(0)

    # Process each repo
    for repo in repos:
        process_repo(repo, args, csv_path)

if __name__ == "__main__":
    main()
