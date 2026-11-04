# Prompt — have the agent write the plan

*Step 3 of the roadmap. Same folder, agent in **Planning** mode, a new conversation.*

```text
Read docs/PRD.md and docs/DESIGN.md. Both are approved. Do NOT write any code yet.
Break the MVP into 8-10 tasks and write them to docs/PLAN.md.

Rules for the tasks:
- Each task is a thin end-to-end slice the user can see and test, e.g.
  "upload a CSV and list it in the file explorer", not a layer such as
  "set up the database".
- Task 1 is the skeleton: both parts run, one page says hello, nothing else.
- Order the tasks so the app still works after every one of them.
- For each task write: the goal, the PRD acceptance criteria it covers,
  the files it will create or change, and how I can test it by hand
  in under 5 minutes.
- Leave out anything that is not in the PRD's MVP scope, and say what you left out.

Then stop and wait. I will review the plan before any code is written.
```

## What to look for before you approve it

- **Slices, not layers.** "Build the API", "build the UI" are layers: nothing works until all of them are done.
  "Log in and see an empty dashboard" is a slice: it works on its own.
- **Task 1 is boring on purpose.** A skeleton that runs is step 5 of the roadmap: after it, make the first git commit.
- **Every task can be tested in five minutes.** If a task cannot, it is too big: ask for it to be split.
- **Every PRD acceptance criterion appears in some task.** A criterion that appears nowhere will not get built.

In Antigravity, the agent will still write its own implementation plan and task list *for each task* when you start
it. PLAN.md is the map of the whole project; those are the directions for one step.

Commit `docs/PLAN.md` when you have approved it. Next: `rules-prompt.md`.
