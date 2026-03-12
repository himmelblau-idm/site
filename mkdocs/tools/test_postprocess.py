#!/usr/bin/env python3
"""Tests for postprocess.py man page transforms."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import postprocess as pp


# --- shift_headings ---

def test_shift_h1_to_h2():
    assert pp.shift_headings(['# Title\n']) == ['## Title\n']

def test_shift_h2_to_h3():
    assert pp.shift_headings(['## Section\n']) == ['### Section\n']

def test_shift_leaves_plain_text():
    assert pp.shift_headings(['plain text\n']) == ['plain text\n']

def test_shift_skips_fenced_code():
    lines = ['```\n', '# not a heading\n', '```\n']
    assert pp.shift_headings(lines) == lines


# --- unescape_backticks ---

def test_unescape_paired_backticks():
    assert pp.unescape_backticks(['\\`code\\`\n']) == ['`code`\n']

def test_unescape_lone_backtick():
    assert pp.unescape_backticks(['a \\` b\n']) == ['a ` b\n']

def test_unescape_backticks_skips_fence():
    lines = ['```\n', '\\`keep\\`\n', '```\n']
    assert pp.unescape_backticks(lines) == lines


# --- unescape_pandoc ---

def test_unescape_angle_brackets():
    assert pp.unescape_pandoc(['\\<tag\\>\n']) == ['<tag>\n']

def test_unescape_square_brackets():
    assert pp.unescape_pandoc(['\\[arr\\]\n']) == ['[arr]\n']

def test_unescape_hash():
    assert pp.unescape_pandoc(['\\# comment\n']) == ['# comment\n']

def test_unescape_numbered_list():
    assert pp.unescape_pandoc(['1\\. item\n']) == ['1. item\n']

def test_unescape_dash():
    assert pp.unescape_pandoc(['\\- item\n']) == ['- item\n']


# --- deduplicate_sections ---

def test_dedup_removes_second_synopsis():
    lines = ['## SYNOPSIS\n', 'first\n', '## SYNOPSIS\n', 'second\n', '## OTHER\n']
    result = pp.deduplicate_sections(lines)
    assert result.count('## SYNOPSIS\n') == 1
    assert 'first\n' in result
    assert 'second\n' not in result


# --- format_code_blocks: shell prompt handler (Bug 1 regression) ---

def test_shell_prompt_single_line():
    """Single shell prompt line after blank produces a code block."""
    lines = ['\n', '# sudo reboot\n', '\n']
    result = pp.format_code_blocks(lines)
    assert '```text\n' in result
    assert '# sudo reboot\n' in result

def test_shell_prompt_collects_continuation_lines():
    """Shell prompt followed by non-blank lines collects all into one block."""
    lines = [
        '\n',
        '# Example entries:\n',
        '# user:name@domain\n',
        'alice:alice@example.com\n',
        'bob:bob@example.com\n',
        '\n',
    ]
    result = pp.format_code_blocks(lines)
    text_start = result.index('```text\n')
    text_end = result.index('```\n', text_start + 1)
    block = result[text_start + 1:text_end]
    assert '# Example entries:\n' in block
    assert '# user:name@domain\n' in block
    assert 'alice:alice@example.com\n' in block
    assert 'bob:bob@example.com\n' in block

def test_shell_prompt_stops_at_blank():
    """Continuation stops at blank line — next paragraph not swallowed."""
    lines = ['\n', '# prompt\n', '\n', 'next paragraph\n']
    result = pp.format_code_blocks(lines)
    text_start = result.index('```text\n')
    text_end = result.index('```\n', text_start + 1)
    block = result[text_start + 1:text_end]
    assert 'next paragraph\n' not in block

def test_shell_prompt_stops_at_heading():
    """Continuation stops at heading."""
    lines = ['\n', '# prompt\n', '## Next Section\n']
    result = pp.format_code_blocks(lines)
    text_start = result.index('```text\n')
    text_end = result.index('```\n', text_start + 1)
    block = result[text_start + 1:text_end]
    assert '## Next Section\n' not in block


# --- format_code_blocks: INI section handler (Bug 2 regression) ---

def test_ini_section_becomes_code_block():
    """INI [section] followed by params becomes a single code block."""
    lines = [
        '\n',
        '[offline_breakglass]\n',
        'enabled = true\n',
        'ttl = 2h\n',
        '# Allow offline for 2 hours\n',
        '\n',
    ]
    result = pp.format_code_blocks(lines)
    text_start = result.index('```text\n')
    text_end = result.index('```\n', text_start + 1)
    block = result[text_start + 1:text_end]
    assert '[offline_breakglass]\n' in block
    assert 'enabled = true\n' in block
    assert 'ttl = 2h\n' in block
    assert '# Allow offline for 2 hours\n' in block

def test_ini_section_with_trailing_spaces():
    """INI [section] with trailing spaces (pandoc line breaks) still detected."""
    lines = [
        '\n',
        '[global]  \n',
        'domain = example.com  \n',
        '\n',
    ]
    result = pp.format_code_blocks(lines)
    assert '```text\n' in result
    text_start = result.index('```text\n')
    text_end = result.index('```\n', text_start + 1)
    block = result[text_start + 1:text_end]
    assert '[global]  \n' in block
    assert 'domain = example.com  \n' in block

def test_ini_section_stops_at_blank():
    """INI block collection stops at blank line."""
    lines = [
        '\n',
        '[section]\n',
        'key = val\n',
        '\n',
        'Next paragraph.\n',
    ]
    result = pp.format_code_blocks(lines)
    text_start = result.index('```text\n')
    text_end = result.index('```\n', text_start + 1)
    block = result[text_start + 1:text_end]
    assert 'Next paragraph.\n' not in block

def test_ini_section_not_after_text():
    """INI [section] not preceded by blank line is left as-is."""
    lines = [
        'Some text.\n',
        '[section]\n',
        'key = val\n',
        '\n',
    ]
    result = pp.format_code_blocks(lines)
    # Should NOT be wrapped in a code block
    assert '[section]\n' in result
    assert '```text\n' not in result


# --- format_code_blocks: config example lines ---

def test_config_example():
    lines = ['\n', 'domain = example.com\n', '\n']
    result = pp.format_code_blocks(lines)
    assert '```text\n' in result
    assert 'domain = example.com\n' in result


# --- format_code_blocks: double blockquote ---

def test_double_blockquote():
    lines = ['> > sudo reboot\n', '> > echo done\n', '\n']
    result = pp.format_code_blocks(lines)
    assert '```text\n' in result
    assert 'sudo reboot\n' in result
    assert 'echo done\n' in result


# --- rename_subcommand_headings ---

def test_rename_subcommand():
    lines = [
        '## SUBCOMMAND\n',
        '\n',
        '```text\n',
        'aad-tool auth-test [OPTIONS]\n',
        '```\n',
    ]
    result = pp.rename_subcommand_headings(lines)
    assert result[0] == '## aad-tool auth-test\n'

def test_preserves_non_subcommand():
    lines = ['## OPTIONS\n', '\n']
    result = pp.rename_subcommand_headings(lines)
    assert result[0] == '## OPTIONS\n'


# --- convert_see_also_links ---

def test_see_also_bold_to_link():
    lines = ['## SEE ALSO\n', '\n', '**himmelblaud(8)**\n']
    result = pp.convert_see_also_links(lines)
    assert '[himmelblaud(8)](himmelblaud.md)' in result[-1]

def test_see_also_no_conversion_outside():
    lines = ['## DESCRIPTION\n', '\n', '**himmelblaud(8)**\n']
    result = pp.convert_see_also_links(lines)
    assert '**himmelblaud(8)**' in result[-1]


# --- convert_admonitions ---

def test_note_admonition():
    lines = ['### **Note:** Important info\n']
    result = pp.convert_admonitions(lines)
    assert result[0] == '!!! note\n'
    assert result[1] == '    Important info\n'


# --- fix_author_links ---

def test_mailto_link():
    lines = ['[](mailto:user@example.com)\n']
    result = pp.fix_author_links(lines)
    assert result[0] == 'user@example.com\n'


# --- full pipeline ---

def test_process_ini_config_end_to_end():
    """Full pipeline wraps INI config blocks in code fences."""
    lines = [
        '# DESCRIPTION\n',
        '\n',
        'Some text.\n',
        '\n',
        '[global]\n',
        'domain = example.com\n',
        '\n',
    ]
    result = pp.process(lines)
    text = ''.join(result)
    assert '```text' in text
    assert '[global]' in text
    assert 'domain = example.com' in text
