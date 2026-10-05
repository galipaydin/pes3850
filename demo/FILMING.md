# Filming the Week 1 demo clip

> *Written for whoever runs the session. Students are welcome to read it — it is also a decent
> brief for filming your own movement for the Week 10 laboratory.*

Twenty seconds of video. It is the most important twenty seconds of the semester, because it decides how a third of the room feels about the course.

---

> **Cannot film?** Four licensed clips ship with the course in `clips/` — see `VIDEO-SOURCES.md`. Filming your own is still better: the demo works because the person on screen is real to the room.

## What to film

**A bodyweight squat. Three repetitions. Filmed from the side.**

Why a squat and not something more exciting:

- Everybody in the room knows what a squat is, so nobody is decoding the movement while you talk.
- The knee angle changes a great deal, so the curve you produce has three obvious dips and reads instantly from the back row.
- It is slow, so a 30 fps phone resolves it perfectly.
- It is exactly what students will film themselves in Week 10, which makes the promise you make in Week 1 concrete.

**Who should be in it, in order of preference:**

1. **A student who will be in the room.** Ask permission, and use the course consent form.
2. **A METU athlete or team member** the class would recognise.
3. **You.**
4. A stranger from stock footage — the weakest option. The demo works because the person is real to them.

---

## How to film it

| | |
|---|---|
| **Angle** | Side-on, camera perpendicular to the direction of movement |
| **Camera height** | Roughly hip height. Not looking down from standing |
| **Distance** | The whole body fills most of the frame height, with a little room above and below |
| **Support** | Phone on a bench, a stack of books, a tripod. **Not handheld** |
| **Background** | A plain wall. Not a busy gym with people walking behind |
| **Clothing** | Contrasting with the background. Shorts rather than long trousers if possible |
| **Lighting** | Bright and even. Avoid a bright window directly behind the athlete |
| **Length** | 15 seconds maximum |
| **Resolution** | 720p. Higher is slower and no better for this |
| **Frame rate** | 30 fps is fine for a squat. 60 if your phone offers it |
| **Orientation** | Landscape |

**The two most common mistakes:** the feet are cut off at the bottom of the frame, and the athlete is too small in the picture. Both make the landmark detection unreliable.

---

## Before you film

Get the **consent form** signed. Filming a person and showing it to a class is processing personal data, and Week 13 of your own course is about exactly this. If you cannot demonstrate the standard you teach in the first session, the rest is harder to argue.

For a member of a METU team, check whether the department or the team has its own media policy as well.

---

## After you film

1. Get the file onto a laptop. Do not rely on the phone in the room.
2. Open `demo_pose_live.ipynb` in Google Colab, upload the clip, and run it. If you filmed at 4K or longer than 15 seconds, run section 3c to trim and downscale first.
3. Download the three outputs: `squat_frontal_raise_overlay_web.mp4`, `squat_frontal_raise_knee_angle.png`, `squat_frontal_raise_side_by_side.png`.
4. Put them in the same folder as the slides, on the machine you will teach from.
5. **Play the video once, on that machine, in the room if you can.** Projector audio, aspect ratio and codec problems are all better discovered the day before.

---

## A useful second clip

If you have five spare minutes while filming, shoot the same squat **again from about 30–40° off perpendicular.**

You will not use it in Week 1. You will use it in Week 10, when students discover that the identical movement yields a different measured knee angle depending on where the camera was. Having the two clips be the same person doing the same squat makes that lesson much sharper, and you will not want to re-film in November.

---

## After you film: one command

```bash
python3 run_demo.py my_squat.mov --crop
```

It trims, downscales, finds the leg facing the camera, draws the skeleton, measures the knee angle and writes the three files you project. Everything in the rules above is there because the script measured it going wrong on a real clip — see `VIDEO-SOURCES.md`, where the highest-resolution of the four test clips ranks last because the feet are out of frame.
