#!/usr/bin/env python3
"""Post-process pandoc GFM output of man pages for the Himmelblau MkDocs site."""
import re
import sys

# Matches any markdown heading
HEADING_RE = re.compile(r'^(#{1,6}) (.+)')
# Matches bold synopsis lines at the start of a paragraph.
# Matches **aad-tool, **pam_himmelblau.so**, **himmelblaud**, **/etc/himmelblau/...
SYNOPSIS_RE = re.compile(r'^\*\*[\w/]')
# Matches pandoc's double-blockquote lines used for command examples
DOUBLE_BLOCKQUOTE_RE = re.compile(r'^> > (.+)')
# Matches consecutive single-blockquote lines (used for code-like examples)
SINGLE_BLOCKQUOTE_RE = re.compile(r'^> ')
# Matches pandoc's HTML comment separator between adjacent bold paragraphs
HTML_COMMENT_RE = re.compile(r'^<!-- -->$')
# Any markdown heading (for dedup section skipping)
ANY_HEADING_RE = re.compile(r'^#{1,6}( |$)')


def shift_headings(lines):
    """Shift all heading levels down by one: # → ##, ## → ###, etc."""
    out = []
    in_fence = False
    for line in lines:
        if line.startswith('```'):
            in_fence = not in_fence
        if not in_fence:
            m = HEADING_RE.match(line)
            if m:
                line = '#' + m.group(1) + ' ' + m.group(2) + '\n'
        out.append(line)
    return out


def unescape_backticks(lines):
    """Convert pandoc's escaped backticks \\` to real backtick code spans.

    Pandoc escapes backticks in GFM output. Convert paired \\`text\\` to
    `text` (inline code span) outside of code fences.
    """
    out = []
    in_fence = False
    for line in lines:
        if line.startswith('```'):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            # Replace \`...\` pairs with `...` (code spans)
            line = re.sub(r'\\`([^`]+)\\`', r'`\1`', line)
            # Remove any remaining lone escaped backticks
            line = line.replace('\\`', '`')
        out.append(line)
    return out


def unescape_pandoc(lines):
    """Strip pandoc's backslash escapes from body text outside code fences.

    Pandoc escapes <, >, [, ], #, and numbered list periods in GFM output.
    These render as literal backslashes in many contexts.
    """
    out = []
    in_fence = False
    for line in lines:
        if line.startswith('```'):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            line = line.replace('\\<', '<').replace('\\>', '>')
            line = line.replace('\\[', '[').replace('\\]', ']')
            # Escaped # at start of line (shell prompt or comment)
            line = re.sub(r'^\\#', '#', line)
            # Escaped numbered list: 1\. → 1.
            line = re.sub(r'^(\d+)\\.', r'\1.', line)
            # Escaped dash at start (list items inside code-like blocks)
            line = re.sub(r'^\\-', '-', line)
        out.append(line)
    return out


def clean_trailing_backslashes(lines):
    """Remove trailing backslash line continuations from groff conversion."""
    out = []
    in_fence = False
    for line in lines:
        if line.startswith('```'):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence and line.rstrip('\n').endswith('\\'):
            line = line.rstrip('\n').rstrip('\\') + '\n'
        out.append(line)
    return out


def fix_bold_punctuation(lines):
    """Move trailing punctuation outside bold spans: **word,** → **word**,"""
    out = []
    in_fence = False
    for line in lines:
        if line.startswith('```'):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            # **word,** → **word**, and **word.** → **word**.
            line = re.sub(r'\*\*([^*]+?)([,.])\*\*', r'**\1**\2', line)
        out.append(line)
    return out


def remove_html_comments(lines):
    """Remove <!-- --> separators pandoc inserts between adjacent bold items."""
    return [line for line in lines if not HTML_COMMENT_RE.match(line.rstrip('\n'))]


def deduplicate_sections(lines):
    """Remove duplicate ## SYNOPSIS and ## DESCRIPTION headings and their content."""
    seen_synopsis = False
    seen_description = False
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip('\n')
        if stripped == '## SYNOPSIS':
            if seen_synopsis:
                i += 1
                while i < len(lines) and not ANY_HEADING_RE.match(lines[i]):
                    i += 1
                continue
            seen_synopsis = True
        elif stripped == '## DESCRIPTION':
            if seen_description:
                i += 1
                while i < len(lines) and not ANY_HEADING_RE.match(lines[i]):
                    i += 1
                continue
            seen_description = True
        out.append(line)
        i += 1
    return out


def clean_synopsis(line):
    """Strip markdown formatting from a bold subcommand synopsis line."""
    s = line.strip()
    s = re.sub(r'^\*\*(.+)\*\*$', r'\1', s)   # remove outer **bold**
    # Remove *italic* spans — run twice to handle **aad-tool** → *aad-tool* → aad-tool
    s = re.sub(r'\*([^*]+)\*', r'\1', s)
    s = re.sub(r'\*([^*]+)\*', r'\1', s)
    s = re.sub(r'\*+', '', s)                   # strip any remaining bare *
    s = re.sub(r'`([^`]*)`', r'\1', s)           # remove `code` ticks
    s = s.replace('\\<', '<').replace('\\>', '>')
    s = s.replace('&lt;', '<').replace('&gt;', '>')
    s = re.sub(r'\\([\[\]])', r'\1', s)          # unescape \[ \]
    # Remove italic _ markers that are not part of identifiers
    s = re.sub(r'(?<![a-zA-Z0-9])_|_(?![a-zA-Z0-9])', '', s)
    s = re.sub(r' {2,}', ' ', s)
    return s.strip()


def collect_synopsis_block(lines, i):
    """Collect a possibly multi-line bold synopsis block starting at lines[i].

    Returns (cleaned_text, new_i). Pandoc sometimes wraps long synopsis lines
    across multiple lines within the same bold span (closing ** on a later line).
    """
    parts = [lines[i].rstrip('\n')]
    # If the line already closes the bold span, it's a single-line synopsis
    if lines[i].rstrip().endswith('**'):
        return clean_synopsis(' '.join(parts)), i + 1
    # Also handle the form **aad-tool** *rest* (bold just the command name)
    # where the line doesn't end with ** but is still a complete synopsis
    i += 1
    while i < len(lines):
        l = lines[i].rstrip('\n')
        if not l:  # blank line ends the block without closing **
            break
        parts.append(l)
        i += 1
        if l.endswith('**'):
            break
    return clean_synopsis(' '.join(parts)), i


def format_code_blocks(lines):
    """Convert synopsis bold lines and double-blockquote commands to code blocks."""
    out = []
    i = 0
    in_fence = False
    last_heading = ''

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip('\n')

        # Track current section heading
        if ANY_HEADING_RE.match(stripped):
            last_heading = stripped

        if line.startswith('```'):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue

        if in_fence:
            out.append(line)
            i += 1
            continue

        # Bold synopsis lines (single or multi-line) → code block.
        # Only fire in SYNOPSIS or SUBCOMMAND sections to avoid
        # swallowing bold text at the start of description paragraphs.
        prev = out[-1].rstrip('\n') if out else ''
        if (SYNOPSIS_RE.match(line)
                and (not prev or ANY_HEADING_RE.match(prev))
                and ('SYNOPSIS' in last_heading or 'SUBCOMMAND' in last_heading)):
            text, i = collect_synopsis_block(lines, i)
            out.append('```text\n')
            out.append(text + '\n')
            out.append('```\n')
            continue

        # Double-blockquote lines (> > command) → fenced code block.
        # A lone '>' line between two '> >' groups is treated as a blank
        # separator line inside the same code block.
        if DOUBLE_BLOCKQUOTE_RE.match(line):
            out.append('```text\n')
            while i < len(lines):
                if DOUBLE_BLOCKQUOTE_RE.match(lines[i]):
                    out.append(DOUBLE_BLOCKQUOTE_RE.match(lines[i]).group(1) + '\n')
                    i += 1
                elif lines[i].rstrip('\n') == '>':
                    # Peek ahead: if the next non-empty line is another > >, keep going
                    j = i + 1
                    while j < len(lines) and lines[j].rstrip('\n') == '>':
                        j += 1
                    if j < len(lines) and DOUBLE_BLOCKQUOTE_RE.match(lines[j]):
                        out.append('\n')
                        i += 1
                    else:
                        break
                else:
                    break
            out.append('```\n')
            continue

        # Single-blockquote lines that look like scripts → code block
        if stripped.startswith('> #!/') or stripped.startswith('> sudo '):
            out.append('```text\n')
            while i < len(lines) and lines[i].rstrip('\n').startswith('> '):
                content = lines[i].rstrip('\n')[2:]  # strip "> " prefix
                out.append(content + '\n')
                i += 1
            out.append('```\n')
            continue

        # Shell prompt lines (# command) after a bold label → code block.
        # After shift_headings, real headings are ## or deeper, so # is always a prompt.
        if stripped.startswith('# ') and not stripped.startswith('## '):
            # shell prompts follow a bold label (ending with trailing spaces) or blank line
            if out and (not out[-1].strip() or out[-1].rstrip('\n').endswith('  ')):
                out.append('```text\n')
                out.append(stripped + '\n')
                i += 1
                out.append('```\n')
                continue

        out.append(line)
        i += 1

    return out


def fix_author_links(lines):
    """Replace pandoc's empty email hyperlinks [](mailto:foo) with plain address."""
    out = []
    for line in lines:
        # [](mailto:addr) , [](mailto:addr2) → addr , addr2
        line = re.sub(r'\[\]\(mailto:([^)]+)\)', r'\1', line)
        out.append(line)
    return out


def process(lines):
    lines = shift_headings(lines)
    lines = unescape_backticks(lines)
    lines = unescape_pandoc(lines)
    lines = remove_html_comments(lines)
    lines = deduplicate_sections(lines)
    lines = clean_trailing_backslashes(lines)
    lines = format_code_blocks(lines)
    lines = fix_bold_punctuation(lines)
    lines = fix_author_links(lines)
    return lines


if __name__ == '__main__':
    sys.stdout.writelines(process(sys.stdin.readlines()))
