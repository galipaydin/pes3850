# Prompt — have the agent draft the rules file

*Step 4 of the roadmap. The rules file holds what the agent forgets between conversations. It reads it at the
start of every one.*

```text
Read docs/PRD.md, docs/DESIGN.md and docs/PLAN.md. Draft AGENTS.md: the rules
every agent must follow in this project. Keep it under one page. Include:
- what the project is, in two sentences, with links to the three documents;
- the technologies and their versions, and "do not add a library without asking me";
- how to run both parts and the tests: the exact commands;
- the working loop: one task from PLAN.md at a time; write a plan first;
  run the tests after every change; never start the next task while a test fails;
- never: build anything outside the MVP scope, send athlete data to a third-party
  service, put passwords or keys in the code, delete or rewrite docs/ without asking;
- when a decision changes, update PRD.md or DESIGN.md first, then the code.
Show me the draft before you save it.
```

## Then edit it yourself

The agent drafts it; **you** own it. Read every line and ask: would I be annoyed if the agent broke this rule?
If not, delete the line. A short file that is obeyed beats a long one that is skimmed.

Add a line every time the agent makes the same mistake twice. That is how the file grows.

**Where the file lives.** Many agents read `AGENTS.md` at the project root. Antigravity also has workspace rules in
its settings. Check which one your version reads, and keep a single copy of the rules.

A real example: this course's own repository has a `CLAUDE.md` with the rules for keeping two computers and GitHub
in step. It is short, and every line in it is there because something once went wrong.

Next: step 5, the skeleton. Start task 1 from `docs/PLAN.md`, run it, and make the first git commit.
