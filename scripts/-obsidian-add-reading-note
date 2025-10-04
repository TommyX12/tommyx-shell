#!/usr/bin/env python3

import os
import sys
import tempfile
import subprocess
import re
from urllib.request import urlopen
from html.parser import HTMLParser


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = None

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and self.title is None:
            self.title = data.strip()


def extract_section(content, section_name):
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

    return '\n'.join(section_lines).strip()


def get_title_from_url(url):
    """Fetch the webpage and extract the title."""
    try:
        with urlopen(url, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')

        parser = TitleParser()
        parser.feed(html)

        if parser.title:
            return parser.title
        else:
            print("Error: Could not extract title from URL", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)


def sanitize_title(title):
    """Convert title to filename-safe format."""
    # Replace non-alphanumeric (except dash and underscore) with space
    sanitized = re.sub(r'[^a-zA-Z0-9\-_]', ' ', title)
    # Replace consecutive spaces with single dash
    sanitized = re.sub(r' +', ' ', sanitized)
    # Remove leading/trailing dashes
    sanitized = sanitized.strip()
    return sanitized


def main():
    # Create temporary markdown file
    fd, temp_path = tempfile.mkstemp(suffix='.md')

    try:
        # Write initial template
        with os.fdopen(fd, 'w') as f:
            f.write('#URL\n\n#Tags\n\n#Notes\n\n')

        # Open editor
        editor = os.environ.get('EDITOR', 'vim')
        subprocess.run([editor, temp_path], check=True)

        # Read the edited content
        with open(temp_path, 'r') as f:
            content = f.read()

        # Extract sections
        url = extract_section(content, 'URL')
        tags = extract_section(content, 'Tags')
        notes = extract_section(content, 'Notes')

        if not url:
            print("Error: URL section is empty", file=sys.stderr)
            sys.exit(1)

        # Process tags: split by comma, trim, and format as hashtags
        tag_list = [f'#{tag.strip()}' for tag in tags.split(',') if tag.strip()]
        formatted_tags = ' '.join(tag_list)

        # Extract date from arXiv URL or use current date
        arxiv_match = re.search(r'arxiv\.org/abs/(\d{2})(\d{2})\.\d+', url)
        if arxiv_match:
            yy = arxiv_match.group(1)
            mm = arxiv_match.group(2)
            date_str = f'20{yy}-{mm}-01'
        else:
            from datetime import date
            date_str = date.today().strftime('%Y-%m-%d')

        # Get and sanitize title
        page_title = get_title_from_url(url)
        # Remove arXiv ID from title if present (e.g., "[2510.01123] Title" or "[2510.01123v2] Title" -> "Title")
        page_title = re.sub(r'^\[\d{4}\.\d{5}(v\d+)?\]\s*', '', page_title)
        title = sanitize_title(page_title)

        # Create output file
        output_dir = os.path.expanduser('~/data/notes/obsidian')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{title}.md')

        # Write final markdown file
        final_content = f"""# {page_title}
#research {formatted_tags}
date:: {date_str}
- Paper link: {url}
- Code link:

## Prerequisites

## Overview
{notes}

## Method

## Results

## Reading notes

## Ideas

## Other links
"""

        with open(output_path, 'w') as f:
            f.write(final_content)

        print(f"Created: {output_path}")

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


if __name__ == '__main__':
    main()
