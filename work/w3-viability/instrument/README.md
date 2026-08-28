# Viability decision instrument (O6)

Takes a control's **measured viability profile** — adaptive lift, utility cost, defender
cost per unit of attack success averted — together with an **adversary profile** from the
RQ1 derivation, and returns:

- one of the four ISO 31000 treatments: reduce, accept, transfer, avoid;
- the **margin** by which the decision was made — how far the profile sits from the nearest
  boundary;
- whether the decision is **stable** under the measurement uncertainty in its own inputs,
  by propagating the bootstrap distributions from the composition study.

The third output is what distinguishes this from a framework diagram. Every input is an
estimate with an interval, and a rule that flips on noise cannot be used by a practitioner
however sound its reasoning. Controls whose treatment is not invariant across resamples are
returned as **undetermined at this measurement precision** rather than assigned a treatment
the data will not support.

That also makes the framework falsifiable in a way a prose rule is not: determinacy,
ordering validity and stability are all measurable, and the instrument is what makes them
measurable on inputs it did not choose.

## Running it

```python
from viability import Profile, Adversary, decide, stability

d = decide(Profile(adaptive_lift=6.0, utility_cost=3.0, cost_ratio=0.8),
           Adversary("criminal", "commodity", budget_bound=True))
d.treatment        # reduce | accept | transfer | avoid
d.margin           # distance to the nearest boundary, per force
d.forces_applied   # economic drops out for an unbounded adversary

stability(bootstrap_profiles, adversary)   # -> 'undetermined' if it flips on noise
```

Cut-points are those fixed in `preregistration/PREREGISTRATION.md` §9 and are not
tunable here: a rule whose thresholds move after seeing data is not a rule.

Tests: `python3 work/tests/test_instruments.py`.
