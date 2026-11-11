# Implementation Plan: Sports Analytics Web App (MVP)

## Overview & Delivery Strategy

This plan breaks down the development of the MVP into **9 sequential, end-to-end vertical slices**. Every task is self-contained: when a task is completed, the application builds, runs cleanly with two local commands, and provides immediate functionality that can be tested by hand in under 5 minutes.

### Explicitly Excluded from MVP Scope
In strict accordance with the approved PRD and Design Document, the following items are intentionally omitted:
- **"Predict a number" Tab**: Regression models (e.g. sprint times, jump heights).
- **"Find groups" Tab**: Unsupervised clustering (e.g. athlete archetypes).
- **"Over time" Tab**: Longitudinal ACWR calculations and workload trends.
- **Public Self-Registration**: No public signup; accounts are provisioned via admin seeding.
- **Multi-Tenant Sharing**: No cross-user file access or team workspaces.
- **Cloud/External APIs**: Zero third-party telemetry, cloud storage, or external AI APIs.
- **Docker/Containers**: Deployment runs directly on the local machine via Node and Python virtual environment.

---

## Task 1: Skeleton & Service Interconnect
- **Goal**: Establish the base project structure so both Next.js and FastAPI run locally with two commands, communicate over loopback HTTP (`127.0.0.1:8000`), and display a live health status screen.
- **PRD Acceptance Criteria Covered**: Section 1 & Section 8 (Local two-command execution, basic communication baseline).
- **Files Created / Changed**:
  - `frontend/package.json`, `frontend/app/layout.tsx`, `frontend/app/page.tsx`
  - `frontend/lib/python-client.ts`
  - `backend/requirements.txt`, `backend/main.py`
  - `backend/routers/health.py`
  - `data/uploads/.gitkeep`, `data/app.db` initialization script
- **How to Test by Hand (< 5 minutes)**:
  1. Terminal 1: Run `cd backend && uvicorn main:app --port 8000`.
  2. Terminal 2: Run `cd frontend && npm run dev`.
  3. Open `http://localhost:3000` in the browser.
  4. Verify the page displays "Sports Analytics Platform: Operational" and confirms an active, successful connection to the Python backend (`status: ok`).

---

## Task 2: Authentication & Route Protection
- **Goal**: Implement email and password authentication using encrypted session cookies (`iron-session`), password hashing (`bcrypt`), and an SQLite `users` table, with middleware redirecting unauthenticated traffic.
- **PRD Acceptance Criteria Covered**: 6.1 (1, 2, 3, 4).
- **Files Created / Changed**:
  - `frontend/lib/db.ts` (SQLite connection to `data/app.db`)
  - `frontend/lib/session.ts` (Session encryption configuration)
  - `frontend/app/login/page.tsx` (Login UI with shadcn/ui components)
  - `frontend/app/api/auth/login/route.ts`, `frontend/app/api/auth/logout/route.ts`, `frontend/app/api/auth/me/route.ts`
  - `frontend/middleware.ts` (Route protection guard)
  - `scripts/seed-admin.js` (Local utility to create an initial user account)
- **How to Test by Hand (< 5 minutes)**:
  1. Run `node scripts/seed-admin.js` to seed `coach@club.com` / `password123`.
  2. Visit `http://localhost:3000/data` without logging in; verify immediate redirect to `/login`.
  3. Enter an incorrect password; verify an error alert: "Invalid email or password".
  4. Enter correct credentials; verify redirect to `/data` and session cookie creation.
  5. Click "Logout"; verify session is cleared and user is redirected to `/login`.

---

## Task 3: Settings Page (Profile & Appearance)
- **Goal**: Deliver the Settings page with two tabs: Profile (view details, update display name, change password) and Appearance (toggle light/dark/system theme and font choice) with immediate persistence.
- **PRD Acceptance Criteria Covered**: 6.2 (1, 2, 3).
- **Files Created / Changed**:
  - `frontend/app/settings/page.tsx`
  - `frontend/components/nav-header.tsx` (Navigation bar with user profile & settings links)
  - `frontend/components/theme-provider.tsx`
  - `frontend/app/api/user/profile/route.ts`
  - `frontend/app/api/user/password/route.ts`
- **How to Test by Hand (< 5 minutes)**:
  1. Navigate to `/settings`.
  2. Under the **Appearance** tab, switch between Light and Dark mode; confirm theme switches instantly across the interface.
  3. Switch the font family (e.g. Inter to Roboto); confirm typography changes immediately.
  4. Under the **Profile** tab, update your display name and change your password.
  5. Refresh the page or re-login with the new password; verify all updates persisted in SQLite.

---

## Task 4: File Upload, Listing, and Deletion
- **Goal**: Implement the Data Management page file explorer, allowing users to upload CSV and `.xlsx` files (enforcing 50MB and 50,000 row limits), view metadata in a table, and delete files with confirmation.
- **PRD Acceptance Criteria Covered**: 6.3 (1, 2, 6).
- **Files Created / Changed**:
  - `frontend/app/data/page.tsx`
  - `frontend/components/file-uploader.tsx`
  - `frontend/app/api/files/route.ts` (Handles multipart upload, size/type checks, SQLite record)
  - `frontend/app/api/files/[id]/route.ts` (Handles deletion from SQLite and disk)
  - `backend/routers/files.py` (Validates row and column counts from disk file)
- **How to Test by Hand (< 5 minutes)**:
  1. Navigate to `/data`.
  2. Upload a sample CSV dataset (<50MB, $\le$50,000 rows); confirm it appears in the table with its name, row count, column count, and upload date.
  3. Attempt to upload an invalid file type (e.g. `.pdf` or `.png`); confirm rejection with a clear error toast.
  4. Click the delete icon on an uploaded file; confirm that a confirmation modal appears.
  5. Confirm deletion; verify the file disappears from the table and is removed from `data/uploads/`.

---

## Task 5: In-Browser Spreadsheet Viewer & In-Place Editing
- **Goal**: Provide an interactive in-browser spreadsheet view (`/data/[id]`) that renders large files smoothly using server-side windowed paging, lets users edit cells, delete rows, and rename columns, and commits changes via a "Save Changes" button.
- **PRD Acceptance Criteria Covered**: 6.3 (3, 4, 5).
- **Files Created / Changed**:
  - `frontend/app/data/[id]/page.tsx`
  - `frontend/components/spreadsheet-grid.tsx`
  - `frontend/app/api/files/[id]/slice/route.ts`
  - `frontend/app/api/files/[id]/save/route.ts`
  - `backend/routers/files.py` (Adds `/api/files/slice` and `/api/files/save` endpoints)
- **How to Test by Hand (< 5 minutes)**:
  1. On `/data`, click "View" on an uploaded dataset.
  2. Confirm rows 1–50 load with pagination controls and column sorting.
  3. Double-click a cell (e.g., change `450` to `500`); click "Drop Row" on an unwanted row; double-click a header to rename it.
  4. Verify the pending change counter displays (e.g., "3 pending changes").
  5. Click "Save Changes"; wait for the success toast.
  6. Refresh the page; verify that the edited cell, dropped row, and renamed column are persisted.

---

## Task 6: "Know Your Data" (Exploratory Data Analysis)
- **Goal**: Implement the "Know your data" analysis tab, computing dataset health metrics, column data type inferences, summary statistics with outlier detection, and an interactive correlation matrix.
- **PRD Acceptance Criteria Covered**: 6.4 (1, 2, 3, 4).
- **Files Created / Changed**:
  - `frontend/app/analysis/page.tsx`
  - `frontend/components/eda-view.tsx`
  - `frontend/app/api/analysis/eda/route.ts`
  - `backend/routers/analysis.py` (`/api/analysis/eda`)
  - `backend/services/eda_engine.py` (Pandas computations for types, stats, missingness, correlations)
- **How to Test by Hand (< 5 minutes)**:
  1. Navigate to `/analysis` and ensure "Know your data" tab is active.
  2. Select an uploaded dataset from the dropdown.
  3. Verify top metric cards display total rows, columns, and overall missing value percentage.
  4. Inspect the column table to confirm data types and missing counts are correctly categorized.
  5. Click a numerical column; verify descriptive stats (mean, median, IQR, min/max) and histogram/boxplot render.
  6. View the correlation matrix; verify correlations $> |0.70|$ are clearly highlighted.

---

## Task 7: "Predict a Risk" - Core Modeling & Athlete Group Splitting
- **Goal**: Implement the "Predict a risk" classification workflow: target column selection, algorithm suggestion (Logistic Regression vs Random Forest), tuning controls, Athlete ID selection enforcing `GroupShuffleSplit`, and side-by-side Dummy baseline comparison.
- **PRD Acceptance Criteria Covered**: 6.5 (1, 2, 3, 4) & Guardrails 1, 2.
- **Files Created / Changed**:
  - `frontend/components/risk-prediction-view.tsx`
  - `frontend/app/api/analysis/predict/route.ts`
  - `backend/routers/analysis.py` (`/api/analysis/predict`)
  - `backend/services/ml_engine.py` (Scikit-Learn classification pipelines, DummyClassifier)
  - `backend/services/guardrails.py` (Athlete group split validation)
- **How to Test by Hand (< 5 minutes)**:
  1. On `/analysis`, switch to the "Predict a risk" tab.
  2. Choose a binary/multiclass target column (e.g. `strain_risk`); confirm the system suggests an algorithm with a short explanation.
  3. Select the `athlete_id` column as the Athlete ID.
  4. Click "Run Honest Evaluation".
  5. Verify the results card renders the primary model's metrics directly beside the Dummy (Majority Class) baseline.
  6. Verify the blue informational banner is displayed: *"Honest Split: Data partitioned by 'athlete_id'. 0 athletes share rows across training and testing."*

---

## Task 8: Modeling Guardrails (Leakage, Rare Outcomes, and Sample Size)
- **Goal**: Implement the remaining three guardrails in the classification engine: target leakage detection, rare outcome handling (suppress raw accuracy, surface PR-AUC and F1), and small test sample size warnings.
- **PRD Acceptance Criteria Covered**: 6.5 (5) & Guardrails 3, 4, 5.
- **Files Created / Changed**:
  - `backend/services/guardrails.py` (Target correlation check, class imbalance check, sample size check)
  - `frontend/components/guardrail-banner.tsx` (Alert styling for info, warning, and destructive states)
  - `frontend/components/risk-prediction-view.tsx` (Conditionally hide raw accuracy and highlight PR-AUC)
- **How to Test by Hand (< 5 minutes)**:
  1. **Leakage Test**: Run risk prediction on a dataset containing a feature column with $|r| \ge 0.90$ with the target; verify a prominent red destructive alert fires advising the user to exclude that column.
  2. **Rare Outcome Test**: Run risk prediction on a dataset with $<15\%$ positive target cases; verify an amber alert fires, raw accuracy is hidden from the primary card, and PR-AUC/F1 are showcased.
  3. **Small Sample Test**: Run risk prediction where the test split results in $<10$ positive cases; verify an orange caution banner warns of high metric variance.

---

## Task 9: Analysis History & Exports (Executive PDF & Enriched CSV)
- **Goal**: Complete the analytical loop by persisting analysis runs to SQLite history and offering one-click downloads for an executive summary PDF (compiled via ReportLab/Matplotlib) and an enriched CSV containing predicted probabilities.
- **PRD Acceptance Criteria Covered**: 6.6 (1, 2, 3).
- **Files Created / Changed**:
  - `frontend/components/analysis-history.tsx` (Drawer or modal showing past runs)
  - `backend/routers/exports.py` (`/api/export/pdf` and `/api/export/csv`)
  - `backend/services/pdf_builder.py` (ReportLab template compiling metrics, charts, guardrails)
  - `frontend/app/api/analysis/history/route.ts`
  - `frontend/app/api/analysis/export/route.ts`
- **How to Test by Hand (< 5 minutes)**:
  1. Complete a risk prediction run; verify that it immediately appears in the "Analysis History" panel with timestamp and summary metrics.
  2. Click "Export Summary PDF"; verify a valid `.pdf` downloads containing the evaluation metrics, confusion matrix, PR curve plot, and fired guardrail notes.
  3. Click "Export Predictions CSV"; verify a `.csv` downloads containing all original columns plus `predicted_class` and `predicted_risk_probability`.

---

## Execution Readiness

Each of these 9 tasks maintains a working, testable product state. No code will be written until this implementation plan is formally reviewed and approved.

