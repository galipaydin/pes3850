# PES 517 — Artificial Intelligence Applications in Sport

**Middle East Technical University · Faculty of Education · Department of Physical Education and Sports**
Elective · open to undergraduate and graduate students · Fall 2026‑2027

| | |
|---|---|
| **Course code** | PES 517 (proposed) — **see the note on dual-level numbering below** |
| **Credits** | 3 (2‑2) — 2 h lecture + 2 h computer lab per week |
| **ECTS** | 8.0 *(confirm with the department; most PES 5XX courses are catalogued at 8.0)* |
| **Level** | Undergraduate and graduate, open to students from other departments |
| **Language of instruction** | English |
| **Prerequisites** | None. No programming or mathematics background is assumed. |
| **Class size** | 20 (cap recommended — lab-based) |
| **Delivery** | Face-to-face; every session includes a hands-on Google Colab lab |
| **Platform** | Google Colab (free tier) + ODTÜClass + shared Google Drive |
| **Instructor** | Galip Aydın · gaydin@firat.edu.tr |
| **Office hours** | 2 h/week, by appointment + 1 open "lab clinic" hour before each deliverable |

---

> **A note on the course code.** PES 517 sits in the PES 5XX series, which is the graduate series. A course taken by both undergraduate and graduate students normally needs either dual numbering — an undergraduate code and a graduate code for the same meetings, such as PES 4XX / PES 5XX — or registration under an undergraduate code with graduate credit arranged separately. **Confirm the mechanism with the department and the Registrar before the catalogue entry is submitted.** Everything else in this package works unchanged under either arrangement; only the code and the catalogue entry depend on it.

## 1. Catalogue description

A practice-oriented introduction to artificial intelligence for sport science professionals. The course covers the conceptual foundations of artificial intelligence, machine learning and large language models, and then applies them to real problems in performance analysis, athlete monitoring, injury risk, biomechanics, tactical analysis and sport organisations. Students work every week in Google Colab notebooks that are supplied pre-written, so that no prior programming experience is required. Emphasis is placed on correct interpretation, honest model evaluation, and the ethical and legal handling of athlete data, rather than on algorithm implementation. Assessment is by weekly laboratory submissions, article critiques, a midterm examination and a team term project.

## 2. Rationale and positioning

Sport science students and graduates are now routinely asked to buy, evaluate, supervise or defend AI systems: markerless motion capture, injury-risk dashboards, tracking providers, automated video tagging, LLM-generated training plans. Very few of them will ever build such a system, and almost none need to. What they do need is the ability to **judge** one — to know what the model was trained on, whether the reported accuracy is real, what it will do when it fails, and who is accountable for the athlete's data.

This course is therefore deliberately **problem-first and tool-assisted**, not algorithm-first and code-first. Students run and modify working code; they do not write software from scratch. The intellectual work assessed is framing, evaluation, interpretation and critique.

## 3. Course learning outcomes

On successful completion, a student will be able to:

**CLO1.** Distinguish artificial intelligence, machine learning, deep learning and generative AI / large language models, and correctly place a given sport technology within that taxonomy.

**CLO2.** Describe the main sources of sport data (event, optical tracking, GPS/LPS, IMU, physiological, video, questionnaire) and evaluate a dataset's suitability, quality, sampling properties and limitations for a stated question.

**CLO3.** Execute, modify and interpret a supervised and an unsupervised machine-learning workflow in Google Colab using low-code tooling, and report results with appropriate performance metrics.

**CLO4.** Diagnose the failure modes that invalidate most published sport-AI models — overfitting, data leakage, class imbalance, inadequate validation, insufficient sample size, distribution shift — and propose corrections.

**CLO5.** Apply computer-vision tools (pose estimation, object detection and tracking) to sport video and state the accuracy limits of the resulting kinematic or spatial measures relative to laboratory reference methods.

**CLO6.** Use large language models productively and safely for literature work, code generation, content drafting and data interpretation, and design an evaluation that exposes hallucination and bias.

**CLO7.** Analyse the ethical, legal and governance dimensions of an AI application in sport — consent, biometric and health data, athlete data sovereignty, algorithmic bias, accountability — with reference to GDPR/KVKK and the EU AI Act.

**CLO8.** Scope, prototype and defend an AI solution to an authentic sport problem, and communicate it to a non-technical decision-maker (coach, club manager, federation).

### Alignment with programme outcomes

| CLO | Contributes to |
|---|---|
| CLO1, CLO2 | Disciplinary knowledge; research methods literacy |
| CLO3, CLO4 | Quantitative analysis; critical evaluation of evidence |
| CLO5 | Measurement and assessment in sport science |
| CLO6, CLO8 | Scientific communication; professional practice |
| CLO7 | Research ethics; professional responsibility |

## 4. Weekly schedule (14 weeks)

| Wk | Topic | Lab (Google Colab) | Due |
|---|---|---|---|
| 1 | What AI actually is: AI / ML / DL / GenAI, and the sport landscape | **Lab 1** Colab onboarding + run a pretrained model on a sport clip | — |
| 2 | Large language models as a working tool: how they work, prompting, hallucination | **Lab 2** Prompt-to-notebook: get an LLM to write and debug your analysis code | Lab 1 |
| 3 | Sport data literacy: sources, structure, quality, units, missingness | **Lab 3** Load, clean, describe and plot a training-load dataset | Lab 2 |
| 4 | Supervised learning: features, labels, train/test, the first model | **Lab 4** Predict a performance outcome; compare with linear regression | Lab 3 |
| 5 | Honest evaluation: overfitting, cross-validation, **data leakage**, metrics | **Lab 5** Build a leaky model that scores AUC 0.93, then fix it | Lab 4 · Critique 1 |
| 6 | Classification and risk models: injury risk, talent ID, return-to-play | **Lab 6** Injury-risk classifier; confusion matrix, thresholds, cost of errors | Lab 5 |
| 7 | Unsupervised learning: clustering, PCA, athlete profiling, segmentation | **Lab 7** Cluster a physical test battery into athlete phenotypes | Lab 6 |
| 8 | **Midterm examination** (75 min) + term-project scoping workshop | Project clinic | Lab 7 · **Project proposal** |
| 9 | Wearables and time series: IMU, sampling, windowing, activity recognition | **Lab 8** Record your own movement with a phone; classify walk/run/jump | — |
| 10 | Computer vision I: pose estimation and markerless biomechanics | **Lab 9** Your own squat/CMJ video → joint angles; validate against Kinovea | Lab 8 |
| 11 | Computer vision II: detection, tracking, event and tactical analysis | **Lab 10** Track players in a clip; build a pitch map from open event data | Lab 9 · Critique 2 |
| 12 | Applied LLMs: retrieval over your own literature, assistants, evaluation | **Lab 11** Build a grounded Q&A assistant over sport-science PDFs | Lab 10 |
| 13 | Ethics, privacy, governance, bias; AI in officiating and regulation | **Lab 12** Audit a real sport-AI product against an ethics checklist | Lab 11 |
| 14 | **Project presentations** + adoption in real organisations; course wrap | Demo session | Lab 12 · **Final report** |

*A detailed session-by-session breakdown — objectives, lecture outline, lab specification, dataset, deliverable and readings — is in `02-weekly-course-content.md`.*

## 5. Assessment

| Component | Weight | Notes |
|---|---|---|
| Weekly laboratory submissions | **30%** | 12 labs; best 10 count. Colab link + 150-word interpretation. |
| Article critiques (2 × 5%) | **10%** | One page each, structured reviewer checklist. |
| Midterm examination (Week 8) | **20%** | 75 min, open-book, no internet/LLM. Concepts and interpretation, not code recall. |
| Term project | **35%** | Proposal 5% · Presentation + demo 10% · Final report 20%. Teams of 2. |
| Participation and lab engagement | **5%** | In-class discussion, peer help, project peer review. |

**Passing:** overall ≥ 60/100 **and** at least 8 of 12 labs submitted. Letter grades per METU regulations.

### What differs between undergraduate and graduate students

The weights above are identical for both, and so is almost everything else. **One** component differs.

| | Undergraduate | Graduate |
|---|---|---|
| **Weekly labs** | Identical | Identical |
| **Midterm** | Same paper, same marking | Same paper, same marking |
| **Article critiques** | Identical — two critiques, 5% each | Identical |
| **Term project** (35%) | Report of **2000 words** | Report of **3000 words**, with an additional section positioning the work against **at least three published studies** |
| **Participation** | Identical | Identical |

Everything else — the laboratory sessions, the article critiques, the project brief, the rubric criteria and the weightings — is the same for everyone. Graduate students are not given more work for its own sake; they are asked for the one thing a graduate course has to demand, which is awareness of where their own work sits in the published literature.

Full rubrics, the project brief and the exam blueprint are in `04-assessment-and-rubrics.md`.

## 6. Policy on the use of AI tools

You are expected to use large language models in this course. That is part of the subject matter. The conditions are:

1. **Labs and project — LLM use is permitted and encouraged.** Every submission must include a short **AI Use Log** appendix: which tool, what you asked it, what it produced, and what you changed or rejected. A submission with no log is treated as claiming no AI use; if AI use is later evident, it is an academic-integrity matter.
2. **You own every claim in your submission.** "The model said so" is not a defence for a wrong number, a fabricated citation or a nonsensical interpretation. Hallucinated references are treated as fabricated sources.
3. **Midterm — no LLM, no internet.** The exam tests what you can judge without assistance.
4. **Article critiques — LLM may be used for language, not for reading.** The critique must reflect your reading of the paper.

## 7. Software, accounts and equipment

Bring a laptop to every session. Everything runs in the browser; nothing needs to be installed.

- **Google account** (personal or METU) for Google Colab and Drive — free tier is sufficient for the whole course.
- **An LLM account**: ChatGPT, Claude or Gemini free tier; Google NotebookLM (free).
- **Smartphone** with a camera and a free sensor-logging app (Phyphox or SensorLog) — used in Weeks 9 and 10.
- **Kinovea** (free, Windows) for Week 10 — a lab machine will be available for macOS users.
- Optional free accounts: Roboflow, Teachable Machine, Hugging Face.

No paid subscription is required. Where a paid tier would help, a free fallback is provided in the notebook.

## 8. Course materials

There is no single textbook. Each week has one required reading (10–20 pages) and optional depth material; all are open access or supplied through ODTÜClass. Recommended background references:

- *Artificial Intelligence and Machine Learning in Sports Science* (Springer, 2025) — edited volume, chapter-level use.
- "Artificial Intelligence and Machine Learning in Sport Research: An Introduction for Non-data Scientists," *Frontiers in Sports and Active Living* (2021) — the conceptual spine of Weeks 1 and 4–7.
- "Large Language Models in Sport Science & Medicine: Opportunities, Risks and Considerations" (arXiv 2305.03851) — Weeks 2 and 12.
- "Ethical implications of artificial intelligence in sport: a systematic scoping review," *Journal of Sport and Health Science* (2025) — Week 13.

The full reading list, dataset catalogue and tool links are in `05-resources-datasets-readings.md`.

## 9. Research ethics for student projects

If your term project involves **recording video of people, collecting sensor or physiological data from people, or using an identifiable athlete's data**, you must either (a) use one of the approved open datasets listed in the resources file, or (b) obtain approval from the **METU Human Subjects Ethics Committee (İnsan Araştırmaları Etik Kurulu)** before collecting anything. A template participant information sheet and consent form is provided in Week 8. Self-recording (you filming yourself) and recording consenting classmates for in-class labs is covered by a course-level consent form signed in Week 1; that consent does **not** extend to publishing the footage.

## 10. Attendance, late work and accessibility

- **Attendance:** 70% minimum, per METU regulations. The lab cannot be replicated at home in the same way, but all notebooks remain available.
- **Late labs:** accepted up to 7 days late at 70% credit; after that, use one of your two dropped labs. Project deadlines are firm.
- **Accessibility:** students registered with the METU Disability Support Office should contact the instructor in Week 1; notebooks can be supplied with screen-reader-friendly output and extended lab time is available.
- **Academic integrity:** METU Student Disciplinary Regulations apply. Sharing a notebook link with a teammate is collaboration; submitting a classmate's interpretation text as your own is plagiarism.
