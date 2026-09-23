#!/usr/bin/env python3
"""Does the spotlighting marker CAUSE the detector to drop a sentence, or does the
sentence go for its content and the marker with it? Section 4.II.b's stated mechanism
("the markers are not sentences and do not survive it") is an inference; this tests it.

Takes the tool messages the spotlighting cell actually produced (every one delimited),
classifies each with the pre-registered detector as delivered and again with the
<< >> markers stripped, and reports whether the detector's verdict changes. Runs the
PIGuard checkpoint locally; no API.

    python marker_test.py --logdir ../../results/runs/redaction_logs
"""
import argparse, json, os, re, sys
from pathlib import Path


def tool_texts(logdir: Path, cell: str):
    for f in sorted(logdir.rglob(f"*/{cell}/*/*/*/*.json")):
        d = json.loads(f.read_text())
        for m in d.get("messages", []):
            if m.get("role") != "tool":
                continue
            for b in m.get("content") or []:
                if b.get("type") == "text" and b.get("content", "").strip():
                    yield b["content"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logdir", default="../../results/runs/redaction_logs")
    ap.add_argument("--out", default="../../results/runs/marker_test.json")
    args = ap.parse_args()
    harness = Path(os.getenv("AUTODOJO_PATH", Path.home() / "research/ResearchMethods/AutoDojo"))
    sys.path.insert(0, str(harness / "agentdojo" / "src"))
    from agentdojo.agent_pipeline.agent_pipeline import CONFIGS_DIR
    from agentdojo.agent_pipeline.defense_filter import DefenseWrapper
    wrapper = DefenseWrapper(os.path.join(CONFIGS_DIR, "piguard.yaml"))

    texts = list(tool_texts(Path(args.logdir), "spotlighting"))
    strip = lambda t: re.sub(r"^<<|>>$", "", t.strip())
    rows = []
    for t in texts:
        with_m, meta_m = wrapper.apply(t, instruction=None)
        bare = strip(t)
        without, meta_b = wrapper.apply(bare, instruction=None)
        rows.append({"delimited_changed": with_m != t or bool(meta_m.get("blocked")),
                     "bare_changed": without != bare or bool(meta_b.get("blocked")),
                     "marker_survives_delimited": with_m.strip().startswith("<<") and with_m.strip().endswith(">>")})
    n = len(rows)
    summary = {
        "messages": n,
        "detector_altered_delimited_text": sum(r["delimited_changed"] for r in rows),
        "detector_altered_bare_text": sum(r["bare_changed"] for r in rows),
        "altered_only_when_delimited": sum(r["delimited_changed"] and not r["bare_changed"] for r in rows),
        "altered_only_when_bare": sum(r["bare_changed"] and not r["delimited_changed"] for r in rows),
        "markers_survive_filter": sum(r["marker_survives_delimited"] for r in rows),
    }
    print(json.dumps(summary, indent=2))
    Path(args.out).write_text(json.dumps({"summary": summary, "rows": rows}, indent=2) + "\n")


if __name__ == "__main__":
    main()
