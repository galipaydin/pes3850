# Pose estimation demo

A computer finds a person's hip, knee and ankle in every frame of an ordinary video, and turns it into a knee-angle curve. This is what Week 1 opens with, and what you build on properly in Week 10.

---

## Run it in Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/galipaydin/pes3850/blob/main/demo/demo_pose_live.ipynb)

Nothing to install. Four clips come with it, so it works straight away — or upload your own.

## Or run it on your own machine

```bash
pip install mediapipe opencv-python matplotlib pandas

python3 run_demo.py clips/squat_frontal_raise.mp4 --crop    # from a video file
python3 live_demo.py --check                                # test your webcam
python3 live_demo.py                                        # live, from the webcam
```

`live_demo.py` shows the skeleton following you in real time with a knee angle, a scrolling trace and a repetition counter. **SPACE** freezes a frame, **f** is full screen, **h** lists the keys, **q** quits.

If the keys do nothing, click the window — OpenCV only sees them while its own window has focus. Ctrl+C in the terminal and the window's close button both work regardless.

Try turning side on to the camera and then rotating slowly. The confidence number falls, and below 0.50 the panel says *the model is guessing*. That is the course's first question — what can the model actually see? — answered as a measurement rather than a claim.

---

## Filming your own

| | |
|---|---|
| **Angle** | Side on, camera perpendicular to the movement |
| **Framing** | Whole body in frame, feet included. This is the one people get wrong |
| **Camera** | On something fixed. Not handheld |
| **Background** | Plain. Not a busy gym with people moving behind |
| **Length** | 15 seconds at most, 720p at most |
| **Frame rate** | 60 fps if your phone offers it |

If you film anyone other than yourself, ask them first.

---

## The clips

| File | What it is | Measured confidence |
|---|---|---|
| `squat_frontal_raise.mp4` | Kettlebell goblet squats, side on, whole body visible | **0.94** · 3 repetitions |
| `squat_single_leg.mp4` | Single-leg squat outdoors | 0.99 · 1 repetition |
| `squat_demo.mp4` | Barbell squat — **feet out of frame**, which is why it tracks worst | 0.78 |
| `sports2d_demo.mp4` | Walking, backlit, several people — deliberately difficult | 0.92 |

Full numbers in `out/RESULTS.txt`. Start with the first one.

Notice that `squat_demo.mp4` has the highest resolution of the four and tracks worst. The feet are cut off at the bottom of the frame, so the ankle is guessed rather than seen — which is why the framing rule above matters more than the camera does.

### Credits

The clips are used under their licences, which require attribution:

- `squat_frontal_raise.mp4` — Taco Fleur, Cavemantraining · CC BY-SA 4.0 · Wikimedia Commons
- `squat_single_leg.mp4` — Ricky Bennison · CC BY-SA 4.0 · Wikimedia Commons
- `squat_demo.mp4` — FitnessScape · CC BY 3.0 · Wikimedia Commons
- `sports2d_demo.mp4` — [Sports2D](https://github.com/davidpagnon/Sports2D) · BSD-3-Clause

If you reuse a clip in a presentation, carry the credit with it.

---

## A note on the library

This uses **MediaPipe Pose Landmarker through the Tasks API**. The older `mp.solutions.pose` interface was removed in MediaPipe 1.0 and raises `AttributeError` on a current install — most tutorials you find online are still written against it and will not run.

On macOS with Apple silicon, MediaPipe 1.0.x aborts with a Metal error that cannot be caught from Python. Install `mediapipe==0.10.18`, which has the same Tasks API and works. Colab runs Linux and is unaffected.
