# Prompt — have the agent write the PRD

*Step 1 of the roadmap. Open an empty folder in Antigravity, start the agent in **Planning** mode, and paste
everything inside the box below. Put the problem statement (`problem-statement.md`) between `<<<` and `>>>`.*

```text
You are helping me write a Product Requirements Document (PRD) for a new web app.
Do NOT write any code, do NOT create the project, and do NOT design the architecture yet.
Your only output in this conversation is a PRD.

## Problem statement
<<<
paste the problem statement here
>>>

## How we will work
1. First, interview me. Ask me questions in rounds of at most 5, numbered, and wait
   for my answers before the next round. Ask about users, their goals, what "done"
   looks like, what must NOT be in the first version, data privacy, and anything
   in my requirements below that is vague or contradictory.
2. When you have enough information, tell me "I am ready to write the PRD" and
   summarise the decisions in 5-10 bullets. Wait for my OK.
3. Then write the PRD to docs/PRD.md.

## What I already know I want
- Login with email and password.
- Settings page with two tabs:
  - Profile: personal details and password change.
  - Appearance: font choice and theme (light / dark / system).
- Data management page that works like a file explorer:
  - upload CSV and Excel (.xlsx) files,
  - click a file to view it as a spreadsheet,
  - delete files.
- Every table view, of an uploaded file or of a file the app generates (for example
  analysis results), is paginated on the server: at most 50 rows per page. The
  browser never loads a whole file.
- Analysis page: pick an uploaded file, then choose a QUESTION, not an algorithm.
  One tab per question:
  - Know your data (types, missing values, outliers, distributions, correlations)
  - Predict a number (e.g. sprint time) - regression
  - Predict a risk or category (e.g. injury) - classification
  - Find groups (athlete profiles) - clustering
  - Over time (training load, ACWR, trends per athlete)
  The app suggests suitable methods for the chosen target column and explains why;
  the user can override the suggestion.
- Guardrails on every analysis:
  - always show a simple baseline next to the model,
  - if there is an athlete ID column, split by athlete, and say so,
  - warn about columns that may leak the outcome,
  - for rare outcomes hide accuracy and show PR-AUC,
  - warn when the test set is too small to trust.

## Decisions already made
These are final. Do not ask me about them; record them under Constraints.
- Frontend: Next.js with shadcn/ui.
- Database: SQLite (a single file, no database server).
- Uploaded files are stored on the local file system; SQLite keeps their metadata.
- All analysis is computed by a separate Python service (FastAPI + scikit-learn),
  so results match what students get in the Colab labs.
- Athlete data is personal health data (KVKK/GDPR): it must not be sent to
  third-party services. Demo data is synthetic.

## The PRD must contain these sections
1. Problem and goal (one paragraph)
2. Users (2-3 short personas)
3. User stories ("As a ..., I want ..., so that ...")
4. Scope of the first version (MVP): only "Know your data" and "Predict a risk"
   analysis tabs, plus login, settings and data management
5. Out of scope for the MVP: list explicitly, including the other analysis tabs
6. Requirements per page, each with acceptance criteria I can test by hand
7. Guardrails, each with an example of when it fires
8. Constraints and assumptions
9. Success criteria: how we will know the MVP works
10. Open questions

Keep it short: plain language, no more than about 3 pages, no code, no architecture.
```

## Why the prompt is built this way

- **Interview first.** The questions the agent asks show the gaps you had not thought about.
- **"No code, no architecture."** A PRD is *what* and *why*. *How* is the next step, the design document.
  Without this line the agent starts building straight away.
- **Decisions already made sit under their own heading, marked final.** The agent records them as constraints and
  does not spend interview questions on them. Put every technology choice you have already made here.
- **The MVP scope is in the prompt.** Two analysis tabs only; the other three go on the out-of-scope list,
  so the agent does not quietly widen the scope.
- **Acceptance criteria you can test by hand.** They become the checklist for step 7, verification.
