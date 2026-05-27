# End of Phase Procedure

When instructed to run the end-of-phase procedure, execute the following steps
in order without skipping any. Do not ask for confirmation between steps.

---

## Required Parameters (always provided by user)

- `{PHASE_NAME}` — name of the phase just completed (e.g. "EDA", "Feature Engineering")
- `{CURRENT_BRANCH}` — the branch we are on now (e.g. `phase/2-eda`)
- `{NEXT_PHASE_NAME}` — name of the next phase (e.g. "Feature Engineering")
- `{NEXT_BRANCH}` — the branch to create next (e.g. `phase/3-feature-engineering`)

---

## Step 1 — Update CHANGELOG.md

- Add a new entry at the top of the file with today's date
- List every action taken in this phase (what was built, what was run)
- List every decision made and the reason behind it
- List anything explicitly decided NOT to do and why
- List any open questions or TODOs for the next phase

Format:
```
## [YYYY-MM-DD] — {PHASE_NAME} Phase Complete

### Done
- ...

### Decisions
- Finding: ... → Decision: ...

### Deferred / Not Done
- ...

### Open Questions for Next Phase
- ...
```

---

## Step 2 — Update CLAUDE.md

- Find the section that corresponds to the completed phase
- Fill in all findings, decisions, and rules that came out of this phase
- If the section does not exist, create it
- Be concise — decisions and rules only, no analysis or charts
- Any rule written here is treated as a constraint for all future phases

---

## Step 3 — Git Commit

```bash
git add .
git commit -m "feat: complete {PHASE_NAME} phase"
```

---

## Step 4 — Push Current Branch

```bash
git push origin {CURRENT_BRANCH}
```

---

## Step 5 — Merge into Main

```bash
git checkout main
git merge {CURRENT_BRANCH} --no-ff -m "merge: {CURRENT_BRANCH} into main"
git push origin main
```

---

## Step 6 — Create Next Branch

```bash
git checkout -b {NEXT_BRANCH}
git push -u origin {NEXT_BRANCH}
```

---

## Step 7 — Confirm & Summarize

Print the following confirmation:

```
✅ Phase {PHASE_NAME} complete.

CHANGELOG.md → updated
CLAUDE.md    → updated
Branch merged: {CURRENT_BRANCH} → main
Now on branch: {NEXT_BRANCH}

Key decisions recorded:
- [list the 3-5 most important decisions from this phase]

Next phase: {NEXT_PHASE_NAME}
First task: [state the first concrete action of the next phase based on CLAUDE.md]
```

---

## How to Invoke This Procedure

At the end of any phase, say:

> "Follow `scripts/end_of_phase.md`.
> Phase: EDA.
> Current branch: `phase/2-eda`.
> Next phase: Feature Engineering.
> Next branch: `phase/3-feature-engineering`."
