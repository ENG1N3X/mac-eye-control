Implement the following new feature for Mac Eye Control: $ARGUMENTS

Follow this exact workflow:

---

**Step 1 — Planning (foreground, wait for completion)**

Use the `planner` agent to produce a detailed implementation plan for the feature described above.
The planner must read `CLAUDE.md` and `PRODUCT.md` before producing the plan.
Wait for the plan to complete. Save the full plan text — you will pass it verbatim to the developer and tester agents in the next steps.

---

**Step 2 — Development (foreground, wait for completion)**

Launch the `developer` agent in **foreground** mode. Pass the complete plan from Step 1 in full — do not summarize it.
Wait for the developer to finish before proceeding to Step 3.

---

**Step 3 — Testing (foreground, wait for completion)**

Launch the `tester` agent in **foreground** mode. Pass:
1. The complete plan from Step 1 (in full)
2. The list of files created or modified by the developer in Step 2

The tester must write tests in `tests/`, run them, and report results.

---

**Step 4 — Report**

Summarize:
- What was implemented (files created/modified)
- Test results (passed / failed / errors)
- Any bugs found by the tester
- Any open questions or blockers

If the tester found bugs, launch the `developer` agent again (foreground) with the exact bug report, then re-run the `tester` agent (foreground) to confirm fixes.
