# Filename: ./copy_project.py
# ----- Start of file content -----
#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

# Directories and files/extensions to exclude
EXCLUDE_DIRS = {".git", ".venv", "venv", "__pycache__", "instance", ".vscode"}
EXCLUDE_FILES = {".env", ".DS_Store"}
EXCLUDE_EXTENSIONS = {".db", ".sqlite", ".pyc", ".log"}

def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded based on predefined rules."""
    # Check parent directories
    for parent in path.parents:
        if parent.name in EXCLUDE_DIRS:
            return True
    # Check the item itself (directory or file name)
    if path.name in EXCLUDE_DIRS or path.name in EXCLUDE_FILES:
        return True
    # Check file extension
    if path.is_file() and path.suffix in EXCLUDE_EXTENSIONS:
        return True
    return False

def main():
    """Walks the project directory, collects file contents, and copies to clipboard."""
    project_root = Path(".")
    project_text = ""

    # Sort files for consistent order
    all_paths = sorted(list(project_root.rglob("*")))

    collected_files: list[Path] = []
    for path in all_paths:
        if not should_exclude(path) and path.is_file():
            collected_files.append(path)

    for file_path in collected_files:
        relative_path = file_path.relative_to(project_root)
        project_text += f"Filename: ./{relative_path.as_posix()}\n" # Use posix path sep for consistency
        project_text += "----- Start of file content -----\n"
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                project_text += f.read().strip() + "\n" # Strip trailing whitespace
        except Exception as e:
            project_text += f"Error reading file: {e}\n"
        project_text += "----- End of file content -----\n\n"

    # Copy the complete output to the clipboard using xclip.
    try:
        process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
        process.communicate(input=project_text.encode('utf-8'))
        print("Project contents copied to clipboard.")
    except FileNotFoundError:
        print("Error: 'xclip' command not found. Please install xclip.", file=sys.stderr)
        print("\n--- Project Content ---")
        print(project_text) # Print to stdout as fallback
    except Exception as e:
        print(f"Error copying to clipboard: {e}", file=sys.stderr)
        print("\n--- Project Content ---")
        print(project_text) # Print to stdout as fallback

if __name__ == "__main__":
    main()
