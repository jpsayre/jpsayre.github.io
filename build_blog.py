#!/usr/bin/env python3
"""
Converts markdown files in posts/ to HTML pages in blog/ and generates blog-data.js.

Usage: python3 build_blog.py

Each markdown file should be named: YYYY-MM-DD-slug.md
The first # heading is used as the post title.
"""

import os
import re
import json
import glob

POSTS_DIR = "posts"
BLOG_DIR = "blog"
TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Jeff Sayre</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link rel="apple-touch-icon" href="../apple-touch-icon.svg">
    <link rel="stylesheet" href="../styles.css">
</head>
<body>
    <nav>
        <div class="nav-brand">
            <a href="../index.html" class="name">Jeff Sayre</a>
            <span class="subtitle">Chicago · engineer &amp; data scientist</span>
        </div>
        <div class="nav-links">
            <a href="../index.html">About</a>
            <a href="../projects.html">Projects</a>
            <a href="../photography.html">Photography</a>
            <a href="../travels.html">Travels</a>
            <a href="../blog.html" class="active">Blog</a>
        </div>
    </nav>
    <div style="padding: 40px 40px 48px; max-width: 780px;">
        <a href="../blog.html" class="post-back">&larr; All posts</a>
        <div class="post-date">{date}</div>
        <div class="post-content">
{content}
        </div>
    </div>
    <footer>
        <span>&copy; 2026 Jeff Sayre</span>
        <div class="footer-links">
            <span>jpsayre@gmail.com</span>
            <a href="https://www.linkedin.com/in/jeff-sayre-b3ab8924/" target="_blank">linkedin.com/in/jeff-sayre</a>
        </div>
    </footer>
</body>
</html>"""


def markdown_to_html(md):
    """Simple markdown to HTML converter — handles headings, paragraphs, images, bold, italic, links, lists, and code."""
    lines = md.split("\n")
    html_lines = []
    in_list = False
    in_code_block = False
    code_lines = []

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                html_lines.append("<pre><code>" + "\n".join(code_lines) + "</code></pre>")
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue
        if in_code_block:
            code_lines.append(line)
            continue

        # List items
        if re.match(r"^[-*]\s+", line.strip()):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            item = re.sub(r"^[-*]\s+", "", line.strip())
            item = inline_formatting(item)
            html_lines.append(f"<li>{item}</li>")
            continue
        elif in_list and line.strip() == "":
            html_lines.append("</ul>")
            in_list = False
            continue
        elif in_list and not re.match(r"^[-*]\s+", line.strip()):
            html_lines.append("</ul>")
            in_list = False

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            text = inline_formatting(m.group(2))
            html_lines.append(f"<h{level}>{text}</h{level}>")
            continue

        # Images
        m = re.match(r"^!\[(.*?)\]\((.*?)\)$", line.strip())
        if m:
            alt, src = m.group(1), m.group(2)
            html_lines.append(f'<img src="{src}" alt="{alt}">')
            continue

        # Empty lines
        if line.strip() == "":
            continue

        # Paragraphs
        text = inline_formatting(line)
        html_lines.append(f"<p>{text}</p>")

    if in_list:
        html_lines.append("</ul>")
    if in_code_block:
        html_lines.append("<pre><code>" + "\n".join(code_lines) + "</code></pre>")

    return "\n".join(html_lines)


def inline_formatting(text):
    """Handle bold, italic, inline code, and links."""
    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Images inline
    text = re.sub(r"!\[(.*?)\]\((.*?)\)", r'<img src="\2" alt="\1">', text)
    # Links
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def extract_title(md):
    """Extract the first # heading as the title."""
    m = re.search(r"^#\s+(.*)", md, re.MULTILINE)
    return m.group(1) if m else "Untitled"


def extract_summary(md):
    """Extract the first paragraph after the title as the summary."""
    lines = md.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            # Strip markdown formatting for summary
            summary = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
            summary = re.sub(r"[*_`]", "", summary)
            return summary[:200]
    return ""


def parse_date(filename):
    """Extract date from filename like 2026-04-21-slug.md."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", os.path.basename(filename))
    return m.group(1) if m else ""


def main():
    os.makedirs(BLOG_DIR, exist_ok=True)

    md_files = sorted(glob.glob(os.path.join(POSTS_DIR, "*.md")), reverse=True)

    blog_entries = []

    for md_file in md_files:
        with open(md_file, "r") as f:
            md = f.read()

        title = extract_title(md)
        date = parse_date(md_file)
        summary = extract_summary(md)

        # Remove the title heading from content (it's shown via template)
        content_md = re.sub(r"^#\s+.*\n*", "", md, count=1)
        content_html = markdown_to_html(content_md)

        slug = os.path.basename(md_file).replace(".md", "")
        html_filename = slug + ".html"
        html_path = os.path.join(BLOG_DIR, html_filename)

        html = TEMPLATE.format(title=title, date=date, content=content_html)

        with open(html_path, "w") as f:
            f.write(html)

        blog_entries.append({
            "title": title,
            "date": date,
            "summary": summary,
            "url": f"blog/{html_filename}",
        })

        print(f"  Built: {html_path}")

    # Write blog-data.js
    js = "const BLOG_POSTS = " + json.dumps(blog_entries, indent=4) + ";\n"
    with open("blog-data.js", "w") as f:
        f.write(js)

    print(f"\n  {len(blog_entries)} post(s) built. blog-data.js updated.")


if __name__ == "__main__":
    main()
