import csv
import os
import threading

CSV_LOCK = threading.Lock()

def save_tag(csv_path: str, codebase_path: str, tag: str, tech_stack: str = ""):
    """
    Saves the tag and tech stack to the specified CSV file.
    Creates the file and headers if it doesn't exist.
    """
    file_exists = os.path.exists(csv_path)
    
    with CSV_LOCK:
        with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header if file is new
            if not file_exists:
                writer.writerow(["Codebase Path", "Tag", "Tech Stack"])
                
            writer.writerow([os.path.abspath(codebase_path), tag, tech_stack])

def load_processed_repos(csv_path: str) -> set[str]:
    """
    Reads the CSV index and returns a set of absolute paths
    for repositories that have already been tagged.
    """
    processed = set()
    if not os.path.exists(csv_path):
        return processed
        
    with CSV_LOCK:
        with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            # Skip header if it exists
            try:
                _ = next(reader)
            except StopIteration:
                return processed
                
            for row in reader:
                if row and len(row) > 0:
                    processed.add(os.path.abspath(row[0]))
                    
    return processed
