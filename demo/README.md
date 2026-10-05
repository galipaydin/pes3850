# Week 1 · the opening demo

> *Instructor notes for the Week 1 opening demonstration. The notebook and the clips are
> for anyone; this file explains how the session uses them.*

Slide 6 of `../slides.pptx` says *"The demo — a phone clip of a squat, and a computer finding the knee. No explanation, just watch."* This folder is what makes that ten minutes work.

**Everything is already here.** Four freely-licensed clips are downloaded, the script runs them, and the three files you project are in `out/`.

```bash
cd lectures/week01/demo
pip install mediapipe opencv-python matplotlib pandas
python3 run_demo.py clips/squat_frontal_raise.mp4 --crop
```

**Outputs are named after the clip**, so running it on a second clip never overwrites the first. All four supplied clips have already been processed — `out/` holds twelve files plus `RESULTS.txt`, which records the measured tracking quality of each.

---

## What is in here

| | |
|---|---|
| **`run_demo.py`** | Build the demo from any clip. Auto-picks the visible leg, trims, downscales, crops, writes H.264 |
| **`clips/`** | Four clips, licensed and attributed. See `VIDEO-SOURCES.md` |
| **`out/`** | All four clips already processed — three files each, plus `RESULTS.txt` |
| **`FILMING.md`** | How to film your own, and the consent to get first |
| **`VIDEO-SOURCES.md`** | What each clip is, measured tracking quality, and which to use |
| **`demo_pose_live.ipynb`** | The same thing in Google Colab — [open it](https://colab.research.google.com/github/galipaydin/pes517/blob/main/demo/demo_pose_live.ipynb). Downloads the clips from the public repo, so nothing needs uploading |

---

## What to show, in this order

| # | What | What you say |
|---|---|---|
| 1 | `out/squat_frontal_raise_side_by_side.png` | Nothing. Five full seconds of silence. Let them look. |
| 2 | `out/squat_frontal_raise_overlay_web.mp4` | "This is [name], on a phone." Play it **twice**. |
| 3 | `out/squat_frontal_raise_knee_angle.png` | Point at the three peaks: *"those are the three squats."* |

Those three are from `squat_frontal_raise.mp4`, which is the clip to use — see `VIDEO-SOURCES.md` for why it beats the one that tracks best. The other nine files in `out/` are the same three products for the other clips, kept so you can compare.

Then the three facts and the promise, on slide 7.

## The rule

> **Never install software in front of twenty students.**

The outputs are already generated. In class you play a video file and show two images, and nothing can fail. If you also want to run it live, do that *after* showing the saved outputs.

---

## Which library, and why it was rewritten

**MediaPipe Pose Landmarker through the Tasks API** — 33 landmarks including heel and foot index, CPU-only, Apache 2.0, and the same tool Week 10's lab uses.

⚠️ **This was rewritten in October 2026, and the rewrite was necessary rather than cosmetic.** The first version used `mp.solutions.pose`, MediaPipe's legacy Solutions API. Verified on MediaPipe 1.0.1:

```
>>> import mediapipe as mp; mp.solutions
AttributeError: module 'mediapipe' has no attribute 'solutions'
```

It is not deprecated, it is **gone**. Any notebook calling it fails the moment someone runs `pip install mediapipe`. Almost every MediaPipe tutorial online is still written against it; if you adapt code from a blog post and it says `mp.solutions.anything`, it is dead.

### A version trap worth knowing about

| | |
|---|---|
| **MediaPipe 1.0.1** | Tasks API only. **Crashes on macOS Apple silicon** — the graph reaches for a Metal service that is not there and aborts the process. Not catchable in Python. |
| **MediaPipe 0.10.18** | Same Tasks API, works on macOS. What this script was tested on. |
| **Google Colab** | Linux, unaffected. The notebook installs unpinned and is fine. |

`run_demo.py` detects the crash in a subprocess before it can kill your run, and tells you to install 0.10.18. You do not have to remember any of this — but if you are on a Mac and something aborts with `DrishtiMetalHelper`, that is what happened.

---

## The script

```
python3 run_demo.py CLIP [CLIP ...] [options]

  --out DIR        where to write        (default: out)
  --crop           auto-crop to the athlete so the slide reads from the back row
  --side auto|left|right    which leg to measure (default: auto)
  --seconds N      trim to N seconds     (default: 12)
  --height N       downscale to N px     (default: 720)
  --model lite|full|heavy                (default: full)
  --compare        rank several clips instead of writing figures
```

It handles the things that otherwise cost you the session: 4K stock footage that would take minutes to process, OpenCV writing an `mpeg4` file that half of all players refuse, and — the one nobody predicts — **measuring the leg that is facing away from the camera.**

---

## Optional: a second, three-minute demo

**Teachable Machine** (teachablemachine.withgoogle.com) trains a three-class classifier from your webcam in about sixty seconds, with no code. Show three positions — standing, half squat, bottom — record roughly twenty examples of each, train, and point the camera at yourself.

It dramatises the sentence the whole first half of the course is built on: **we stop writing the rules and start supplying examples.** Students watch you supply the examples, and a working classifier appears. Nothing was programmed.

Keep it to three minutes. It is an aside, not a tool the course uses again.

Section 8 of the notebook adds a different optional aside: **YOLO26-pose** (Ultralytics, January 2026), two lines of code and several people at once — carrying an **AGPL-3.0 licence** that is a live instance of the Week 13 and Week 14 point that what stops a club deploying a model is frequently the licence rather than the accuracy.
