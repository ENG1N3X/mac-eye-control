Implement the following new feature for Mac Eye Control: $ARGUMENTS

Follow this exact workflow:

---

**Step 1 — Planning (run first, foreground)**

Use the `planner` agent to produce a detailed implementation plan for the feature described above.
The planner must read `CLAUDE.md` and `PRODUCT.md` before producing the plan.
Wait for the plan to complete before proceeding.

---

**Step 2 — Development + Test planning (run in parallel)**

Once the plan is ready, launch two agents simultaneously in a single message:

1. `developer` agent — implement the feature following the plan exactly, adhering to all rules in `CLAUDE.md`
2. `tester` agent — based on the same plan, prepare the test suite: write tests in `tests/`, then run them against the developer's implementation once it lands

Run both agents in **background** mode so they work in parallel.

---

**Step 3 — Report**

Once both agents complete, summarize:
- What was implemented (files created/modified)
- Test results (passed / failed)
- Any bugs found by the tester
- Any open questions or blockers

If the tester found bugs, launch the `developer` agent again with the bug report to fix them, then re-run the `tester` agent.
