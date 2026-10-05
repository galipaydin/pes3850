# Running the demo live, from a camera

> *For whoever runs the session.*

`live_demo.py` puts the skeleton, a live knee-angle readout, a scrolling trace and a repetition counter on screen, from a webcam, in real time. It is meant to be projected and operated with one hand while you talk.

---

## The one thing to do before the lecture

```bash
python3 live_demo.py --check
```

On the room's machine, with the room's camera, at least a day before.

**On macOS the first run triggers a camera permission prompt.** You do not want twenty students watching you find System Settings. `--check` triggers it quietly and tells you exactly what to do:

```
  camera 0   CANNOT OPEN

  On macOS, grant camera access to your terminal:
    System Settings > Privacy & Security > Camera
```

A good check looks like this:

```
  model      pose_landmarker_lite.task (5.5 MB)
  camera 0   1280x720
  speed      34 fps over 30 frames
  detection  person found in 30/30 frames

  Ready.
```

Below about 10 fps it will tell you, and the fix is `--model lite` (already the default) or `--width 640 --height 480`.

---

## Running it

```bash
python3 live_demo.py                 # default camera
python3 live_demo.py --camera 1      # an external camera
python3 live_demo.py --model full    # slower, slightly steadier
```

**If the camera fails in the room, it still runs.** Point it at a video instead and nobody needs to know:

```bash
python3 live_demo.py --source clips/squat_frontal_raise.mp4
```

The file loops, so it behaves like a camera for as long as you talk over it. Keep this command on a card.

### Keys

| | |
|---|---|
| **SPACE** | freeze / unfreeze — **the one you will use most** |
| **f** | full screen |
| **s** | save a screenshot |
| **r** | reset the trace and the rep counter |
| **l** | cycle leg: auto → left → right |
| **m** | mirror on / off |
| **h** | hide the panel, video only |
| **q** or **ESC** | quit |

Mirroring is on by default, so moving to your right moves the figure to the audience's right. Turn it off with `m` if you are filming somebody else facing the screen.

---

## How to use it in the session

The scripted route, about four minutes:

**1 · Stand in frame and say nothing.** Let the skeleton appear and follow you. Five seconds of silence does more than any sentence.

**2 · Do three slow squats.** Point at the number as it climbs, then at the trace drawing three peaks, then at the repetition counter. *"Nobody told it what a squat is. It is measuring the angle at my knee, thirty times a second."*

**3 · Press SPACE at the bottom of a squat.** Now the picture holds still and you can talk over it — point at the hip, the knee and the ankle, and say that three points make an angle. This is the moment to explain, and it is why the freeze key exists.

**4 · Then break it on purpose.** This is the part worth rehearsing, because it is the Week 1 lesson rather than a trick:

| Do this | What happens | What to say |
|---|---|---|
| **Turn side on, then rotate slowly** | The confidence number falls; below 0.50 the skeleton goes grey and the panel says *the model is guessing* | "It can only measure what it can see." |
| **Hide one leg behind the other** | Auto-switch moves to the visible leg | "The leg facing the camera is measured twice as confidently as the hidden one." |
| **Step out of frame** | Everything stops | "No data is not the same as zero." |
| **Have a second person step in** | It tracks one of you, and may jump between you | "One person is a solved problem. Twenty-two on a pitch is Week 11." |

**5 · Press `s`** to save a screenshot of the frozen frame, and tell them it will be on ODTÜClass. It costs nothing and they like it.

---

## What it is doing

The same thing as the pre-rendered demo and as the Week 10 laboratory: **MediaPipe Pose Landmarker through the Tasks API**, 33 landmarks, the angle at the knee between the thigh and the shank. The only differences are that the frames come from a camera and the model is the `lite` one, which is quicker and slightly less steady.

The repetition counter is deliberately crude — it counts a repetition when the knee passes 75° and re-arms below 35°. If somebody asks whether that is how commercial systems count repetitions, the honest answer is that many of them are not much more sophisticated, and that the thresholds are somebody's choice. That is Week 9.

---

## When it goes wrong

| | |
|---|---|
| Camera will not open on macOS | System Settings → Privacy & Security → Camera. Quit Zoom or Teams first — they hold the camera. |
| Black window, no image | Another application has the camera. Or try `--camera 1`. |
| Slow and stuttering | `--width 640 --height 480`. The model is already `lite`. |
| Skeleton flickers | Low light. More light helps far more than any setting. |
| It tracks the wrong person | It takes one person. Ask the other to step out of frame. |
| Panel text is cut off | Make the window bigger, or press `f` for full screen. |
| It aborts with `DrishtiMetalHelper` | MediaPipe 1.0.x on macOS Apple silicon. `pip install 'mediapipe==0.10.18'` — `requirements.txt` already pins it. |

---

## Honest limits, if a student asks

It is a 2D estimate from one camera. It cannot see rotation out of the filmed plane, it degrades at speed and in poor light, and the confidence number is the model's own opinion of itself rather than an accuracy measurement. Every one of those is a Week 10 topic, and saying so in Week 1 is better than letting the demo imply otherwise.
