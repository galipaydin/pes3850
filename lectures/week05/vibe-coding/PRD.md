# Product Requirements Document (PRD)

## 1. Problem and Goal

Sport scientists, athletic coaches, and kinesiology students (such as those in PES 3850) routinely collect athlete data across wellness surveys, GPS monitoring, physical assessments, and injury tracking. Today, analyzing this data requires either manual, error-prone spreadsheet manipulation or writing custom Python scripts—causing the majority of data to remain unanalyzed. When non-programmers do attempt predictive modeling, subtle but critical methodology errors go unnoticed: feature columns that leak the target outcome, random train/test splits that place the same athlete in both sets (memorization), and deceptively high accuracy scores on rare outcomes (such as acute injuries). The goal of this web application is to provide a user-friendly, no-code platform where staff can upload datasets, view and edit them like a spreadsheet, and run robust sports science analyses by selecting the *question* they want answered. Every analysis is grounded by automatic baseline comparisons and safety guardrails that flag flawed or untrustworthy evaluations.

---

## 2. Target Personas

- **Can (Club Sport Scientist / S&C Coach)**: Collects GPS loads and daily wellness scores. Needs to detect injury risk patterns and fatigue trends quickly without fighting Python syntax or statistical libraries.
- **Elif (PES 3850 Kinesiology Student)**: Learning applied data analysis for sport. Needs to explore datasets and build predictive models that mirror course Colab labs, relying on automated guardrails to prevent common methodological pitfalls.
- **Dr. Mert (Academic Instructor / Performance Director)**: Oversees departmental sports analytics. Wants students and staff to produce transparent, honest, and reproducible analyses featuring clear baselines and reliable validation metrics.

---

## 3. User Stories

- **As a user**, I want to log in securely with my email and password so that my athletes' private data is isolated and protected.
- **As a user**, I want to customize my interface font and theme (light, dark, or system) so that the app is comfortable to use in any environment.
- **As a user**, I want to upload CSV and Excel (`.xlsx`) files and manage them in a file explorer so that all my team datasets are organized in one place.
- **As a user**, I want to open an uploaded file in an in-browser spreadsheet viewer, edit cells, delete rows, rename columns, and save changes so that I can clean simple data entry mistakes without external software.
- **As a user**, I want to open the "Know your data" tab to view data types, missing value percentages, distributions, and correlation matrices so that I understand data quality before modeling.
- **As a user**, I want to open the "Predict a risk" tab, pick an outcome column, and receive an automated model recommendation alongside a dummy baseline so that I know if the model delivers genuine predictive power.
- **As a user**, I want manual tuning controls (feature selection, algorithm choice, split ratio, class balance) so that I can refine models when needed.
- **As a user**, I want the system to warn me if an evaluation leaks data, contaminates athlete splits, or relies on misleading metrics so that I do not make false decisions.
- **As a user**, I want to view my past analyses and export results as an executive PDF summary or an enriched CSV so that I can share findings with colleagues.

---

## 4. Scope of the MVP

The MVP delivers a complete, validated analytical loop restricted to two core analytical questions and supporting infrastructure:

- **Authentication**: Invite/admin-managed email and password login.
- **Settings**: Profile management (display name, email, password update) and Appearance controls (font family selection, light/dark/system theme toggle).
- **Data Management**: File explorer supporting CSV and `.xlsx` uploads (up to 50MB and 50,000 rows), file deletion, and an in-browser interactive spreadsheet viewer allowing cell editing, row removal, column renaming, and in-place saving.
- **Analysis - "Know Your Data" Tab**: Automated exploratory data analysis (EDA) covering column data types, missing value counts/percentages, outlier detection, distribution plots, and correlation heatmaps.
- **Analysis - "Predict a Risk" Tab**: Supervised classification for binary and multiclass outcomes featuring:
  - System suggestion of suitable algorithm (Logistic Regression or Random Forest) with plain-language justification.
  - User override controls: algorithm selector, feature column inclusion/exclusion checkboxes, train/test split slider, and class imbalance weighting toggle.
  - Designated Athlete ID column selection to enforce athlete-level group splitting.
- **Built-in Guardrails**: Five automated guardrails active across all classification runs.
- **Persistence & Export**: Analysis session history log, executive PDF report export, and CSV download with predicted risk classes and probabilities appended.

---

## 5. Out of Scope for the MVP

The following capabilities are explicitly deferred to future releases:

- **"Predict a number" Tab**: Regression modeling (e.g., sprint time, jump height).
- **"Find groups" Tab**: Unsupervised clustering (e.g., athlete profiling, positional archetypes).
- **"Over time" Tab**: Longitudinal analysis, Acute:Chronic Workload Ratio (ACWR) calculations, and trend tracking.
- **Public Self-Registration**: No open sign-up; accounts are provisioned via admin/invite.
- **Multi-Tenant Sharing**: No shared group workspaces or cross-user dataset visibility; all user workspaces are strictly isolated.
- **Direct Hardware / Wearable Integrations**: No direct API synchronization with Catapult, STATSports, ForceDecks, or Oura.
- **Automated Hyperparameter Grid Search**: No exhaustive AutoML searches; manual tuning is limited to predefined algorithm parameters.

---

## 6. Requirements per Page & Acceptance Criteria

### 6.1. Login Page
- **Description**: Secure entry point for provisioned users.
- **Acceptance Criteria**:
  1. Entering valid registered credentials redirects the user to the Data Management page.
  2. Entering an invalid email or password displays a clear error message: "Invalid email or password" without revealing which field was incorrect.
  3. Submitting an empty form highlights required fields and prevents submission.
  4. An unauthenticated user attempting to access internal URLs is redirected to the login page.

### 6.2. Settings Page
- **Description**: User profile and appearance preferences.
- **Acceptance Criteria**:
  1. *Profile Tab*: User can update their display name and change their password by confirming the current password; success state updates immediately.
  2. *Appearance Tab*: Switching between Light, Dark, and System immediately updates the application theme across all pages without requiring a page reload.
  3. *Appearance Tab*: Selecting a different font updates typography immediately and persists after logging out and back in.

### 6.3. Data Management Page
- **Description**: File manager and browser-based spreadsheet editor.
- **Acceptance Criteria**:
  1. Uploading a valid CSV or `.xlsx` file (<50MB, $\le$50,000 rows) adds the file to the file table with its name, upload date, and size.
  2. Uploading a file larger than 50MB or an unsupported extension (e.g., `.pdf`, `.json`) is rejected with a clear error notification.
  3. Clicking a file opens the spreadsheet viewer displaying tabular rows and columns with pagination and column sorting.
  4. In the spreadsheet viewer, clicking a cell allows inline text/number editing; clicking a row action allows row deletion; double-clicking a column header allows renaming.
  5. Clicking "Save Changes" commits all modifications to the stored file; refreshing the page displays the updated data.
  6. Clicking the delete icon on a file row prompts a confirmation dialog; confirming removes the file from storage and the table.

### 6.4. Analysis Page: "Know Your Data" Tab
- **Description**: Initial data audit and exploratory data summary.
- **Acceptance Criteria**:
  1. Selecting an uploaded file generates summary cards indicating total row count, column count, and overall missing value percentage.
  2. Each column is listed with its inferred data type (numerical, categorical, datetime), missing row count, and unique value count.
  3. Selecting a numerical column renders its summary statistics (mean, median, standard deviation, min, max, IQR) and a distribution histogram/boxplot flagging potential outliers.
  4. Displays an interactive correlation matrix heatmap for numerical columns, highlighting correlations greater than $|0.70|$.

### 6.5. Analysis Page: "Predict a Risk" Tab
- **Description**: Question-driven classification workflow with baseline and tuning.
- **Acceptance Criteria**:
  1. Selecting a categorical target column triggers an automated recommendation (e.g., Logistic Regression for simple linear relations, Random Forest for complex non-linear tabular features) accompanied by a 1–2 sentence explanation.
  2. The user can override the recommended algorithm and manually select or unselect feature columns via checkboxes.
  3. The user can select a column designated as "Athlete ID" from a dropdown.
  4. Running the analysis displays a side-by-side comparison between the model and a Dummy (Majority Class) baseline showing PR-AUC, F1-score, Precision, Recall, and Confusion Matrix.
  5. Guardrail warnings fire conditionally as prominent alert banners whenever evaluation criteria are compromised.

### 6.6. Analysis History & Export
- **Description**: Historical analysis logs and shareable outputs.
- **Acceptance Criteria**:
  1. Every executed analysis run is saved to an "Analysis History" panel with timestamp, target column, algorithm used, and key metric summary.
  2. Clicking "Export PDF" generates and downloads a formatted summary document containing dataset info, model selection, baseline comparison, evaluation metrics, and active guardrail warnings.
  3. Clicking "Export CSV" downloads a copy of the original dataset with new appended columns: `predicted_class` and `predicted_risk_probability`.

---

## 7. Guardrails

The application implements five non-bypassable guardrails designed to prevent deceptive or invalid machine learning results:

| # | Guardrail | Purpose | Concrete Trigger Example |
|---|---|---|---|
| 1 | **Baseline Comparison** | Prevents mistaking trivial majority-class accuracy for real predictive utility. | A model predicting hamstring strain achieves 92% raw accuracy. The guardrail places it directly beside a Dummy baseline showing 92% accuracy (achieved by predicting "No Injury" for every row), immediately exposing that the model has learned nothing useful. |
| 2 | **Athlete Group Splitting** | Eliminates data leakage caused by having records of the same athlete in both train and test splits. | A user designates `player_id` as the Athlete ID column. The system splits data using `GroupKFold` so that all 25 rows belonging to "Player #9" are placed strictly in the test set, never divided between train and test. A banner indicates: *"Data split by Athlete ID: No athlete appears in both training and testing sets."* |
| 3 | **Target Leakage Warning** | Detects feature columns that encode outcome knowledge collected post-event. | In an injury prediction task for target `injured` (0/1), a feature named `rehab_sessions_attended` has a Pearson correlation of $0.97$ with the target. The system flags the column in red: *"Warning: 'rehab_sessions_attended' has an extremely high association with the target and may be leaking post-event information. Consider excluding it."* |
| 4 | **Rare Outcome Evaluation Guardrail** | Prevents relying on overall accuracy when the positive class is heavily imbalanced. | The target variable `incurred_concussion` contains only 3% positive cases. The system hides raw accuracy from the primary summary card, highlights **PR-AUC** and **F1-score**, and displays a banner: *"Rare outcome detected (3% positive rate). Raw accuracy is misleading; evaluation is focused on Precision-Recall AUC."* |
| 5 | **Underpowered Test Set Warning** | Flags evaluations where the test sample is too small to yield statistically reliable conclusions. | An 80/20 train/test split on a small squad dataset results in only 4 positive injury cases in the test set. The system displays an orange caution banner: *"Caution: The test set contains fewer than 10 positive cases. Metric estimates have high statistical variance and should be interpreted with extreme care."* |

---

## 8. Constraints and Assumptions

### Constraints
- **Frontend Architecture**: Built using Next.js with shadcn/ui component styling.
- **Analytical Engine**: All statistical and machine learning calculations run on an isolated Python service (FastAPI + scikit-learn) so mathematical output matches PES 3850 Google Colab course materials.
- **Data Privacy & Regulation (KVKK/GDPR)**: Athlete physical and wellness data is sensitive personal health data. No data, metadata, or logs may be sent to third-party cloud services or external AI APIs.
- **Data Persistence**: Local deployment using SQLite for relational state (users, analysis history metadata) and local filesystem storage for uploaded and exported files.
- **File Scale**: Maximum file size limited to 50MB; row count limited to 50,000 rows for responsive in-browser editing and synchronous calculation.

### Assumptions
- Uploaded files are valid tabular CSV or `.xlsx` files with column header names in row 1.
- Users have domain understanding of their data (i.e., can identify which column corresponds to Athlete ID and which represents their target question).
- Administrative deployment handles initial user provisioning and environment configuration.

---

## 9. Success Criteria

1. **Non-Technical Usability**: A PES 3850 student with no coding experience can upload a sports science CSV, inspect and clean missing entries, configure a risk classification model, and download an executive PDF report in under 5 minutes.
2. **Methodological Reliability**: Zero evaluations in student lab testing exhibit athlete split contamination or undetected target leakage when following the guided workflow.
3. **Curriculum Concordance**: Classification metrics and baseline calculations generated by the app replicate scikit-learn Python results from PES 3850 Google Colab notebooks with 100% numerical parity.
4. **Data Isolation Compliance**: 100% of network traffic and file processing remains within the local environment; zero external requests are triggered during data upload, exploration, or modeling.

---

## 10. Open Questions

1. **Automated Imputation Policy**: If a user runs "Predict a risk" without addressing missing values in the spreadsheet viewer, should the app apply automated median/mode imputation with a notification, or require the user to clean the data before proceeding?
2. **Leakage Detection Sensitivity**: What exact statistical threshold should trigger the leakage warning (e.g., Pearson correlation $|r| > 0.90$, mutual information score $> 0.80$, or identical categorical distributions)?
3. **PDF Executive Summary Detail Level**: Should the exported PDF be a high-level 1-page executive summary for coaches, or a multi-page technical report containing full confusion matrix breakdowns and feature importances for academic coursework?

