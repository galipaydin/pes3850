# System Design Document (DESIGN.md)

## 1. System Overview

The application is structured as a two-service architecture that runs locally on a single laptop without cloud dependencies or Docker containers. 

- **Frontend & Orchestrator (Next.js + shadcn/ui)**: Operates on `http://localhost:3000`. Handles user interface rendering, session management via encrypted HTTP-only cookies, local SQLite operations, and proxies analysis requests.
- **Analytical Engine (FastAPI + scikit-learn)**: Operates on `http://127.0.0.1:8000`. Executes all tabular data processing, statistical summaries, classification training, guardrail checks, and PDF report compilation using Pandas, Scikit-Learn, Matplotlib, and ReportLab.
- **Storage Layer**: Local SQLite database (`data/app.db`) for relational metadata and local directory storage (`data/uploads/`) for tabular files.

```text
+-------------------------------------------------------------------------+
|                              LOCAL LAPTOP                               |
|                                                                         |
|  +--------------------+             +--------------------------------+  |
|  |   Web Browser      |             |     Next.js Server (:3000)     |  |
|  |  (React/shadcn UI) | <--(HTTP)-->|  - Route Handlers / Proxy      |  |
|  +--------------------+   (Cookie)  |  - Auth & SQLite Metadata      |  |
|                                     +--------------------------------+  |
|                                                     |                   |
|                                         Internal HTTP (Loopback)        |
|                                         http://127.0.0.1:8000           |
|                                                     v                   |
|  +--------------------+             +--------------------------------+  |
|  |  SQLite Database   |             |     FastAPI Service (:8000)    |  |
|  |  (data/app.db)     |<--[SQL]-----|  - Pandas EDA & Validation     |  |
|  |  - Users & Sessions|             |  - Scikit-Learn Classification |  |
|  |  - Files Metadata  |             |  - Guardrail Calculations      |  |
|  |  - Analysis History|             |  - ReportLab PDF Generation    |  |
|  +--------------------+             +--------------------------------+  |
|            ^                                        |                   |
|            | File IDs / Paths                       | File Path Access  |
|            v                                        v                   |
|  +-------------------------------------------------------------------+  |
|  |               Local Storage (data/uploads/{file_id}.csv)          |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

### Local Execution
The entire system is started with two terminal commands:
1. `npm run dev` (starts Next.js on port 3000)
2. `python -m uvicorn main:app --port 8000` (starts FastAPI on port 8000)

---

## 2. Screens and Flow

```text
                                +-------------+
                                |    Login    |
                                +-------------+
                                       |
                                       v
                                +-------------+
           +------------------->|  Data Mgmt  |<-------------------+
           |                    +-------------+                    |
           |                           |                           |
           v                           v                           v
    +-------------+             +-------------+             +-------------+
    |  Settings   |             | Spreadsheet |             |  Analysis   |
    | (Profile /  |             |   Viewer    |             | (EDA / Risk |
    | Appearance) |             +-------------+             | Prediction) |
    +-------------+                                         +-------------+
                                                                   |
                                                                   v
                                                            +-------------+
                                                            |  PDF / CSV  |
                                                            |   Exports   |
                                                            +-------------+
```

### 2.1. Screen Wireframes

#### Screen 1: Login (`/login`)
```text
+------------------------------------------------------------------+
|                          SPORTS ANALYTICS                        |
+------------------------------------------------------------------+
|                                                                  |
|                     +-----------------------+                    |
|                     | Sign In to Account    |                    |
|                     |                       |                    |
|                     | Email Address         |                    |
|                     | [ user@club.com     ] |                    |
|                     |                       |                    |
|                     | Password              |                    |
|                     | [ ****************  ] |                    |
|                     |                       |                    |
|                     | [      Sign In      ] |                    |
|                     +-----------------------+                    |
|                                                                  |
+------------------------------------------------------------------+
```

#### Screen 2: Data Management (`/data`)
```text
+------------------------------------------------------------------+
| Sports Analytics  | Data Management | Analysis | Settings | [Logout] |
+------------------------------------------------------------------+
| Upload Dataset                                                   |
| +--------------------------------------------------------------+ |
| |  Drag and drop CSV or .xlsx here, or [Browse Files]          | |
| |  Max file size: 50MB. Max rows: 50,000                       | |
| +--------------------------------------------------------------+ |
|                                                                  |
| Your Datasets                                                    |
| +---------------------+---------+----------+------------+------+ |
| | Filename            | Rows    | Columns  | Uploaded   | Act. | |
| +---------------------+---------+----------+------------+------+ |
| | wellness_gps_w1.csv | 12,400  | 18       | 2026-11-01 | [V][D]| |
| | physical_tests.xlsx | 450     | 12       | 2026-10-28 | [V][D]| |
| +---------------------+---------+----------+------------+------+ |
| [V] View Spreadsheet  [D] Delete                                 |
+------------------------------------------------------------------+
```

#### Screen 3: Spreadsheet Viewer (`/data/[id]`)
```text
+------------------------------------------------------------------+
| < Back to Files | Editing: wellness_gps_w1.csv   [ Save Changes ] |
+------------------------------------------------------------------+
| Showing rows 1 - 50 of 12,400               [ < Prev ] [ Next > ]|
| +----+-------------+------------+--------------+---------------+ |
| | #  | athlete_id  | sRPE_load  | sleep_score  | strain_risk   | |
| +----+-------------+------------+--------------+---------------+ |
| | 1  | ATH_01      | 450        | 8            | 0             | |
| | 2  | ATH_01      | 620 [edit] | 6            | 1             | |
| | 3  | ATH_02      | 310        | 9            | 0  [Drop Row] | |
| +----+-------------+------------+--------------+---------------+ |
| * 2 pending edits staged. Click 'Save Changes' to commit to disk.|
+------------------------------------------------------------------+
```

#### Screen 4: Analysis - "Know Your Data" (`/analysis?tab=eda`)
```text
+------------------------------------------------------------------+
| Sports Analytics  | Data Management | Analysis | Settings | [Logout] |
+------------------------------------------------------------------+
| Select Dataset: [ wellness_gps_w1.csv           v ]              |
| [ Know your data (EDA) ]  [ Predict a risk (Classification) ]    |
+------------------------------------------------------------------+
| Dataset Health: 12,400 rows | 18 columns | 1.4% missing values   |
|                                                                  |
| Column Inferences:                                               |
| - athlete_id (Categorical, 32 unique, 0% missing)                |
| - sRPE_load  (Numerical, min: 100, max: 1200, mean: 480)        |
| - sleep_score(Numerical, min: 1, max: 10, 8 outliers detected)   |
|                                                                  |
| Distribution & Outliers:             Correlation Heatmap:        |
| +----------------------------------+ +-------------------------+ |
| | [ Histogram / Boxplot Chart ]    | | sRPE vs Strain: +0.68   | |
| | (Selected column: sRPE_load)     | | Sleep vs Strain: -0.54  | |
| +----------------------------------+ +-------------------------+ |
+------------------------------------------------------------------+
```

#### Screen 5: Analysis - "Predict a Risk" (`/analysis?tab=predict`)
```text
+------------------------------------------------------------------+
| Target Question: What risk do you want to predict?               |
| Target Column: [ strain_risk                   v ]               |
| Athlete ID:    [ athlete_id                    v ]               |
|                                                                  |
| Suggested Algorithm: Random Forest                               |
| "Your target has non-linear relationships with workload inputs." |
| [ Override Settings: Algorithm [ Random Forest v ] Split [80/20] |
|   Features: [x] sRPE_load  [x] sleep_score  [ ] test_date        |
|   Class Balance: [x] Adjust for rare outcomes ]                  |
|                                                                  |
| [ Run Honest Evaluation ]                                        |
|                                                                  |
| Results & Guardrails:                                            |
| ! ALERT: Rare outcome detected (4.2% risk rate). Showing PR-AUC. |
| ! NOTICE: Group split by 'athlete_id'. 0 athlete overlap.        |
|                                                                  |
| +-------------------------------+------------------------------+ |
| | Primary Model (Random Forest) | Baseline (Majority Class)    | |
| | PR-AUC: 0.74                  | PR-AUC: 0.04                 | |
| | F1-Score: 0.68                | F1-Score: 0.00               | |
| | Recall: 0.71                  | Recall: 0.00                 | |
| +-------------------------------+------------------------------+ |
| [ Export Summary PDF ]  [ Export Predictions CSV ]               |
+------------------------------------------------------------------+
```

---

## 3. Data Model

The data layer uses SQLite (`data/app.db`) for system state and relational metadata. Uploaded and modified datasets reside in the local directory (`data/uploads/`).

### 3.1. Entity Relationship
```text
+------------------+         1:N         +-------------------+
|      users       |-------------------->|       files       |
+------------------+                     +-------------------+
        |                                          |
        | 1:N                                      | 1:N
        v                                          v
+------------------------------------------------------------+
|                       analysis_runs                        |
+------------------------------------------------------------+
```

### 3.2. Table Schemas

#### Table: `users`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | TEXT | PRIMARY KEY | Unique UUID identifier. |
| `email` | TEXT | UNIQUE, NOT NULL | Admin-provisioned user email. |
| `password_hash` | TEXT | NOT NULL | Bcrypt hash (cost factor 12). |
| `display_name` | TEXT | NOT NULL | Coach/student full name. |
| `font_family` | TEXT | DEFAULT 'inter' | Preference: 'inter', 'roboto', 'system'. |
| `theme` | TEXT | DEFAULT 'system' | Preference: 'light', 'dark', 'system'. |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp. |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last profile update. |

#### Table: `files`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | TEXT | PRIMARY KEY | Unique UUID for the file. |
| `user_id` | TEXT | NOT NULL, FK(`users.id`) | File owner (isolated workspace). |
| `original_name`| TEXT | NOT NULL | Name of uploaded file (e.g. `gps_w1.csv`). |
| `stored_path` | TEXT | NOT NULL | Absolute local disk path (`data/uploads/{id}.csv`). |
| `size_bytes` | INTEGER | NOT NULL | File size in bytes (max 52,428,800). |
| `row_count` | INTEGER | NOT NULL | Number of data rows. |
| `column_count` | INTEGER | NOT NULL | Number of columns. |
| `uploaded_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Upload timestamp. |
| `updated_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last edit/save timestamp. |

#### Table: `analysis_runs`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | TEXT | PRIMARY KEY | Unique run UUID. |
| `user_id` | TEXT | NOT NULL, FK(`users.id`) | Initiator of analysis. |
| `file_id` | TEXT | NOT NULL, FK(`files.id`) | Analyzed file. |
| `question_type`| TEXT | NOT NULL | 'eda' or 'predict_risk'. |
| `target_column`| TEXT | NULLABLE | Target column (for classification). |
| `athlete_col` | TEXT | NULLABLE | Selected Athlete ID column. |
| `algorithm` | TEXT | NULLABLE | 'logistic_regression' or 'random_forest'. |
| `summary_json` | TEXT | NOT NULL | Model metrics, baseline metrics, column stats. |
| `guardrails_json`| TEXT| NOT NULL | Status and messages of all fired guardrails. |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Execution timestamp. |

---

## 4. API Between Next.js and Python (FastAPI)

All endpoints operate over `http://127.0.0.1:8000`. Next.js validates session credentials, verifies file ownership in SQLite, and invokes FastAPI passing local file paths.

### 4.1. Health Check
- **`GET /health`**
- **Response**: `{"status": "ok", "service": "pes3850-analytics-engine"}`

### 4.2. File Paging & Commit (Spreadsheet Viewer)

#### `POST /api/files/slice`
Reads a window of rows from disk with optional sorting.

**Request JSON:**
```json
{
  "file_path": "/Users/user/project/data/uploads/f47ac10b.csv",
  "offset": 0,
  "limit": 50,
  "sort_column": "sRPE_load",
  "sort_direction": "desc"
}
```

**Response JSON:**
```json
{
  "total_rows": 12400,
  "offset": 0,
  "limit": 50,
  "columns": ["athlete_id", "sRPE_load", "sleep_score", "strain_risk"],
  "rows": [
    {"_row_index": 142, "athlete_id": "ATH_01", "sRPE_load": 920, "sleep_score": 4, "strain_risk": 1},
    {"_row_index": 88, "athlete_id": "ATH_04", "sRPE_load": 890, "sleep_score": 5, "strain_risk": 1}
  ]
}
```

#### `POST /api/files/save`
Applies staged cell edits, dropped rows, and renamed columns, rewriting the CSV on disk.

**Request JSON:**
```json
{
  "file_path": "/Users/user/project/data/uploads/f47ac10b.csv",
  "rename_columns": { "old_name": "new_name" },
  "drop_row_indices": [14, 29],
  "cell_updates": [
    { "row_index": 2, "column": "sRPE_load", "new_value": 620 }
  ]
}
```

**Response JSON:**
```json
{
  "success": true,
  "new_row_count": 12398,
  "new_column_count": 4,
  "updated_at": "2026-11-03T21:40:00Z"
}
```

### 4.3. Know Your Data (EDA)

#### `POST /api/analysis/eda`
Generates descriptive statistics, type inferences, missingness, and correlation data.

**Request JSON:**
```json
{
  "file_path": "/Users/user/project/data/uploads/f47ac10b.csv"
}
```

**Response JSON:**
```json
{
  "dataset_summary": {
    "total_rows": 12400,
    "total_columns": 4,
    "missing_cells_percentage": 0.45
  },
  "columns": [
    {
      "name": "athlete_id",
      "inferred_type": "categorical",
      "unique_count": 32,
      "missing_count": 0,
      "missing_percentage": 0.0
    },
    {
      "name": "sRPE_load",
      "inferred_type": "numerical",
      "unique_count": 450,
      "missing_count": 12,
      "missing_percentage": 0.1,
      "stats": {
        "mean": 482.3,
        "std": 140.2,
        "min": 100.0,
        "p25": 380.0,
        "median": 475.0,
        "p75": 580.0,
        "max": 1150.0,
        "outlier_count_iqr": 18
      }
    }
  ],
  "correlations": {
    "columns": ["sRPE_load", "sleep_score", "strain_risk"],
    "matrix": [
      [1.00, -0.42, 0.68],
      [-0.42, 1.00, -0.54],
      [0.68, -0.54, 1.00]
    ]
  }
}
```

### 4.4. Predict a Risk (Classification)

#### `POST /api/analysis/predict`
Executes classification modeling with athlete group splitting and baseline comparison.

**Request JSON:**
```json
{
  "file_path": "/Users/user/project/data/uploads/f47ac10b.csv",
  "target_column": "strain_risk",
  "athlete_id_column": "athlete_id",
  "algorithm": "random_forest",
  "feature_columns": ["sRPE_load", "sleep_score"],
  "test_split_ratio": 0.20,
  "balance_classes": true
}
```

**Response JSON:**
```json
{
  "algorithm_used": "random_forest",
  "target_column": "strain_risk",
  "evaluation": {
    "model_metrics": {
      "pr_auc": 0.742,
      "f1_score": 0.680,
      "precision": 0.655,
      "recall": 0.708,
      "raw_accuracy": 0.941
    },
    "baseline_metrics": {
      "strategy": "most_frequent",
      "pr_auc": 0.042,
      "f1_score": 0.000,
      "precision": 0.000,
      "recall": 0.000,
      "raw_accuracy": 0.958
    },
    "confusion_matrix": {
      "tn": 2300,
      "fp": 38,
      "fn": 29,
      "tp": 71
    }
  },
  "guardrails": [
    {
      "id": "group_split",
      "status": "active",
      "message": "Group split by 'athlete_id' enforced. 0 athletes overlap between train and test."
    },
    {
      "id": "rare_outcome",
      "status": "warning",
      "message": "Target positive rate is 4.2%. Raw accuracy is hidden; evaluate via PR-AUC and Recall."
    },
    {
      "id": "leakage",
      "status": "clear",
      "message": "No feature columns exhibit suspicious near-perfect target correlation."
    },
    {
      "id": "sample_size",
      "status": "clear",
      "message": "Test set contains 100 positive cases (sufficient for evaluation)."
    }
  ]
}
```

### 4.5. Export Endpoints

- **`POST /api/export/pdf`**: Generates and streams an executive PDF summary using `reportlab` and `matplotlib` plots.
- **`POST /api/export/csv`**: Appends `predicted_class` and `predicted_risk_probability` to the original dataset and streams the resulting CSV file.

---

## 5. Guardrails Architecture

All guardrail logic is computed in Python inside the analytical service prior to returning results to Next.js.

```text
                                [ Analysis Request ]
                                         |
                                         v
                      +--------------------------------------+
                      | Guardrail 2: Athlete Group Split     |
                      | (GroupKFold / GroupShuffleSplit)     |
                      +--------------------------------------+
                                         |
                                         v
                      +--------------------------------------+
                      | Guardrail 3: Target Leakage Check    |
                      | (Flags features with |r| >= 0.90)    |
                      +--------------------------------------+
                                         |
                                         v
                      +--------------------------------------+
                      | Train Model + Dummy Baseline         |
                      | Guardrail 1: Compute Baseline Metric |
                      +--------------------------------------+
                                         |
                                         v
                      +--------------------------------------+
                      | Guardrail 4: Rare Outcome Check      |
                      | (If minority < 15%, suppress acc.)   |
                      +--------------------------------------+
                                         |
                                         v
                      +--------------------------------------+
                      | Guardrail 5: Test Set Sample Size    |
                      | (Warns if minority test cases < 10)  |
                      +--------------------------------------+
                                         |
                                         v
                                [ Response to UI ]
```

### Guardrail UI Specifications

| Guardrail | Detection Rule | UI Component & Styling | Message Displayed |
|---|---|---|---|
| **1. Baseline Comparison** | Always computed using `DummyClassifier(strategy="most_frequent")`. | Side-by-side metric comparison card with neutral gray borders. | "Model PR-AUC (0.74) vs Baseline (0.04). The baseline always predicts the most common class." |
| **2. Athlete Group Split** | Triggered when user selects an Athlete ID column; uses `GroupShuffleSplit`. | Blue Info Callout (`Alert` with info icon). | "Honest Split: Data partitioned by 'athlete_id'. 0 athletes share rows across training and testing." |
| **3. Target Leakage** | Feature column has Pearson $|r| \ge 0.90$ or Mutual Information $> 0.85$ with target. | Red Destructive Callout (`Alert` variant `destructive`). | "High Risk Leakage: Column '[col_name]' has 0.97 correlation with '[target]'. Exclude this feature." |
| **4. Rare Outcome** | Minority target class prevalence is $< 15\%$. | Amber Warning Callout; hides raw accuracy metric card. | "Rare Outcome Alert: Only 4.2% positive cases. Accuracy is deceptive; PR-AUC and F1 are primary." |
| **5. Underpowered Test Set** | Test set contains $< 10$ positive outcome examples. | Orange Caution Callout (`Alert` with alert-triangle). | "Caution: Test set contains only [N] positive cases. Metric estimates have high statistical noise." |

---

## 6. Security and Privacy (KVKK / GDPR)

1. **Local Isolation**: All application files, databases, and network requests stay strictly bound to localhost (`127.0.0.1`). No analytical data, metadata, telemetry, or user information is transmitted to external servers or cloud APIs.
2. **Password Storage**: Passwords are never stored in plaintext. Passwords are hashed using `bcrypt` with cost factor 12 via the Next.js auth route handler.
3. **Session Cookies**: Session state is encrypted and signed using `iron-session` with a 32-character secret key. Cookies are marked `HttpOnly`, `SameSite=Lax`, and `Secure` (in production mode).
4. **File Type & Size Verification**:
   - File size is checked during upload streaming; uploads exceeding 52,428,800 bytes (50MB) are rejected immediately.
   - Files are validated against allowed extensions (`.csv`, `.xlsx`) and inspected for standard CSV delimiters or Excel magic bytes before persistence.
   - Row limit verification: files with $> 50,000$ rows trigger a descriptive validation error before processing.
5. **Synthetic Demo Data**: Any sample datasets provided for teaching or demonstration contain purely synthetic athlete profiles to eliminate personal data exposure risks.

---

## 7. Error Handling

| Scenario | System Behavior | User Interface Presentation |
|---|---|---|
| **Oversized Upload (>50MB)** | Next.js API route terminates stream and deletes temporary chunks. | Red toast notification: *"File exceeds maximum limit of 50MB."* |
| **Malformed CSV / Corrupted Excel** | Python parsing engine throws format exception. | Dialog error: *"Unable to parse file. Ensure valid headers on row 1 and consistent delimiters."* |
| **Target Column has 1 Unique Value** | Python detects zero-variance target ($y$ has only 1 class). | Banner on Analysis Page: *"Target column '[col]' contains only one class. Prediction requires at least two classes."* |
| **Python Service Unavailable** | Next.js internal fetch to `127.0.0.1:8000` times out or fails connection. | Alert callout: *"Analytical engine is unavailable. Ensure the Python service is running on port 8000."* |
| **Missing Athlete ID during Risk Prediction** | Validation triggers if target is repeated measurements without ID. | Form inline error: *"Please select an Athlete ID column to prevent split contamination across athletes."* |

---

## 8. Testing Strategy

| Acceptance Criteria Category | Verification Method | Automated Test Scope |
|---|---|---|
| **Authentication & Isolation** | Attempt login with invalid credentials; verify redirect on unauthenticated route access. | Next.js Route Integration Tests (`jest` / `playwright`). Verify cookie encryption and user isolation. |
| **Spreadsheet In-Place Edits** | Open 10,000-row file, edit cell row 5, drop row 20, click "Save Changes", reload. | Unit test `/api/files/save` logic. Verify disk file updates with exact modified values. |
| **Athlete Split Contamination** | Run classification with synthetic athlete dataset having 10 rows per athlete. | Python test: Assert intersection of `train_athletes` and `test_athletes` is empty set (`len(set_a & set_b) == 0`). |
| **Leakage Detection** | Feed dataset with artificial duplicate target column into `/api/analysis/predict`. | Python unit test: Assert guardrail returns `status="warning"` for the correlated column. |
| **Rare Outcome Suppression** | Run classification on dataset with 3% positive class rate. | Cypress/Playwright UI test: Assert raw accuracy is absent and PR-AUC metric card is visible. |
| **PDF & CSV Export** | Trigger both export buttons on completed run. | Integration test: Assert PDF response header is `application/pdf` and CSV includes `predicted_class`. |

---

## 9. Folder Structure

```text
project/
├── data/
│   ├── app.db                       # Local SQLite database
│   └── uploads/                     # Uploaded and edited CSV/Excel files
├── docs/
│   ├── PRD.md                       # Approved Product Requirements Document
│   └── DESIGN.md                    # This system design document
├── backend/                         # FastAPI Python Service (:8000)
│   ├── main.py                      # FastAPI entrypoint and CORS setup
│   ├── requirements.txt             # fastapi, uvicorn, pandas, scikit-learn, reportlab, matplotlib
│   ├── routers/
│   │   ├── files.py                 # Slicing (/slice) and commit save (/save)
│   │   ├── analysis.py              # /eda and /predict endpoints
│   │   └── exports.py               # /export/pdf and /export/csv
│   └── services/
│       ├── eda_engine.py            # Summary stats, missingness, correlation
│       ├── ml_engine.py             # Model training & baseline evaluation
│       ├── guardrails.py            # The 5 guardrail validation rules
│       └── pdf_builder.py           # ReportLab PDF compilation
└── frontend/                        # Next.js App Router (:3000)
    ├── package.json                 # next, react, shadcn/ui, iron-session, bcrypt
    ├── middleware.ts                # Route protection checking auth session
    ├── app/
    │   ├── layout.tsx               # Root layout (theme provider, font loader)
    │   ├── login/
    │   │   └── page.tsx             # Login screen
    │   ├── data/
    │   │   ├── page.tsx             # Data management (file list + upload)
    │   │   └── [id]/
    │   │       └── page.tsx         # In-browser spreadsheet viewer
    │   ├── analysis/
    │   │   └── page.tsx             # Analysis page ("Know your data" & "Predict risk")
    │   ├── settings/
    │   │   └── page.tsx             # Settings (Profile & Appearance tabs)
    │   └── api/
    │       ├── auth/
    │       │   ├── login/route.ts
    │       │   ├── logout/route.ts
    │       │   └── me/route.ts
    │       ├── files/
    │       │   └── route.ts         # Upload, list, delete proxy
    │       └── analysis/
    │           └── route.ts         # Proxy to FastAPI backend with history logging
    ├── components/
    │   ├── ui/                      # shadcn/ui components (button, table, card, dialog, alert)
    │   ├── file-uploader.tsx
    │   ├── spreadsheet-grid.tsx
    │   └── guardrail-banner.tsx
    └── lib/
        ├── db.ts                    # SQLite connection & query helpers
        ├── session.ts               # iron-session configuration
        └── python-client.ts         # Internal fetch wrapper for 127.0.0.1:8000
```

---

## 10. Decision Log

### Decision 1: Authentication Architecture
- **Options Considered**:
  - *Option A*: Lightweight Encrypted Cookie Session (`iron-session` + `bcrypt` in SQLite).
  - *Option B*: NextAuth.js (Auth.js) Credentials Provider.
  - *Option C*: FastAPI-Managed JWT Tokens.
- **Choice**: **Option A**.
- **Rationale**: Keeps the Next.js server autonomous for page routing and layout rendering without querying Python on every request. Safely hashes passwords in local SQLite with zero cloud dependencies.

### Decision 2: Storage for Uploaded Files & Metadata
- **Options Considered**:
  - *Option A*: Local Filesystem (`data/uploads/`) + SQLite for metadata.
  - *Option B*: All-in-SQLite (File content stored as `BLOB`).
  - *Option C*: Dynamic SQLite Tables per Dataset.
- **Choice**: **Option A**.
- **Rationale**: Allows Pandas in the Python service to read and write files directly via local file path (`pd.read_csv`). Eliminates database bloat from 50MB files and simplifies in-place edits.

### Decision 3: Next.js ↔ Python Communication Architecture
- **Options Considered**:
  - *Option A*: Next.js Server-to-FastAPI Internal HTTP Proxy (Loopback `127.0.0.1:8000`).
  - *Option B*: Direct Browser-to-FastAPI Calls with CORS & JWT.
  - *Option C*: Background Job Queue (Redis + Celery).
- **Choice**: **Option A**.
- **Rationale**: Isolates the Python port from the browser, eliminates CORS configuration, centralizes session verification in Next.js route handlers, and automatically logs analysis history in SQLite.

### Decision 4: High-Performance Spreadsheet View
- **Options Considered**:
  - *Option A*: Full Dataset Loaded in Browser + DOM Virtualization (`@tanstack/react-virtual`).
  - *Option B*: Client-Side Numbered Pagination (50–100 rows per page).
  - *Option C*: Server-Side Windowed Paging (Fetch 50 rows at a time from backend with staged changes).
- **Choice**: **Option C**.
- **Rationale**: Selected by user preference to guarantee minimal initial payload transfers and prevent browser memory bloat on large tabular files up to 50,000 rows. Edits are staged on the client and committed in batch back to disk.

### Decision 5: PDF Report Generation
- **Options Considered**:
  - *Option A*: Python-Generated PDF (`matplotlib` + `reportlab`).
  - *Option B*: Node.js / React-PDF (`@react-pdf/renderer`).
  - *Option C*: Print Stylesheet (`@media print` / Browser "Save as PDF").
- **Choice**: **Option A**.
- **Rationale**: Enables direct access to Scikit-Learn evaluation figures, confusion matrices, and PR curves rendered in Python, producing a downloadable PDF in a single headless request.

