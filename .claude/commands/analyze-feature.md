Analyze the following feature idea for Mac Eye Control: $ARGUMENTS

---

**Step 1 — Analysis (foreground)**

Launch the `analyst` agent with the feature description above.

The analyst must:
1. Read `CLAUDE.md`, `PRODUCT.md`, and `docs/overview.md`
2. Scan relevant files in `src/` to understand current implementation state
3. Produce a complete feature document saved to `docs/features/<feature-slug>.md`
4. Return a short summary of the document: problem statement, acceptance criteria count, risks found, and whether the feature is ready or blocked

Wait for the analyst to finish before proceeding.

---

**Step 2 — Decision**

After the analyst completes, show the user:

```
Analysis saved to: docs/features/<feature-slug>.md

Summary:
- Problem: <one line>
- Acceptance criteria: <N> items
- Risks identified: <N>
- Status: Ready for Development | Blocked

Proceed with /new-feature using this analysis? (yes / no)
```

If the status is **Blocked**, explain what open questions must be resolved before development can start. Do not offer to launch `/new-feature`.

---

**Step 3 — Launch development (only if user confirms)**

If the user says yes, launch `/new-feature` with the following context:

> Implement the feature described in `docs/features/<feature-slug>.md`. Read that file fully before planning. All acceptance criteria in the document must be met.

This will trigger the full planner → developer → tester pipeline.
