# PES 517 — Artificial Intelligence Applications in Sport

**Middle East Technical University · Department of Physical Education and Sports**
elective · laboratory notebooks

---

## For students

Click a badge. The notebook opens in Google Colab — nothing to install, no account needed to look.

**Before you edit anything: `File → Save a copy in Drive`.** Otherwise your work is not saved.

| Week | Lab | |
|---|---|---|
| 1 | Welcome to Google Colab | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab01_colab_onboarding.ipynb) |
| 2 | Prompt-to-notebook: make an LLM write your analysis | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab02_prompt_to_notebook.ipynb) |
| 3 | Clean it, describe it, plot it | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab03_data_literacy.ipynb) |
| 4 | Your first supervised model | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab04_first_supervised_model.ipynb) |
| 5 | Build a leaky model, then fix it | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab05_data_leakage.ipynb) |
| 6 | An injury-risk classifier, honestly | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab06_injury_risk_classifier.ipynb) |
| 7 | Athlete phenotypes | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab07_athlete_phenotypes.ipynb) |
| 9 | Classify your own movement | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab08_wearables_activity_recognition.ipynb) |
| 10 | Your video, your joint angles | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab09_pose_estimation.ipynb) |
| 11 | Tracking and event data | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab10_tracking_and_event_data.ipynb) |
| 12 | A grounded assistant | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab11_grounded_assistant.ipynb) |
| 13 | Audit a real product | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/notebooks/lab12_product_audit.ipynb) |


---

## The opening demonstration — pose estimation

The first session opens with a computer finding a person's hip, knee and ankle in every frame of an ordinary video, and turning it into a knee-angle curve. You can run it yourself:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes517/blob/main/demo/demo_pose_live.ipynb)

Four clips ship with it, so it works immediately — or upload your own video of a squat. By Week 10 you will do exactly this with your own footage, and then measure how wrong it is against a manual reference.

Or run it **live from your own webcam** — the skeleton follows you, with a knee angle that updates thirty times a second, a scrolling trace and a repetition counter:

```bash
pip install mediapipe opencv-python
python3 demo/live_demo.py --check     # test first
python3 demo/live_demo.py             # go
```

Press **SPACE** to freeze a frame mid-squat. Then turn away from the camera and watch the confidence fall — that is the course's first question, measured rather than asserted: *what can the model actually see?*

```
demo/
├── demo_pose_live.ipynb   the Colab notebook above
├── live_demo.py           real time from a webcam
├── run_demo.py            process a video file from the command line
├── clips/                 four freely-licensed clips, attributed in VIDEO-SOURCES.md
├── out/                   the figures, already generated
├── LIVE-DEMO.md           running it live: pre-flight, keys, failure modes
├── FILMING.md             how to film your own: angle, framing, length, consent
└── VIDEO-SOURCES.md       what each clip is, and how well each one tracked
```

**Measured on `squat_frontal_raise.mp4`:** landmarks found in 100% of frames, median confidence 0.94, three repetitions, 134° range of motion. Full results in `demo/out/RESULTS.txt`.

The clips are CC BY / CC BY-SA. If you use them in a presentation, name the creator — the attributions are in `VIDEO-SOURCES.md`.

---

## The syllabus

**[SYLLABUS.md](SYLLABUS.md)** — learning outcomes, the fourteen-week schedule, assessment weights, the policy on using AI tools, required software, and the research-ethics route for term projects.

---

## About these notebooks

**No programming experience is required.** Every notebook is written for you. You change values in cells marked ✏️ **EDIT ME**, run them, and explain what came out. The explanation is what is graded, not the code.

Each notebook follows the same shape:

```
SETUP        pinned installs — never edited
DATA         generated inside the notebook, so nothing can fail to download
LOOK         always look at the data before modelling it
DO           the analysis, pre-written, with a few ✏️ EDIT ME values
SEE          the figures
BREAK IT     change one thing on purpose and watch the damage
INTERPRET    ← this cell is what is marked
AI USE LOG   which tool, what you asked, what you changed or rejected
```

Every dataset is generated by the notebook itself. Nothing is downloaded, so a slow network or a dead link cannot stop you.

---

## If something goes wrong

| | |
|---|---|
| "I lost my work" | You edited the shared notebook instead of your copy. `File → Save a copy in Drive` first, every time. |
| "It says I'm not connected" | Click **Connect**, top right, and wait about fifteen seconds. |
| "The runtime disconnected" | `Runtime → Restart and run all`. Nothing is lost — the notebook is the file. |
| An error you do not understand | Copy the **whole** error message, paste it into ChatGPT, Claude or Gemini, and ask it to explain and fix. That habit is taught in Week 2 and it is the one that makes you self-sufficient. |

---

## Using AI tools

You are expected to use large language models in this course — it is part of the subject matter. Every submission carries an **AI Use Log**: which tool, what you asked, what it produced, and what you changed or rejected. What you rejected says more about your judgement than what you kept.

You remain responsible for every claim in your work. A fabricated citation is treated as a fabricated source.

---

*Course materials for PES 517. Questions: gaydin@firat.edu.tr*
