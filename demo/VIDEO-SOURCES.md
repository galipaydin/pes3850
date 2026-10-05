# The demo clips

> *Written for whoever runs the session. Students are welcome to read it — it is also a decent
> brief for filming your own movement for the Week 10 laboratory.*

Four clips are **already downloaded** in `clips/`. All four are freely licensed and were obtained programmatically, so nothing here depends on a link still working in a year.

I ran every one of them through `run_demo.py` on 5 October 2026. The numbers below are measured, not estimated.

---

## What is in `clips/`

| File | What it shows | Licence | Source |
|---|---|---|---|
| **`squat_frontal_raise.mp4`** | Man doing kettlebell goblet squats, **side on, barefoot, whole body in frame**. 640×480, 28 s | CC BY-SA 4.0 — *Taco Fleur, Cavemantraining* | Wikimedia Commons |
| `squat_single_leg.mp4` | Single-leg squat outdoors against sky and grass. 480×640 vertical, 7.9 s | CC BY-SA 4.0 — *Ricky Bennison* | Wikimedia Commons |
| `squat_demo.mp4` | Barbell back squat, three-quarter rear view, **feet cut off at the bottom of frame**. 1280×720, 7.1 s | CC BY 3.0 — *FitnessScape* | Wikimedia Commons |
| `sports2d_demo.mp4` | A person walking in the sagittal plane, a second person backlit doing a flip, a third flickering in the background. 1768×994, 7.7 s | BSD-3-Clause | [Sports2D](https://github.com/davidpagnon/Sports2D) |

The CC BY and CC BY-SA licences require **attribution**. Put the creator's name on the slide — one line, and it models the behaviour you will ask students for all semester.

---

## How they actually performed

```
                   clip  side found  vis foot_vis peak  rom  reps score
   squat_single_leg.mp4  left  100% 0.99     0.99 124°  56°     1 0.981
squat_frontal_raise.mp4  left  100% 0.94     0.94 143° 138°     3 0.891
      sports2d_demo.mp4 right   96% 0.92     0.92 105° 103°     3 0.811
         squat_demo.mp4 right  100% 0.90     0.78 137° 137°     2 0.701
```

`vis` is the model's own median confidence in the hip, knee and ankle; `foot_vis` is confidence in the foot. Reproduce with:

```bash
python3 run_demo.py clips/*.mp4 --compare
```

---

## Use `squat_frontal_raise.mp4`

It is not top of the ranking, and it is still the right choice. **The score measures how well the model tracks, not how good a teaching clip it is.**

| | |
|---|---|
| **Three clean repetitions** in twelve seconds | The curve has three unmistakable peaks that read from the back row. `squat_single_leg` gives you one. |
| **A movement everybody recognises** | A bilateral squat needs no explanation. A single-leg squat invites questions about the movement instead of about the technology. |
| **138° range of motion** | A big, obvious signal. |
| **Barefoot, whole body in frame** | The foot landmarks are tracked at 0.94 confidence, so the ankle is measured rather than guessed. |
| Confidence 0.94 across the whole clip | Nothing to apologise for on screen. |

**All four clips are already processed.** `out/` holds three files for each, named after the clip, plus `RESULTS.txt` recording every measurement below. To rebuild:

```bash
python3 run_demo.py clips/squat_frontal_raise.mp4 --crop
```

Outputs carry the clip's name (`squat_frontal_raise_knee_angle.png` and so on), so running it on a second clip never overwrites the first.

`--crop` matters here. The athlete occupies about a third of the original frame; cropping to the body makes the skeleton readable on a projector.

### Measured output

```
side     : left  (visibility right 0.43 · left 0.91)
crop     : 462x530 from 960x720  (35% of the frame)
landmarks: 100% of frames · median confidence 0.94 (foot 0.94)
knee     : peak 141° · range 134° · 3 reps detected
```

---

## Two things worth saying out loud in class

### The model found the left leg, not the right

The script defaults to `--side auto` because it matters more than you would expect. On this clip the athlete faces left, so the camera sees the left side of the body and the right leg is partly hidden behind it:

| | right leg | left leg |
|---|---|---|
| Median confidence | **0.43** | **0.91** |

Same video, same model, same frame. **The visible side is measured twice as confidently as the hidden one.** That is occlusion, demonstrated in one number — and it is a straight line to Week 10, where students learn that a single camera can only measure what it can see.

### `squat_demo.mp4` is a worked example of bad filming

It has the highest resolution of the four and ranks last. Three reasons, all of which are in `FILMING.md` as rules:

1. **The feet are cut off** at the bottom of the frame, so the ankle is inferred. Foot confidence drops to 0.78, the lowest of the four.
2. **A barbell crosses the shoulders**, hiding landmarks.
3. **Three-quarter rear view**, not a clean sagittal view.

If you want a thirty-second aside on why the filming rules exist, run the comparison live and point at the last row.

---

## If you want to film your own instead

You should, and `FILMING.md` tells you how. The demo is stronger when the person on the screen is somebody in the room. These four clips are the backup for the week the student who agreed to be filmed does not turn up.

Your own clip goes through exactly the same command:

```bash
python3 run_demo.py my_squat.mov --crop
```

---

## If you want different stock footage

**Wikimedia Commons** is the only source here that can be searched and downloaded by script — Pexels and Pixabay both block automated requests, so their clips cannot be fetched this way and the links rot. Commons also states the licence in machine-readable form.

```bash
curl -s "https://commons.wikimedia.org/w/api.php?action=query&format=json\
&list=search&srsearch=squat+exercise+filetype:video&srnamespace=6&srlimit=10"
```

Then take `imageinfo.url` for the file you want.

**What to look for, in priority order:** side on · whole body including feet · one person · plain background · fixed camera · ten seconds is plenty.

**What to avoid:** barbells across the shoulders, anything filmed from behind, feet out of frame, and slow motion, which distorts the time axis of the knee-angle curve.

---

*Clips downloaded and measured 5 October 2026 with MediaPipe 0.10.18 on macOS. The files are in the repository, so these results do not depend on anything staying online.*
