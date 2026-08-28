import os, re, sys, glob
try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUB = "<!-- STUB -->"

def load(name):
    with open(os.path.join(ROOT, "docs", "canon", name)) as f:
        return yaml.safe_load(f)

def read(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    with open(p, errors="ignore") as f:
        return f.read()

def is_stub(text):
    return text is None or STUB in text or len(text.split()) < 40

def words(text):
    """Prose word count: strips code fences, tables, HTML comments, headings markup."""
    if not text:
        return 0
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"^\s*\|.*$", " ", text, flags=re.M)   # tables
    text = re.sub(r"[#*_>`\[\]()]", " ", text)
    return len([w for w in text.split() if any(c.isalnum() for c in w)])

def dissertation_files():
    return sorted(glob.glob(os.path.join(ROOT, "dissertation", "**", "*.md"), recursive=True))

class Report:
    def __init__(self, name):
        self.name, self.fail, self.warn, self.ok = name, [], [], []
    def F(self, m): self.fail.append(m)
    def W(self, m): self.warn.append(m)
    def O(self, m): self.ok.append(m)
    def emit(self, strict):
        print(f"\n=== {self.name} ===")
        for m in self.ok:   print(f"  ok    {m}")
        for m in self.warn: print(f"  warn  {m}")
        for m in self.fail: print(f"  FAIL  {m}")
        bad = len(self.fail)
        if not strict and bad:
            print(f"  ({bad} failing, advisory mode — not enforced until the gate)")
            return 0
        return 1 if bad else 0
