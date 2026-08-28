# Budget options

Computed by `plan/budget_options.py` from the same measured base as the cost
model: 265 agent episodes per (cell, injection task), read off the released
AutoDojo grid. Baseline **519,400 episodes, $6,570** (+25% contingency = $8,213).

Levers are ranked by **scientific cost**, not by saving. A cheaper study that
cannot answer its own question is not a saving.

| Lever | Saves | Left | Severity |
|---|---|---|---|
| Substitute the frontier arm for mid-tier | $1,840 | $4,731 | 2 |
| Five model arms to three | $2,628 | $3,942 | 3 |
| Four seed styles to the strongest per defence | $2,316 | $4,254 | 3 |
| Six suites back to four | $2,950 | $3,620 | 4 |
| Attacker five rounds to three | $1,393 | $5,177 | **5 — do not** |

## Combinations

| | Episodes | With contingency | Saves |
|---|---|---|---|
| **A** frontier substitution only | 519,400 | **$5,913** | $1,840 |
| **B** frontier + three arms | 311,640 | **$3,548** | $3,732 |
| **C** frontier + single seed style | 336,311 | **$3,829** | $3,507 |
| **D** frontier + three arms + single seed | 201,786 | **$2,297** | $4,733 |
| **E** everything except the attacker | 111,188 | **$1,266** | $5,558 |

## Recommendation: B

It keeps the three things the questions actually rest on.

**All six suites.** RQ1 is now the stronger of the two analytic questions, and
suites are its deployments — the discrimination test is over six architectures,
and cutting to four costs two of them. It also keeps the cluster count at 49
rather than dropping to 27, below the range where cluster-robust variance is
anti-conservative.

**All four seed styles.** R1 is the published-attack lower bound and feeds the
adaptive lift, which is RQ3's scientific force. A one-seed baseline is noisier in
the quantity RQ3 grades on.

**The full attacker.** Cutting rounds is the one lever that biases the study
toward its own refutation branch, and it risks failing the adequacy precondition
outright — which makes an arm uninterpretable rather than merely cheaper. It saves
the least of any lever and costs the most. It is on the list only so that it is
visibly rejected.

What B gives up is generalisation across models: composition tested on three
configurations rather than five, with sign consistency read over three arms. That
is the most declarable of the available concessions, because it bounds the scope
of the claim without weakening the measurement inside that scope.

**D is the fallback** if $3,548 is still too much — it adds the seed-style cut,
and the declaration is that R1 rests on the strongest published bypass per defence
rather than four styles, which still satisfies the §2.4 criterion as written.

## Note on where the money is

The GPU arm is $156 of the total. Cutting local compute saves nothing; the API
arms are the entire cost. That is also why substituting the frontier model is the
cheapest first move — one arm carries a large share of the price.
