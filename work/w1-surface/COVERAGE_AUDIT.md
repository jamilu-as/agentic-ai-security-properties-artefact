# O2 — benchmark coverage audit

Verification of Paper 1 Table 1, "Capability clusters, the security property each admits, and the first dedicated benchmark that measures it", against the landscape as of 28 August 2026.

The claim under audit in each row is **priority** — first *dedicated* benchmark for that property — not best or most-used.

## Corrected table

| Capability cluster | Derived security property | First dedicated benchmark |
|---|---|---|
| Tools | Tool-call integrity (indirect prompt injection) | **InjecAgent** — Zhan et al., arXiv:2403.02691, 5 Mar 2024; ACL 2024 Findings |
| Code interpreter | Code-execution containment | **RedCode** — Guo et al., arXiv:2411.07781, 12 Nov 2024; NeurIPS 2024 D&B |
| Persistent memory | Cross-session contextual integrity | **CIMemories** — Mireshghallah et al., arXiv:2511.14937, 18 Nov 2025 |
| Actuators | Action reversibility | **None dedicated** — see flag A |
| Peer agents | Agent-to-agent integrity | **TAMAS** — Kavathekar et al., arXiv:2511.05269, 7 Nov 2025; ICML 2025 MAS Workshop |
| Goal structure | Deception under conflict | **AI-LieDar** — Su et al., arXiv:2409.09013, 13 Sep 2024; NAACL 2025 |
| **Extensibility / installable skills** | Skill provenance and privilege integrity | **Skill-Inject** — Schmotz et al., arXiv:2602.20156, 23 Feb 2026 |

Optional eighth row: **Multimodal / perceptual input** → perceptual input integrity → **VPI-Bench** (arXiv:2506.02456, 3 Jun 2025; ICLR 2026). Distinct because the injection arrives through rendered pixels, so text-level provenance and sanitisation defences are structurally unavailable — a different control surface, which is what the viability framework turns on.

## Per-row findings

**Tools — priority reassigned.** AgentDojo is real and correctly described (arXiv:2406.13352, NeurIPS 2024 D&B; 97 tasks, 629 security tests). It is not first. InjecAgent (5 Mar 2024) predates it by three months as the first dedicated IPI benchmark *for tool-integrated agents* — 1,054 cases, 17 user tools, 62 attacker tools. BIPIA (arXiv:2312.14197, 21 Dec 2023, KDD 2025) is first for indirect prompt injection outright, though without a tool-calling loop. AgentDojo's defensible claim is **first executable, extensible environment scoring utility and security jointly**; state it that way. Footnote that InjecAgent simulates tool responses rather than executing them.

**Code interpreter — category error.** CVE-Bench (Zhu et al., arXiv:2503.17332, ICML 2025) measures an agent's ability to *exploit external web applications*; its sandbox is scaffolding for running vulnerable targets, not the object of measurement. It does not measure sandbox integrity. The replacement depends on which property is meant, and the chapter must say: code-execution containment → RedCode (4,050 cases executed in Docker, 25 vulnerability types); sandbox containment → SandboxEval (arXiv:2504.00018, working paper, no venue); escape capability → SandboxEscapeBench (arXiv:2603.02277). CyberSecEval 2 (arXiv:2404.13161, 19 Apr 2024) is April-2024 prior art — a 500-prompt interpreter-abuse suite — but is one of five areas in a wide suite and never executes code, so it measures willingness to write escape code, not containment.

**Persistent memory — property relabelled.** CIMemories is correctly attributed and matches the source's own reference [13]. But it measures **contextual integrity, a privacy property** — whether the model appropriately withholds memory attributes given task context — not integrity under attack. Paper 1's *prose* is already consistent with this; only the table label "cross-session integrity" misleads, since in security usage that reads as memory poisoning. Relabelled above. If the integrity-under-attack reading is wanted instead, it needs a separate row, for which MemEvoBench (arXiv:2604.15774) self-claims first — see flag C.

**Actuators — the weakest cell.** OS-Harm is real and correctly attributed (arXiv:2506.14866, NeurIPS 2025 D&B Spotlight) but its three categories are deliberate user misuse, prompt injection, and model misbehaviour — none of which is action reversibility. ToolEmu was checked directly: it scores likelihood × severity, not reversibility. ST-WebAgentBench has an adjacent "user consent" dimension. No dedicated benchmark for action reversibility was found. **Mark this cell "none dedicated"** — which is now honest, and pairs with the peer-agents correction below. Alternatively restate the property as "computer-use action safety", but then OS-Harm's priority is contestable against SafeAgentBench (arXiv:2412.13178, 17 Dec 2024).

**Peer agents — "none dedicated" is false, and A2ASecBench is not first.** A2ASecBench is confirmed: ICLR 2026, OpenReview `LfdFnakqGJ`, code at github.com/SaFo-Lab/A2ASecBench (MIT), six attack families. **It has no arXiv preprint — cite the ICLR/OpenReview record.** But TAMAS (arXiv:2511.05269, 7 Nov 2025, ICML 2025 MAS Workshop, public from July 2025) covers 6 attack types, 300 adversarial instances, 211 tools, across AutoGen and CrewAI. A2ASecBench's "first" claim holds only in the narrower *protocol-aware* sense. MAGPIE (arXiv:2510.15186) measures multi-agent contextual privacy, not integrity.

**Goal structure — confirmed.** AI-LieDar is first dedicated, and measures exactly the stated property. MACHIAVELLI (arXiv:2304.03279, ICML 2023 Oral) is the one genuine challenger — built on reward-versus-ethics tension, deception named in the abstract — but deception is one of many harm annotations in a general ethics benchmark. Footnote it; a reader in this area will think of it.

**Extensibility / installable skills — new row, recommended.** Distinct from Tools, not a special case: a skill is a third-party bundle of instructions, code and tool permissions loaded on demand, so the threat surface is supply-chain and privilege-scoping, and attacks land at install/load time before any tool call. IPI injects into tool *returns*; skill attacks corrupt the instruction set itself and persist. First dedicated benchmark is Skill-Inject (23 Feb 2026), predating SkillTester (arXiv:2603.28815) and FORTIS (arXiv:2605.09163). The opening attack paper is arXiv:2510.26328 (30 Oct 2025) by the same group — a clean attack→benchmark pairing mirroring Greshake→InjecAgent in the Tools row, which is a usable structural point for the chapter.

**Clusters considered and rejected.** MCP — no row: it is an implementation substrate for the Tools cluster, not a capability an agent has, and adding it breaks the capability-derived logic; make it a footnote noting MCP shifts injection from tool returns to tool descriptors. Browser/web agents — no row: WASP (arXiv:2504.18575) is a deployment surface combining Tools and Actuators. Long-horizon planning and inter-agent economic capability — no dedicated security benchmark found.

## Flags — not established with confidence

- **A. Actuators / action reversibility.** No dedicated benchmark found. Mark, do not assert.
- **B. TAMAS priority over A2ASecBench.** Moderate confidence; rests on the ICML 2025 workshop date. Mid-2025 workshop proceedings were not exhaustively swept.
- **C. MemEvoBench "first" self-claim.** Moderate confidence.
- **D. A2ASecBench author list unconfirmed** — OpenReview served a bot wall. Confirm from the ICLR proceedings PDF before citing.
- **E. CVE-Bench venue (ICML 2025)** rests on an OpenReview listing, not proceedings.
- **F. Method bound.** The audit's search tooling hit a session call cap partway through. Negative results above are "not found after targeted search", not proof of absence, and should be worded that way in the chapter.

## What this establishes for RQ1

Five of six original rows required correction — one false, one a category error, three mis-attributed on priority. Two clusters are added. This is the substance of O2, and it is also evidence for RQ1's central claim: the derivation vocabulary absorbed a capability cluster (installable skills) that did not exist when it was written, without redesign. A cluster that slots in unchanged is stronger evidence that the model derives rather than enumerates than any argument made in prose.
