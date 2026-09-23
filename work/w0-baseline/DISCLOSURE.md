# Upstream disclosure: AutoDojo released variant grid

Recorded here: what was disclosed, to whom, by what route, and the text sent. Section 3.13 states
the obligation; Appendix D carries the record.

## Finding

`work/w0-baseline/INTEGRITY_FINDING.md`. Fingerprinting the released variant grid on
generated content gives 13 distinct payloads across 150 shipped cells. For 137 of 150 the
content varies with neither the defence nor the target model. Reproduce with
`work/w0-baseline/fingerprint.py`.

This is a data-quality observation about a public artefact, not a security vulnerability.
No embargo applies. The authors should see it before the dissertation is submitted.

## Recipients

Authors of arXiv:2606.15057: Xinhang Ma, Taoran Li, Chaowei Xiao, Zhiyuan Yu, Ning Zhang,
Yevgeniy Vorobeychik.

## Route

Email the corresponding author, copying the co-authors. If there is no acknowledgement in
fourteen days, open an issue on `xhOwenMa/AutoDojo` with the same text.

## Message sent

> **Subject:** Duplication in the released AutoDojo variant grid
>
> Dear Dr Ma,
>
> I am an MSc student at the University of West London. My dissertation uses AutoDojo as
> distributed, pinned at `abbcbd8`, and cites your paper as its adaptive-evaluation baseline.
> While building a baseline from the released grid I found something you may want to check.
>
> Fingerprinting each cell of
> `variant_generation/variants/{suite}/{provider}/{model}/{defense}/injections.json` on
> generated content only (the `variants` arrays and `trajectory` texts, excluding metadata)
> gives 13 distinct payloads across the 150 shipped cells. Collapsing only the defence
> dimension gives 51 of 150.
>
> Per suite, holding the target model fixed across the ten defence directories:
>
> | Suite | Distinct payloads per model |
> |---|---|
> | banking | 5, 6, 6, 7, 7 |
> | slack | 3, 3, 3, 3, 3 |
> | travel | 1, 1, 1, 1, 1 |
>
> For all five travel models, the ten defence directories are byte-identical in content. The
> `no_defense` directory is included, though its metadata correctly records
> `defense_run: False`.
>
> This reproduces it against a clean clone, run from the repository root:
>
> ```python
> import json, hashlib
> from pathlib import Path
> from collections import defaultdict
>
> R = Path("agentdojo/variant_generation/variants")
>
> def fp(path):
>     d = json.load(open(path))
>     blob = [json.dumps({"v": vd.get("variants"),
>                         "t": [s.get("text") for s in (vd.get("trajectory") or [])]},
>                        sort_keys=True)
>             for _, vecs in sorted((d.get("injection_tasks") or {}).items())
>             for _, vd in sorted(vecs.items())]
>     return hashlib.sha256("".join(blob).encode()).hexdigest()[:12]
>
> cells = {}
> for f in sorted(R.rglob("injections.json")):
>     q = f.relative_to(R).parts
>     if len(q) == 5:
>         cells[(q[0], q[2], q[3])] = fp(f)          # suite, target model, defence
>
> per = defaultdict(set)
> for (s, m, _), h in cells.items():
>     per[(s, m)].add(h)
> for k in sorted(per):
>     print(f"{k[0]:8} {k[1]:24} {len(per[k])} distinct across 10 defence dirs")
> print(len(set(cells.values())), "distinct payloads across", len(cells), "shipped cells")
> ```
>
> It hashes the `variants` arrays and the trajectory texts only, so two cells match only if
> the optimiser produced identical output.
>
> This shows the released injections are not defence-specific in those cells. It does not
> show the reported numbers are wrong: the caches hold attack strings, and the benchmark
> applies defences at evaluation time, so defence-specific ASRs can still be measured from a
> non-defence-specific attack. I cannot tell from the repository whether the published tables
> came from these caches or from a separate run, and I have not assumed either.
>
> Possible causes I considered, none confirmed: cells seeded then skipped by `--use-cache`, a
> packaging error in the release, or defence conditioning inactive for two of three suites.
>
> My dissertation reports this as a constraint on my own baseline, which I restrict to
> distinct payloads, and states that it does not establish an error in your results. If there
> is context I have missed, or you would like to correct the release, I will record your
> response. I submit on 20 September 2026. I am happy to send the full write-up, with the
> metadata comparison and the candidate mechanisms, if it is useful.
>
> Thank you for releasing the harness.
>
> Jamilu Abdullahi
> MSc Cyber Security, University of West London

## Attachments

None. The reproduction is inline in the message body: a script attachment is commonly
stripped by mail filters, and the artefact repository stays private until this is sent, so a
link would not resolve either. `INTEGRITY_FINDING.md` goes only if they ask.

## Record

Register item P46 matches a phrase belonging only to a completed record. It stayed failing
while this was a draft, and passes now because the first row carries the date. While drafting,
the phrase had to be kept out of the rest of the file: a draft using it in passing turned the
check green with the disclosure still unsent, which is how it read for one commit on
29 August 2026.

| | |
|---|---|
| Disclosed on | 30 August 2026 |
| Route | email to the authors of arXiv:2606.15057 |
| Recipients | Xinhang Ma, Taoran Li, Chaowei Xiao, Zhiyuan Yu, Ning Zhang, Yevgeniy Vorobeychik |
| Response | none at the time of writing |
| Substance | — |
| Escalation | GitHub issue on `xhOwenMa/AutoDojo` if unacknowledged by 13 September 2026 |
| Reflected at | Section 3.13, Section 4.II.a, Section 5.2, Section 5.4, Appendix D |
| Correction | the message as sent signed off "MSc Cyber Security"; the programme is MSc Artificial Intelligence. Recorded here rather than silently corrected above, since the text above is what the recipients received. |

## Response — 4 September 2026

The first author (Xinhang Ma) replied by email on 4 September 2026. Paraphrase of the reply,
kept beside the message it answers:

- The caches' metadata are misleading: the cache was reorganised for the public release of
  AutoDojo with a script that assigns cache-specific metadata.
- Many cells in the reported numbers are transfer attacks rather than (model, defence)
  optimised attacks. Transfer was used for cost, and because injections optimised against
  PIGuard or the data filter usually, though not always, find good injections against other
  defences.
- Running the optimiser against a new defence is fully supported by the optimize script.
  Numbers cited from the grid should note that transfer can still be effective.
- A follow-up with specifically optimised injections is in progress and, as expected, finds
  them more effective; the full set of (model, defence) optimised injections will not be
  released before this dissertation's submission date.

Effect on the dissertation: Section 4.II.a now states the mechanism as confirmed; Section 4.II.c notes that
Table 4.6's ceilings are computed on transfer-attack rates; Appendix D records the response.
