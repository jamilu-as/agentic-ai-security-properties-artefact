#!/usr/bin/env python3
"""E1.b — does a capability-derived surface discriminate between deployments?

The RQ1 claim in the form a practitioner cares about: an enumerative catalogue
returns the same agentic techniques for any agentic system, because a catalogue
does not know your wiring. A derived surface should return different surfaces for
different architectures, and should identify applicable risk the catalogue does
not carry at all.

Both halves are measured here against six real deployment architectures — the
benchmark suites, each expressed as an architecture from its own tool manifest,
so the derivation sees a deployment rather than a special case.

Run:  python3 work/w1-surface/exp_discrimination.py
"""
import sys, os, re, json, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "instrument"))
ROOT = os.path.dirname(os.path.dirname(HERE))
SUITES_DIR = os.path.join(os.path.dirname(ROOT), "AutoDojo",
                          "agentdojo", "src", "agentdojo", "default_suites", "v1")

from architecture import from_tool_manifest, Environment, Adversary   # noqa: E402
from derivation import derive_from_architecture, atlas_baseline       # noqa: E402
import atlas_map                                                      # noqa: E402

SUITES = ("banking", "slack", "travel", "github", "shopping", "dailylife")


def tool_manifest(suite: str):
    """Read TOOLS from the suite definition, dropping commented-out entries."""
    path = os.path.join(SUITES_DIR, suite, "task_suite.py")
    src = open(path, errors="ignore").read()
    m = re.search(r"TOOLS\s*(?::[^=]*)?=\s*\[(.*?)\]", src, re.S)
    if not m:
        return []
    out = []
    for line in m.group(1).split("\n"):
        line = line.split("#")[0].strip().rstrip(",").strip()
        if line and re.fullmatch(r"[a-z_][a-z0-9_]*", line):
            out.append(line)
    return out


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if (a | b) else 1.0


def main():
    lib = atlas_map.AtlasLibrary()
    audit = atlas_map.validate(lib)
    print("=" * 72)
    print(f"ATLAS {audit['atlas_version']} — {audit['techniques_in_library']} techniques, "
          f"{audit['techniques_referenced']} referenced by the mapping (all validated)")
    print("=" * 72)

    surfaces, manifests = {}, {}
    for s in SUITES:
        tools = tool_manifest(s)
        manifests[s] = tools
        arch = from_tool_manifest(s, tools)
        surfaces[s] = derive_from_architecture(arch, lib)

    print(f"\n{'suite':<11}{'tools':>6}{'reach':>7}{'props':>7}{'comp':>6}{'ATLAS':>7}  properties")
    print("-" * 72)
    for s in SUITES:
        d = surfaces[s]
        props = [p["property"] for p in d["properties"]]
        print(f"{s:<11}{len(manifests[s]):>6}"
              f"{len(d['architecture']['reachable_from_untrusted']):>7}"
              f"{len(props):>7}{len(d['compositional']):>6}{d['n_atlas_techniques']:>7}  "
              f"{', '.join(p.split()[0] for p in props)}")

    # -- discrimination -----------------------------------------------------
    base = set(atlas_baseline(lib))
    print(f"\nENUMERATIVE BASELINE: ATLAS returns the same {len(base)} agentic techniques")
    print("for every one of the six deployments. Pairwise Jaccard = 1.00 by construction.")

    pairs = list(itertools.combinations(SUITES, 2))
    derived_j = [jaccard([p["property"] for p in surfaces[a]["properties"]],
                         [p["property"] for p in surfaces[b]["properties"]]) for a, b in pairs]
    tech_j = [jaccard([t["id"] for p in surfaces[a]["properties"] for t in p["atlas"]],
                      [t["id"] for p in surfaces[b]["properties"] for t in p["atlas"]])
              for a, b in pairs]
    mean = lambda x: sum(x) / len(x)
    distinct = len({tuple(sorted(p["property"] for p in surfaces[s]["properties"])) for s in SUITES})

    print(f"\nDERIVED SURFACE, across {len(pairs)} suite pairs:")
    print(f"  mean Jaccard on properties        {mean(derived_j):.3f}   (1.00 = no discrimination)")
    print(f"  mean Jaccard on ATLAS techniques  {mean(tech_j):.3f}")
    print(f"  distinct surfaces                 {distinct} of {len(SUITES)}")
    print(f"  range                             {min(derived_j):.2f} - {max(derived_j):.2f}")

    # -- residue ------------------------------------------------------------
    cov = atlas_map.coverage_report(lib)
    print(f"\nRESIDUE — applicable risk ATLAS does not carry:")
    print(f"  single-capability properties fully covered   {cov['single_capability_all_covered']}")
    print(f"  compositional properties FULLY covered       {cov['compositional_fully_covered']} "
          f"of {len(cov['compositional'])}")
    print(f"  compositional with no entry at all           {cov['compositional_uncovered']}")
    for name, v in cov["compositional"].items():
        raised = [s for s in SUITES if any(c["property"] == name for c in surfaces[s]["compositional"])]
        if raised:
            mark = "no ATLAS entry" if not v["covered"] else f"partial: {len(v['partial_techniques'])} technique(s)"
            print(f"    {name:<32} raised by {len(raised)}/6 suites — {mark}")

    out = os.path.join(HERE, "discrimination_results.json")
    json.dump({"atlas": audit, "surfaces": surfaces, "coverage": cov,
               "discrimination": {"mean_jaccard_properties": mean(derived_j),
                                  "mean_jaccard_techniques": mean(tech_j),
                                  "distinct_surfaces": distinct,
                                  "n_suites": len(SUITES),
                                  "baseline_techniques": len(base)}},
              open(out, "w"), indent=1)
    print(f"\nwritten: {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
