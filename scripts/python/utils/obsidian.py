import os
import re
from typing import Optional
from .web import get_title_from_url, get_text_from_url
from .ai import call_llm
from pydantic import BaseModel


def sanitize_to_md_filename(text: str):
    """Convert string to filename-safe format."""
    # Replace non-alphanumeric (except dash and underscore) with space
    sanitized = re.sub(r'[^a-zA-Z0-9\-_]', ' ', text)
    # Replace consecutive spaces with single dash
    sanitized = re.sub(r' +', ' ', sanitized)
    # Remove leading/trailing dashes
    sanitized = sanitized.strip()
    return sanitized


class TagInferenceOutput(BaseModel):
    tags: list[str]


def infer_tags(text: str) -> list[str]:
    prompt = f"""
You will be given excerpt of a webpage.
Infer a list of tags from it's content. Each tag should consist of one or more lowercase words separated by dash.
Infer at most 3 (most relevant) tags.
First, check each of the following existing tags to see if the content matches. Include any matching tags in the output.
Then, infer any additional tags from the content, only if you think the content is not relevant to any of the existing tags.
Existing tags:
- agent
- alignment
- architecture
- diffusion
- distillation
- dynamical-system
- efficiency
- energy-based-model
- neural-computation
- reasoning
- reinforcement-learning
- reward-model
- rnn
- scaling
- search
- training
- transformer

Raw text:
{text}
"""
    return call_llm(prompt, TagInferenceOutput).tags


class NotesInferenceOutput(BaseModel):
    notes: str


def infer_notes(text: str) -> str:
    prompt = f"""
You will be given excerpt of a webpage.
Infer a simple summary of the content: what would you quickly tell an undergraduate researcher about the content so that they understand the main idea and results?
The format should be a markdown list. Use nested list (with tab indentation) if possible. Each list item should be EXTREMELY concise.

Raw text:
{text}
"""
    return call_llm(prompt, NotesInferenceOutput).notes


def add_reading_note(url: str, title: Optional[str] = None, tags: Optional[list[str]] = None, notes: Optional[str] = None):
    if not url:
        raise ValueError("URL is required")

    if not title:
        # Get and sanitize title
        title = get_title_from_url(url)
    
    # Remove arXiv ID from title if present (e.g., "[2510.01123] Title" or "[2510.01123v2] Title" -> "Title")
    title = re.sub(r'^\[\d{4}\.\d{5}(v\d+)?\]\s*', '', title)

    if not tags or not notes:
        # Get text from url
        page_text_sample = get_text_from_url(url, max_chars=5000)

    if not tags:
        tags = infer_tags(page_text_sample)

    if not notes:
        notes = infer_notes(page_text_sample)
    
    filename = sanitize_to_md_filename(title)

    # Extract date from arXiv URL or use current date
    arxiv_match = re.search(r'arxiv\.org/abs/(\d{2})(\d{2})\.\d+', url)
    if arxiv_match:
        yy = arxiv_match.group(1)
        mm = arxiv_match.group(2)
        date_str = f'20{yy}-{mm}-01'
    else:
        from datetime import date
        date_str = date.today().strftime('%Y-%m-%d')

    # Create output file
    output_dir = os.path.expanduser('~/data/notes/obsidian')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'{filename}.md')
    # Ensure the file does not already exist
    if os.path.exists(output_path):
        raise FileExistsError(f"File {output_path} already exists")

    # Write final markdown file
    final_content = f"""# {title}
#research {' '.join([f'#{tag}' for tag in tags])}
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
