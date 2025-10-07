import os
import sys
import tempfile
import subprocess
import re
import argparse
from utils.obsidian import add_reading_note
from typing import Optional


def extract_section(content, section_name) -> Optional[str]:
    """Extract content after a section header."""
    pattern = f'^#{section_name}\\s*$'
    lines = content.split('\n')

    in_section = False
    section_lines = []

    for line in lines:
        if re.match(pattern, line, re.IGNORECASE):
            in_section = True
            continue
        elif in_section and line.startswith('#'):
            break
        elif in_section:
            section_lines.append(line)

    return '\n'.join(section_lines).strip() or None


def main():
    parser = argparse.ArgumentParser(description="Add a reading note to Obsidian")
    parser.add_argument("--url", type=str, help="The URL of the reading note", default=None)
    parser.add_argument("--title", type=str, help="The title of the reading note", default=None)
    parser.add_argument("--tags", type=str, help="The tags of the reading note, comma separated", default=None)
    parser.add_argument("--notes", type=str, help="The notes of the reading note", default=None)
    args = parser.parse_args()

    if args.url or args.title or args.tags or args.notes:
        add_reading_note(
            args.url,
            args.title,
            [tag.strip() for tag in args.tags.split(',') if tag.strip()] if args.tags else None,
            args.notes,
        )
        return

    # Create temporary markdown file
    fd, temp_path = tempfile.mkstemp(suffix='.md')

    try:
        # Write initial template
        with os.fdopen(fd, 'w') as f:
            f.write('#URL\n\n#Title\n\n#Tags\n\n#Notes\n\n')

        # Open editor
        editor = os.environ.get('EDITOR', 'vim')
        subprocess.run([editor, temp_path], check=True)

        # Read the edited content
        with open(temp_path, 'r') as f:
            content = f.read()

        # Extract sections
        url = extract_section(content, 'URL')
        assert url, "URL is required"
        title = extract_section(content, 'Title')
        tags = extract_section(content, 'Tags')
        notes = extract_section(content, 'Notes')

        if tags:
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]

        add_reading_note(url, title, tags, notes)

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


if __name__ == '__main__':
    main()
