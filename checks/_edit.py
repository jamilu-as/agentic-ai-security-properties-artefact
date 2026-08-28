"""Text edits that fail loudly.

str.replace() returns the string unchanged when the pattern does not match, so a
mistyped or re-wrapped source string silently does nothing and the edit is
reported as applied. That has now happened twice: a paragraph correction that
never landed because the text used an em-dash where the search used a comma.
Use sub() for every content edit.
"""
def sub(text, old, new, where=""):
    if old not in text:
        raise AssertionError(f"NO MATCH{' in ' + where if where else ''}: {old[:90]!r}")
    return text.replace(old, new, 1)

def subn(text, old, new, n, where=""):
    c = text.count(old)
    if c != n:
        raise AssertionError(f"expected {n} matches, found {c}{' in ' + where if where else ''}: {old[:70]!r}")
    return text.replace(old, new)
