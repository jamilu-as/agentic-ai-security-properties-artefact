# E1.3 / E3.2 — analyst materials

Fixed before any analyst sees them. Deployments are described in prose, as a
practitioner would describe a system to a colleague — **not** as tool lists. That
is deliberate: the step under test is the analyst's construction of the capability
manifest from a description, which is where the ambiguity lives. The mapping from
capabilities to properties is code and would return perfect agreement.

---

## Procedure A — capability-derived (the instrument's procedure)

For the deployment described, work in this order:

1. **List the components.** For each, say whether it is an agent, an LLM, a tool, a
   code executor, a datastore, a retrieval store, an external API, a user channel,
   or a skill registry.
2. **List the flows** between components, and say what each carries: data,
   instructions, credentials, or control.
3. **Mark trust.** Which components sit outside the trust boundary, and which
   ingest content the deployment does not control?
4. **Determine reachability.** Starting from anything that ingests untrusted
   content, follow the flows. Which components are reachable?
5. **Assign properties**, using ONLY this fixed vocabulary, and only for
   capabilities that are reachable per step 4:

   | Capability present and reachable | Property at risk |
   |---|---|
   | acts on the world through a tool | tool-call integrity |
   | executes code | execution containment |
   | retains state across sessions | contextual integrity |
   | reaches an irreversible effect | action irreversibility |
   | communicates with peer agents | inter-agent trust |
   | pursues a goal across steps | goal integrity |
   | installs third-party extensions | supply-chain and privilege scoping |
   | retrieves from an indexed store | retrieval integrity |

6. **Assign compositional properties**, only where BOTH capabilities are reachable
   on the same path:

   | Capabilities co-reachable | Compositional property |
   |---|---|
   | acts + retains | cross-session exfiltration |
   | acts + reaches outside | injected irreversible action |
   | executes + pursues goals | lateral execution |
   | installs + reaches outside | load-time privilege escalation |
   | retains + peer agents | trust laundering |

**Output:** the list of properties from step 5, and the list from step 6. Nothing else.

---

## Procedure B — enumerative baseline

Lifted verbatim from MITRE ATLAS (release v2026.07, pinned commit `2306eca`) and
fixed here before any rating, so that the comparator is not authored by the
proponent of the alternative.

For the deployment described, select every ATLAS technique that applies:

`AML.T0051` LLM Prompt Injection · `AML.T0053` AI Agent Tool Invocation ·
`AML.T0099` AI Agent Tool Data Poisoning · `AML.T0067` LLM Trusted Output
Components Manipulation · `AML.T0101` Data Destruction via AI Agent Tool
Invocation · `AML.T0034.002` Agentic Resource Consumption · `AML.T0080` AI Agent
Context Poisoning · `AML.T0080.000` AI Agent Context Poisoning: Memory ·
`AML.T0057` LLM Data Leakage · `AML.T0092` Manipulate User LLM Chat History ·
`AML.T0086` Exfiltration via AI Agent Tool Invocation · `AML.T0108` AI Agent ·
`AML.T0084.003` Discover AI Agent Configuration: Call Chains · `AML.T0103` Deploy
AI Agent · `AML.T0094` Delay Execution of LLM Instructions · `AML.T0061` LLM
Prompt Self-Replication · `AML.T0010.005` AI Supply Chain Compromise: AI Agent
Tool · `AML.T0104` Publish Poisoned AI Agent Tool · `AML.T0110` AI Agent Tool
Poisoning · `AML.T0109` AI Supply Chain Rug Pull · `AML.T0011.002` Poisoned AI
Agent Tool · `AML.T0070` RAG Poisoning · `AML.T0071` False RAG Entry Injection ·
`AML.T0064` Gather RAG-Indexed Targets · `AML.T0082` RAG Credential Harvesting ·
`AML.T0056` Extract LLM System Prompt

**Output:** the list of technique ids that apply. Nothing else.

---

## Deployments

### D1 — Retail banking assistant
An assistant for retail banking customers, reached through the bank's authenticated
mobile app. A customer can ask it to check a balance, review recent transactions,
schedule a payment, or send money to a saved payee. It reads transaction records,
which carry free-text memo fields written by whoever sent the money, and it can
open documents the customer has previously uploaded to their account. It holds no
memory between sessions. Nothing it does is exposed to the public internet.

### D2 — Engineering workspace assistant
An assistant inside a company's internal chat platform. It reads channel messages
and direct messages from any employee, can post replies, add people to channels,
and read a shared document store. Several teams share one deployment. It keeps a
running summary of each channel it participates in so that it can answer questions
about earlier discussion.

### D3 — Travel booking agent
A public-facing agent on a travel company's website. Anyone can use it without an
account. It searches hotels and restaurants, reads listings and customer reviews
written by third parties, compares prices, and can make and cancel reservations
against the user's stored card.

### D4 — Repository maintenance agent
An agent that triages issues and pull requests on a company's code repositories,
including forks and contributions from outside the organisation. It reads issue
text, pull-request descriptions and source diffs, can run the test suite in a
container, post review comments, and merge approved changes. It delegates parts of
larger tasks to worker instances of itself.

### D5 — Procurement assistant
An assistant for a company's purchasing team. It searches supplier catalogues on the
open web, reads product listings and supplier-written specifications, compares
prices, and can place orders against a corporate account. Buyers install optional
connector plug-ins from a marketplace so it can reach additional supplier systems.

### D6 — Personal scheduling assistant
An assistant for one individual. It reads their incoming email, manages their
calendar, drafts and sends replies, and can pay recurring bills from a linked
account. It remembers preferences and past decisions across sessions so that it can
act consistently. It coordinates across email, calendar and payments to complete
multi-step requests.

---

## E3.2 — treatment materials

The same analysts additionally apply the decision rule. Two steps, scored separately
because they are not equally ambiguous: the grading step is close to a lookup and is
expected to agree almost perfectly, which is stated in advance so that a high figure
is not read as evidence of anything. The informative quantity is the second step.

**Step 1 — grade each force.** Lower is better on all three.

| Force | Graded from | strong | moderate | weak |
|---|---|---|---|---|
| Scientific | adaptive lift, pp | < 10 | 10–30 | > 30 |
| Engineering | utility cost, pp | < 5 | 5–15 | > 15 |
| Economic | defender cost per unit attack success averted | < 1× | 1–3× | > 3× |

The economic force does **not** apply where the adversary is not cost-bounded
(nation-state, hacktivist, ideological).

**Step 2 — return one treatment.** `reduce` · `accept` · `transfer` · `avoid`.
Two or more strong readings with no weak reading returns *reduce*. A weak reading on
a force the adversary profile makes decisive returns *accept* where the residual can
be monitored, *transfer* where it can be shifted contractually, and *avoid* where it
can be neither. No force reaching moderate returns *avoid*.

**Profiles to grade** (each with its adversary and residual posture):

| # | Adaptive lift | Utility cost | Cost ratio | Adversary | Residual |
|---|---|---|---|---|---|
| P1 | 6 pp | 3 pp | 0.8× | cost-bounded criminal | monitorable |
| P2 | 34 pp | 4 pp | 0.9× | cost-bounded criminal | monitorable |
| P3 | 12 pp | 18 pp | 3.4× | cost-bounded criminal | neither |
| P4 | 8 pp | 4 pp | 9.1× | nation-state | monitorable |
| P5 | 11 pp | 6 pp | 1.4× | cost-bounded criminal | contractually shiftable |
| P6 | 31 pp | 16 pp | 3.2× | insider | monitorable |
