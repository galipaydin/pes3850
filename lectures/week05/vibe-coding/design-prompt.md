# Prompt — have the agent write the design document

*Step 2 of the roadmap. Same folder, agent in **Planning** mode, a new conversation.*

## Before you paste it: approve the PRD

The PRD the agent wrote is a draft. Check four things, have the agent fix them, then commit `docs/PRD.md`.
From now on it is the single source of truth: if an idea changes, the PRD changes first.

- **Out of scope is explicit.** The three later analysis tabs are listed there.
- **Acceptance criteria can be tested by hand.** "The user uploads a file easily" cannot.
  "A file over 50 MB shows an error message" can.
- **No technical design has leaked in.** Database tables or API addresses belong in the next step.
- **The open questions are answered.** An unanswered question gets filled in by guesswork during design.

## The prompt

```text
Read docs/PRD.md. It is approved. Now we write the design document: HOW the MVP
will work. Do NOT write any code and do NOT create the project yet.

## How we will work
1. For every decision that has real alternatives, give me 2-3 options in a short
   table (option, pros, cons, your recommendation), one decision at a time, and
   wait for my choice. Decisions to cover at least:
   - authentication (email + password; no third-party service may see user data),
   - how login sessions are kept,
   - how the Next.js app and the Python service talk to each other,
   - which part reads one page of rows from a file: the Next.js app or the
     Python service.
2. Already decided, do not ask about them: Next.js with shadcn/ui, SQLite,
   uploaded files on the local file system, the Python service (FastAPI +
   scikit-learn), and server-side pagination of every table view, uploaded or
   generated, at most 50 rows per page. Everything in the PRD's Constraints
   section is final.
3. Prefer the simplest option that meets the PRD. Everything must run on one
   laptop with two commands. No Docker, no cloud services, unless I ask.
4. When all decisions are made, write docs/DESIGN.md.

## DESIGN.md must contain
1. Overview: one diagram (ASCII is fine) of the browser, the Next.js app,
   the Python service and where data is stored.
2. Screens and flow: every page in the MVP, a simple ASCII wireframe of each,
   and how the user moves between them.
3. Data model: the entities (user, file, ...) and their fields.
4. API between Next.js and Python: each endpoint with an example request and
   an example JSON response, for "Know your data", "Predict a risk" and reading
   one page of a table (page number, page size, total rows).
5. Guardrails: where each one is computed and what the user sees when it fires.
6. Security and privacy: password storage, file type and size checks,
   what happens to athlete data.
7. Error handling: what the user sees when an upload fails, a column is
   missing, or the Python service is down.
8. Testing: which tests prove the PRD's acceptance criteria.
9. Folder structure for both parts of the project.
10. Decision log: each decision, the options considered, the choice, and why.

Plain language, no code except the example JSON, about 4 pages.
```

## Why the prompt is built this way

- **Options, then wait.** The agent does not make the technical decisions. It lays out the options and the student
  chooses: *the AI proposes, a person decides and writes down why.*
- **The decision log.** Three weeks later, when someone asks "why SQLite?", the answer is written down.
- **Example API requests and responses.** The contract between the Next.js app and the Python service, so the two
  halves fit when they are built separately.
- **"One laptop, two commands."** Agents like to add Docker and cloud services. This line stops that at the start.
- **Testing is tied to the PRD.** Every acceptance criterion gets a test that proves it.

Commit `docs/DESIGN.md` when you have read and approved it. Next: `plan-prompt.md`.
