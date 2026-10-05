#!/usr/bin/env python3
"""
PES 517 · Week 1 — LIVE pose estimation from a webcam, for the lecture room.

A full-screen window: the skeleton on the left, a scrolling knee-angle trace on
the right, a large angle readout and a repetition counter. Designed to be read
from the back row and operated with one hand while you talk.

    python3 live_demo.py                 # default camera
    python3 live_demo.py --check         # test everything, change nothing
    python3 live_demo.py --camera 1      # a second camera
    python3 live_demo.py --source clips/squat_frontal_raise.mp4   # no camera

KEYS
    SPACE  freeze / unfreeze       f  full screen
    s      save a screenshot       r  reset the trace and the rep counter
    m      mirror on / off         l  switch leg (left / right / auto)
    h      hide the panel          q or ESC  quit

BEFORE THE LECTURE run  python3 live_demo.py --check  on the room's machine.
On macOS the first run triggers a camera permission prompt. Do not let twenty
students watch you click through it.
"""
from __future__ import annotations
import argparse, sys, time
from collections import deque
from pathlib import Path

import cv2
import numpy as np

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
             "pose_landmarker_{size}/float16/latest/pose_landmarker_{size}.task")

SIDES = {"right": dict(hip=24, knee=26, ankle=28, foot=32),
         "left":  dict(hip=23, knee=25, ankle=27, foot=31)}
EDGES = [(11, 12), (11, 23), (12, 24), (23, 24),
         (11, 13), (13, 15), (12, 14), (14, 16),
         (23, 25), (25, 27), (27, 29), (29, 31), (27, 31),
         (24, 26), (26, 28), (28, 30), (30, 32), (28, 32)]

# BGR. Matches the course palette.
MAROON = (43, 28, 138)
TEAL   = (112, 100, 27)
AMBER  = (20, 87, 154)
INK    = (26, 26, 30)
PAPER  = (249, 251, 252)
GREY   = (120, 112, 108)
WHITE  = (255, 255, 255)

WIN = "PES 517 — live pose estimation"


def fetch_model(size: str) -> Path:
    path = Path(f"pose_landmarker_{size}.task")
    if path.exists() and path.stat().st_size > 1_000_000:
        return path
    print(f"downloading {path.name} ...", end=" ", flush=True)
    import urllib.request
    urllib.request.urlretrieve(MODEL_URL.format(size=size), path)
    print(f"{path.stat().st_size/1e6:.1f} MB")
    return path


def knee_angle(lm, ix) -> float:
    hip, knee, ank = lm[ix["hip"]], lm[ix["knee"]], lm[ix["ankle"]]
    t = np.array([hip.x - knee.x, hip.y - knee.y])
    s = np.array([ank.x - knee.x, ank.y - knee.y])
    n = np.linalg.norm(t) * np.linalg.norm(s)
    if n == 0:
        return 0.0
    return 180 - float(np.degrees(np.arccos(np.clip(t @ s / n, -1, 1))))


def side_visibility(lm, ix) -> float:
    return min(lm[ix[k]].visibility for k in ("hip", "knee", "ankle", "foot"))


def draw_skeleton(img, lm, dim: bool = False) -> None:
    h, w = img.shape[:2]
    pt = lambda i: (int(lm[i].x * w), int(lm[i].y * h))
    thick = max(2, int(w / 320))
    for a, b in EDGES:
        if min(lm[a].visibility, lm[b].visibility) < 0.3:
            continue
        cv2.line(img, pt(a), pt(b), WHITE, thick + 3, cv2.LINE_AA)
        cv2.line(img, pt(a), pt(b), GREY if dim else TEAL, thick, cv2.LINE_AA)
    for i in range(11, 33):
        if lm[i].visibility < 0.3:
            continue
        cv2.circle(img, pt(i), thick + 4, WHITE, -1, cv2.LINE_AA)
        cv2.circle(img, pt(i), thick + 1, GREY if dim else MAROON, -1, cv2.LINE_AA)


def highlight_knee(img, lm, ix) -> None:
    h, w = img.shape[:2]
    pt = lambda i: (int(lm[i].x * w), int(lm[i].y * h))
    r = max(10, int(w / 90))
    for a, b in ((ix["hip"], ix["knee"]), (ix["knee"], ix["ankle"])):
        cv2.line(img, pt(a), pt(b), AMBER, max(3, int(w / 260)), cv2.LINE_AA)
    cv2.circle(img, pt(ix["knee"]), r, AMBER, -1, cv2.LINE_AA)
    cv2.circle(img, pt(ix["knee"]), r, WHITE, 2, cv2.LINE_AA)


def text(img, s, org, scale, color, thick=2, shadow=True):
    f = cv2.FONT_HERSHEY_SIMPLEX
    if shadow:
        cv2.putText(img, s, (org[0] + 2, org[1] + 2), f, scale, (0, 0, 0), thick + 2, cv2.LINE_AA)
    cv2.putText(img, s, org, f, scale, color, thick, cv2.LINE_AA)


def trace_panel(w, h, hist, angle, reps, vis, side, paused):
    """The right-hand panel: live readout plus a scrolling angle trace."""
    p = np.full((h, w, 3), PAPER, np.uint8)
    pad = int(w * 0.07)
    s = w / 420.0                                   # scale everything off width

    text(p, "KNEE FLEXION", (pad, int(h * 0.09)), 0.62 * s, GREY, 1, shadow=False)
    col = MAROON if vis >= 0.5 else GREY
    num = f"{angle:.0f}"
    scale_n, thick_n = 3.3 * s, max(2, int(6 * s))
    (nw, _), _ = cv2.getTextSize(num, cv2.FONT_HERSHEY_SIMPLEX, scale_n, thick_n)
    ybase = int(h * 0.235)
    text(p, num, (pad, ybase), scale_n, col, thick_n, shadow=False)
    text(p, "deg", (pad + nw + int(14 * s), ybase), 0.95 * s, GREY, 2, shadow=False)

    text(p, "REPETITIONS", (pad, int(h * 0.325)), 0.62 * s, GREY, 1, shadow=False)
    text(p, f"{reps}", (pad, int(h * 0.425)), 2.4 * s, TEAL, int(5*s), shadow=False)

    text(p, f"{side.upper()} LEG", (pad + int(165*s), int(h * 0.325)), 0.62 * s, GREY, 1, shadow=False)
    conf_col = TEAL if vis >= 0.7 else (AMBER if vis >= 0.5 else MAROON)
    text(p, f"{vis:.2f}", (pad + int(165*s), int(h * 0.405)), 1.5 * s, conf_col, int(3*s), shadow=False)
    text(p, "confidence", (pad + int(165*s), int(h * 0.432)), 0.46 * s, GREY, 1, shadow=False)
    if vis < 0.5:
        text(p, "the model is guessing", (pad, int(h * 0.468)), 0.52 * s, MAROON, 1, shadow=False)

    # ── trace ──
    gx0, gx1 = pad, w - pad
    gy0, gy1 = int(h * 0.53), int(h * 0.90)
    cv2.rectangle(p, (gx0, gy0), (gx1, gy1), (226, 232, 236), -1)
    for frac, lab in ((0.0, "0"), (0.5, "70"), (1.0, "140")):
        y = int(gy1 - frac * (gy1 - gy0))
        cv2.line(p, (gx0, y), (gx1, y), (205, 213, 219), 1, cv2.LINE_AA)
        text(p, lab, (gx0 - int(30*s), y + int(5*s)), 0.44 * s, GREY, 1, shadow=False)

    if len(hist) > 1:
        n = len(hist)
        pts = [(int(gx0 + i / max(1, hist.maxlen - 1) * (gx1 - gx0)),
                int(gy1 - np.clip(v, 0, 140) / 140 * (gy1 - gy0)))
               for i, v in enumerate(hist)]
        cv2.polylines(p, [np.array(pts, np.int32)], False, MAROON, max(2, int(2.4*s)), cv2.LINE_AA)
        cv2.circle(p, pts[-1], max(4, int(5*s)), MAROON, -1, cv2.LINE_AA)
    text(p, "last 10 seconds", (gx0, gy1 + int(26*s)), 0.46 * s, GREY, 1, shadow=False)

    # shrink the key hint until it fits the panel, and drop items if it still will not
    for hint in ("SPACE freeze | f full | s save | r reset | l leg | h panel | q quit",
                 "SPACE freeze | f full | s save | r reset | q quit",
                 "SPACE freeze | f full | q quit",
                 "SPACE freeze | q quit"):
        hs = 0.40 * s
        (hw, _), _ = cv2.getTextSize(hint, cv2.FONT_HERSHEY_SIMPLEX, hs, 1)
        while hw > w - 2 * pad and hs > 0.22 * s:
            hs *= 0.92
            (hw, _), _ = cv2.getTextSize(hint, cv2.FONT_HERSHEY_SIMPLEX, hs, 1)
        if hw <= w - 2 * pad:
            break
    text(p, hint, (pad, h - int(14*s)), hs, GREY, 1, shadow=False)
    if paused:
        text(p, "FROZEN", (gx1 - int(95*s), int(h * 0.09)), 0.72 * s, AMBER, 2, shadow=False)
    return p


def open_source(args):
    if args.source:
        cap = cv2.VideoCapture(args.source)
        return cap, f"file: {Path(args.source).name}", True
    backend = cv2.CAP_AVFOUNDATION if sys.platform == "darwin" else cv2.CAP_ANY
    cap = cv2.VideoCapture(args.camera, backend)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    return cap, f"camera {args.camera}", False


def check(args) -> int:
    print("PES 517 live demo — pre-flight\n")
    ok = True

    print(f"  python     {sys.version.split()[0]}")
    print(f"  mediapipe  {mp.__version__}")
    print(f"  opencv     {cv2.__version__}")

    try:
        model = fetch_model(args.model)
        print(f"  model      {model.name} ({model.stat().st_size/1e6:.1f} MB)")
    except Exception as e:
        print(f"  model      FAILED — {e}"); return 1

    cap, label, _ = open_source(args)
    if not cap.isOpened():
        print(f"  {label:10s} CANNOT OPEN")
        if sys.platform == "darwin" and not args.source:
            print("\n  On macOS, grant camera access to your terminal:")
            print("    System Settings > Privacy & Security > Camera")
            print("  Then run this check again. If the camera is in use by Zoom or")
            print("  Teams, quit that first.")
        print("\n  Fallback that always works:")
        print("    python3 live_demo.py --source clips/squat_frontal_raise.mp4")
        return 1
    okf, frame = cap.read()
    if not okf:
        print(f"  {label:10s} opened but returned no frame"); cap.release(); return 1
    h, w = frame.shape[:2]
    print(f"  {label:10s} {w}x{h}")

    t0 = time.time(); n = 0
    opts = vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(model)),
        running_mode=vision.RunningMode.VIDEO, num_poses=1)
    found = 0
    with vision.PoseLandmarker.create_from_options(opts) as lm:
        while n < 30:
            okf, frame = cap.read()
            if not okf: break
            img = mp.Image(image_format=mp.ImageFormat.SRGB,
                           data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if lm.detect_for_video(img, int(n / 30 * 1000)).pose_landmarks:
                found += 1
            n += 1
    cap.release()
    fps = n / max(1e-6, time.time() - t0)
    print(f"  speed      {fps:.0f} fps over {n} frames")
    print(f"  detection  person found in {found}/{n} frames")
    if fps < 10:
        print("             ! slow — use --model lite, or --width 640 --height 480")
        ok = False
    if found == 0:
        print("             ! nobody detected. Stand in frame, whole body, good light.")

    print("\n" + ("Ready." if ok else "Usable, but see the warnings above."))
    print("Run it for real:  python3 live_demo.py")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--source", help="a video file instead of a camera")
    ap.add_argument("--model", choices=["lite", "full", "heavy"], default="lite",
                    help="lite is the right choice for live use (default)")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--side", choices=["auto", "left", "right"], default="auto")
    ap.add_argument("--no-mirror", action="store_true")
    ap.add_argument("--check", action="store_true", help="test and exit")
    args = ap.parse_args()

    if args.check:
        sys.exit(check(args))

    model = fetch_model(args.model)
    cap, label, is_file = open_source(args)
    if not cap.isOpened():
        sys.exit(f"Could not open {label}. Run with --check for a diagnosis.")

    opts = vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(model)),
        running_mode=vision.RunningMode.VIDEO, num_poses=1,
        min_pose_detection_confidence=0.5, min_tracking_confidence=0.5)

    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WIN, 1600, 760)
    full = False

    hist = deque(maxlen=300)                 # ~10 s at 30 fps
    vis_r, vis_l = deque(maxlen=60), deque(maxlen=60)   # ~2 s, for the side choice
    reps, armed = 0, True
    mirror = not args.no_mirror
    side = "right" if args.side == "auto" else args.side
    show_panel = True
    paused = False
    frozen = None
    t_prev, fps_s = time.time(), 0.0
    shots = 0
    auto_t = 0.0

    print(f"\nRunning on {label}. Press q to quit, h for the keys.\n")

    with vision.PoseLandmarker.create_from_options(opts) as landmarker:
        t0 = time.time()
        while True:
            if not paused:
                okf, frame = cap.read()
                if not okf:
                    if is_file:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0); continue
                    break
                if mirror and not is_file:
                    frame = cv2.flip(frame, 1)
                frozen = frame.copy()
            else:
                frame = frozen.copy()

            now = time.time()
            res = landmarker.detect_for_video(
                mp.Image(image_format=mp.ImageFormat.SRGB,
                         data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)),
                int((now - t0) * 1000))

            angle, vis = 0.0, 0.0
            if res.pose_landmarks:
                lm = res.pose_landmarks[0]
                vis_r.append(side_visibility(lm, SIDES["right"]))
                vis_l.append(side_visibility(lm, SIDES["left"]))
                # Standing upright, both legs are visible and a single frame cannot tell
                # them apart. The difference only becomes decisive during the movement,
                # so judge on a rolling median and require a clear margin before moving.
                if args.side == "auto" and len(vis_r) >= 20 and now - auto_t > 0.5:
                    auto_t = now
                    mr, ml = float(np.median(vis_r)), float(np.median(vis_l))
                    better = "right" if mr > ml else "left"
                    margin = abs(mr - ml)
                    if better != side and margin > 0.08:
                        side = better
                ix = SIDES[side]
                angle = knee_angle(lm, ix)
                vis = side_visibility(lm, ix)
                draw_skeleton(frame, lm, dim=vis < 0.5)
                if vis >= 0.5:
                    highlight_knee(frame, lm, ix)
                if not paused:
                    hist.append(angle)
                    if armed and angle > 75:
                        reps, armed = reps + 1, False
                    elif angle < 35:
                        armed = True
            elif not paused:
                hist.append(hist[-1] if hist else 0.0)

            fps_s = 0.9 * fps_s + 0.1 / max(1e-6, now - t_prev)
            t_prev = now

            h, w = frame.shape[:2]
            if show_panel:
                pw = int(w * 0.46)
                canvas = np.hstack([frame, trace_panel(pw, h, hist, angle, reps, vis, side, paused)])
            else:
                canvas = frame
            text(canvas, f"{fps_s:4.0f} fps", (12, h - 14), 0.5, WHITE, 1)

            cv2.imshow(WIN, canvas)
            k = cv2.waitKey(1) & 0xFF
            if k in (ord("q"), 27):
                break
            elif k == ord(" "):
                paused = not paused
            elif k == ord("f"):
                full = not full
                cv2.setWindowProperty(WIN, cv2.WND_PROP_FULLSCREEN,
                                      cv2.WINDOW_FULLSCREEN if full else cv2.WINDOW_NORMAL)
            elif k == ord("s"):
                shots += 1
                name = f"live_shot_{shots:02d}.png"
                cv2.imwrite(name, canvas)
                print(f"  saved {name}")
            elif k == ord("r"):
                hist.clear(); reps, armed = 0, True
            elif k == ord("m"):
                mirror = not mirror
            elif k == ord("h"):
                show_panel = not show_panel
            elif k == ord("l"):
                order = ["auto", "left", "right"]
                args.side = order[(order.index(args.side) + 1) % 3]
                if args.side != "auto":
                    side = args.side
                print(f"  side: {args.side}")

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n{reps} repetitions counted.")


if __name__ == "__main__":
    main()
