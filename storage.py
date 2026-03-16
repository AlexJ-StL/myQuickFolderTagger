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
