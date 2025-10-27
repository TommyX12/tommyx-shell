import os
import re
import requests
from typing import Optional
from .web import get_title_from_url, get_text_from_url
from .ai import call_llm, LLMConfig
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


def infer_tags(text: str, user_notes: Optional[str] = None) -> list[str]:
    prompt = f"""
You will be given excerpt of a webpage.
Infer a list of tags from it's content. Each tag should consist of one or more lowercase words separated by dash.
Infer at most 3 (most relevant) tags.
First, check each of the following existing tags to see if the content matches. Include any matching tags in the output.
Then, infer any additional tags from the content, only if you think the content is not relevant to any of the existing tags.
Existing tags (and their descriptions):
- agent (agentic llm systems)
- alignment (alignment to human values)
- architecture (new architecture improvements)
- data (data collection, generation, or preparation)
- diffusion (diffusion models)
- distillation (distillation techniques)
- dynamical-system (dynamical system models)
- efficiency (efficiency improvements)
- energy-based-model (energy-based models)
- neural-computation (neural computation techniques)
- reasoning (reasoning or thinking techniques)
- reinforcement-learning (reinforcement learning models)
- reward-model (reward models)
- rnn (recurrent neural networks)
- scaling (scaling techniques)
- search (techniques for searching information)
- training (new training techniques or improvements)
- transformer (related to transformer models)

{f"User notes: {user_notes}" if user_notes else ""}

Raw text:
{text}
"""
    return call_llm(prompt, TagInferenceOutput).tags


class NotesInferenceOutput(BaseModel):
    notes: str


infer_notes_system_prompt = """
You will be given excerpt of an article.
If this is not a research article, summarize the main key ideas.
If this is a research article, summarize the problem, novel contribution (e.g. method), key results. keep only the most important details (e.g. a few points max for the contributions and results), and summarize the exact insight; don't just say "it introduced a new method", say what the method actually is (e.g. main technical details). don't just say "result is better than baseline", say how much it's better and what the values actually are.
The format should be a markdown list. Use nested list (with tab indentation) if possible. Each list item should be extremely concise. Use inline latex (surrounded by $) for all math and symbolic expressions.
"""


def infer_notes_from_text(text: str, user_notes: Optional[str] = None) -> str:
    prompt = f"""
{infer_notes_system_prompt}

{f"User notes: {user_notes}" if user_notes else ""}

Raw text:
{text}
"""
    return call_llm(prompt, NotesInferenceOutput).notes


def infer_notes_from_pdf(pdf_url: str, user_notes: Optional[str] = None) -> str:
    prompt = f"""
{infer_notes_system_prompt}

{f"User notes: {user_notes}" if user_notes else ""}
"""

    return call_llm(
        [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                    {
                        "type": "input_file",
                        "file_url": pdf_url
                    }
                ]
            }
        ],
        NotesInferenceOutput,
        config=LLMConfig(model="gpt-5-mini"),
    ).notes


def add_reading_note(url: str, title: Optional[str] = None, tags: Optional[list[str]] = None, notes: Optional[str] = None):
    print(f"Adding reading note for: {url}")
    if not url:
        raise ValueError("URL is required")

    if not title:
        # Get and sanitize title
        title = get_title_from_url(url)
    
    # Remove arXiv ID from title if present (e.g., "[2510.01123] Title" or "[2510.01123v2] Title" -> "Title")
    title = re.sub(r'^\[\d{4}\.\d{5}(v\d+)?\]\s*', '', title)

    # Get text from url
    page_text_sample = get_text_from_url(url, max_chars=200000)

    if not tags:
        if not page_text_sample:
            raise ValueError("Cannot infer tag, no text found from URL")

        tags = infer_tags(page_text_sample, notes)

    # Check if URL is an arXiv abstract URL and convert to PDF URL
    pdf_url = None
    arxiv_abs_match = re.search(r'arxiv\.org/abs/(\d{4}\.\d{5}(v\d+)?)', url)
    if arxiv_abs_match:
        arxiv_id = arxiv_abs_match.group(1)
        pdf_url = f'https://arxiv.org/pdf/{arxiv_id}'
        print(f"Found arXiv PDF URL: {pdf_url}")
        # Check PDF size before downloading
        try:
            head_response = requests.head(pdf_url, allow_redirects=True, timeout=5)
            content_length = head_response.headers.get('Content-Length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                print(f"PDF size: {size_mb:.2f} MB")
                if size_mb > 10:
                    print(f"PDF size exceeds 10 MB limit. Falling back to text summarization.")
                    pdf_url = None

        except Exception as e:
            print(f"Could not check PDF size: {e}. Falling back to text summarization.")
            pdf_url = None

    if not pdf_url:
        print("Inferring notes from text...")
        ai_notes = infer_notes_from_text(page_text_sample, notes)
    else:
        print("Inferring notes from PDF...")
        ai_notes = infer_notes_from_pdf(pdf_url, notes)
    
    if not notes:
        notes = ai_notes

    else:
        notes = notes + "\n\n" + ai_notes
    
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
    print(f"Creating output file...")
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

    print(f"Created file: {output_path}")
