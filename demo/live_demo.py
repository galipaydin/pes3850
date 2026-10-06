#!/usr/bin/env python3
"""
PES 517 · Week 1 — live pose estimation from a webcam.

A full-screen window: the skeleton on the left, a scrolling knee-angle trace on
the right, a large angle readout and a repetition counter.

    python3 live_demo.py                 # default camera
    python3 live_demo.py --check         # test everything, change nothing
    python3 live_demo.py --camera 1      # a second camera
    python3 live_demo.py --source clips/squat_frontal_raise.mp4   # no camera

KEYS
    SPACE  freeze / unfreeze       f  full screen
    s      save a screenshot       r  reset the trace and the rep counter
    m      mirror on / off         l  switch leg (left / right / auto)
    p      hide / show the panel   h  this list, on screen
    q or ESC  quit

Run  python3 live_demo.py --check  first. On macOS the first run triggers a
camera permission prompt, which is easier to deal with before you need it.
"""
from __future__ import annotations
import argparse, subprocess, sys, time
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
    # OpenCV's Hershey fonts are ASCII-only; anything else renders as "?"
    s = s.encode("ascii", "replace").decode("ascii")
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
    for hint in ("SPACE freeze | f big | s save | r reset | l leg | p panel | h keys | q quit",
                 "SPACE freeze | f big | s save | r reset | h keys | q quit",
                 "SPACE freeze | f big | q quit",
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


_SCREEN = None


def screen_size():
    """Logical screen size, measured once, in a SUBPROCESS.

    Creating a tkinter root in this process aborts the whole program once an
    OpenCV window exists — two GUI toolkits cannot both own the macOS main
    thread, and the failure is an NSException that Python cannot catch:

        libc++abi: terminating due to uncaught exception of type NSException

    A subprocess cannot take this process down with it."""
    global _SCREEN
    if _SCREEN is not None:
        return _SCREEN
    _SCREEN = (1920, 1080)
    try:
        out = subprocess.run(
            [sys.executable, "-c",
             "import tkinter;r=tkinter.Tk();r.withdraw();"
             "print(r.winfo_screenwidth(),r.winfo_screenheight())"],
            capture_output=True, text=True, timeout=10)
        w, h = out.stdout.split()
        _SCREEN = (int(w), int(h))
    except Exception as e:
        print(f"  could not read the screen size ({type(e).__name__}); "
              f"assuming {_SCREEN[0]}x{_SCREEN[1]}")
    return _SCREEN


def maximise(win, on: bool):
    """Grow the window to fill the screen, WITHOUT OpenCV's full-screen property.

    cv2.setWindowProperty(..., WND_PROP_FULLSCREEN, ...) is what produced the grey
    band on macOS: the window went full screen but the image was not scaled to
    match, so whatever the canvas did not cover stayed unpainted.

    No display measurement is needed. Asking for a window larger than any screen
    makes the window manager clamp it to what genuinely fits, menu bar and dock
    excluded, and the next window_size() reads back the honest answer."""
    try:
        if on:
            cv2.moveWindow(win, 0, 0)
            cv2.resizeWindow(win, 20000, 20000)
        else:
            cv2.resizeWindow(win, 1600, 760)
            cv2.moveWindow(win, 120, 120)
    except Exception as e:
        print(f"  could not resize the window: {e}")


def window_size(win, full=False, fallback=(1600, 760)):
    """The window's real drawable area, asked of OpenCV.

    This is authoritative and the screen size is not: in full screen the menu bar
    and notch are not drawable, so the display's logical height overshoots and the
    window cannot fit what we drew — which shows up as a band at the top."""
    try:
        x, y, w, h = cv2.getWindowImageRect(win)
        if w > 80 and h > 80:
            # maximise() asks for a window larger than any screen and relies on the
            # window manager to clamp it. Never trust that blindly: an unclamped
            # 20000x20000 canvas is over a gigabyte and would take the demo down.
            sw, sh = screen_size()
            return min(w, sw, 4096), min(h, sh, 2304)
    except Exception:
        pass
    return screen_size() if full else fallback


def fill(frame, tw, th):
    """Centre-crop and scale so the frame exactly fills tw x th. No grey bars."""
    h, w = frame.shape[:2]
    if w == 0 or h == 0:
        return np.full((th, tw, 3), INK, np.uint8)
    scale = max(tw / w, th / h)
    nw, nh = max(tw, int(round(w * scale))), max(th, int(round(h * scale)))
    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    r = cv2.resize(frame, (nw, nh), interpolation=interp)
    x0, y0 = (nw - tw) // 2, (nh - th) // 2
    return r[y0:y0 + th, x0:x0 + tw]


HELP = [("SPACE", "freeze / unfreeze"), ("f", "big window"),
        ("s", "save a screenshot"), ("r", "reset trace and reps"),
        ("l", "switch leg"), ("m", "mirror"),
        ("p", "hide / show the panel"), ("h", "this list"), ("q", "quit")]

FOCUS_HINT = "click the window if keys do nothing"


def draw_help(canvas):
    """Key list, centred, with the box measured from the text rather than guessed."""
    h, w = canvas.shape[:2]
    F = cv2.FONT_HERSHEY_SIMPLEX
    sc = max(0.55, min(1.5, w / 1500.0))
    k_sc, d_sc = 0.70 * sc, 0.62 * sc
    pad, row = int(30 * sc), int(40 * sc)

    k_w = max(cv2.getTextSize(k, F, k_sc, 2)[0][0] for k, _ in HELP)
    d_w = max(cv2.getTextSize(d, F, d_sc, 1)[0][0] for _, d in HELP)
    gap = int(26 * sc)
    bw = pad * 2 + k_w + gap + d_w
    bh = pad + int(34 * sc) + row * len(HELP) + int(26 * sc) + pad

    x0, y0 = (w - bw) // 2, (h - bh) // 2
    x0, y0 = max(0, x0), max(0, y0)
    bw, bh = min(bw, w - x0), min(bh, h - y0)

    box = canvas[y0:y0 + bh, x0:x0 + bw]
    canvas[y0:y0 + bh, x0:x0 + bw] = cv2.addWeighted(
        box, 0.15, np.full_like(box, INK), 0.85, 0)

    text(canvas, "KEYS", (x0 + pad, y0 + pad + int(16 * sc)), 0.58 * sc,
         (165, 165, 172), 1, shadow=False)
    y = y0 + pad + int(34 * sc) + int(22 * sc)
    for key, what in HELP:
        text(canvas, key,  (x0 + pad, y), k_sc, (255, 255, 255), 2, shadow=False)
        text(canvas, what, (x0 + pad + k_w + gap, y), d_sc, (196, 196, 202), 1, shadow=False)
        y += row
    text(canvas, "h closes this", (x0 + pad, y0 + bh - int(14 * sc)),
         0.46 * sc, (140, 140, 148), 1, shadow=False)
    return canvas


def compose(frame, panel_args, win, show_panel, panel_frac=0.30, full=False):
    """Build one image that is exactly the size of the window.

    The camera frame is centre-cropped to fill its area rather than letterboxed,
    so there are never grey bars; what is lost is background at the sides, not
    the person."""
    W, H = window_size(win, full)
    if not show_panel:
        return fill(frame, W, H)
    pw = int(np.clip(W * panel_frac, 280, 700))
    vw = W - pw
    video = fill(frame, vw, H)
    panel = trace_panel(pw, H, *panel_args)
    return np.hstack([video, panel])


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
    sw, sh = screen_size()
    print(f"  screen     {sw}x{sh}  (full screen renders at this size)")
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


def probe():
    """Open the window, go full screen, and report every size involved.

    The grey band at the top of a full-screen window means the canvas we draw and
    the area the window can actually draw into disagree. These numbers say which
    one is wrong; nothing else here can tell us."""
    import numpy as _np
    print("probing the display\n")
    sw, sh = screen_size()
    print(f"  screen (OS)          {sw} x {sh}")

    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WIN, 1600, 760)
    frame = _np.full((760, 1600, 3), INK, _np.uint8)
    for _ in range(8):
        cv2.imshow(WIN, frame); cv2.waitKey(30)
    try:
        print(f"  window rect, windowed {cv2.getWindowImageRect(WIN)}")
    except Exception as e:
        print(f"  window rect, windowed  FAILED: {e}")

    maximise(WIN, True)
    for _ in range(14):
        cv2.imshow(WIN, frame); cv2.waitKey(30)
    try:
        r = cv2.getWindowImageRect(WIN)
        print(f"  window rect, BIG      {r}")
        fw, fh = r[2], r[3]
    except Exception as e:
        print(f"  window rect, BIG       FAILED: {e}"); fw, fh = sw, sh

    # draw a canvas at exactly that size, with corner markers, and hold it
    probe_img = _np.full((fh, fw, 3), (40, 40, 44), _np.uint8)
    cv2.rectangle(probe_img, (0, 0), (fw - 1, fh - 1), (0, 0, 255), 10)
    for (x, y, lab) in ((20, 60, "TOP-LEFT"), (fw - 300, 60, "TOP-RIGHT"),
                        (20, fh - 30, "BOTTOM-LEFT"), (fw - 360, fh - 30, "BOTTOM-RIGHT")):
        text(probe_img, lab, (x, y), 1.0, (255, 255, 255), 2, shadow=False)
    text(probe_img, f"canvas {fw} x {fh}", (int(fw * 0.32), int(fh * 0.5)),
         1.6, (120, 220, 255), 3, shadow=False)
    text(probe_img, "all four red edges visible and no grey band = correct",
         (int(fw * 0.17), int(fh * 0.56)), 0.9, (200, 200, 205), 2, shadow=False)
    text(probe_img, "any key to close", (int(fw * 0.40), int(fh * 0.62)),
         0.8, (150, 150, 158), 1, shadow=False)
    cv2.imshow(WIN, probe_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("\n  If a grey band showed, tell me the two numbers above.")
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
    ap.add_argument("--panel", type=float, default=0.30, metavar="F",
                    help="panel width as a fraction of the window (default 0.30; "
                         "lower it if the camera view is cropped too tightly)")
    ap.add_argument("--check", action="store_true", help="test and exit")
    ap.add_argument("--probe", action="store_true",
                    help="report every window size involved in full screen, and exit")
    args = ap.parse_args()

    if args.probe:
        sys.exit(probe())
    if args.check:
        sys.exit(check(args))

    screen_size()                      # measure once, before any window exists
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
    n_frames, auto_at, settle_at = 0, -99, -99
    mirror = not args.no_mirror
    side = "right" if args.side == "auto" else args.side
    show_panel = True
    show_help = False
    closed_for = 0
    key_seen = False
    paused = False
    frozen = None
    t_prev, fps_s = time.time(), 0.0
    shots = 0

    cv2.waitKey(60)
    w0, h0 = window_size(WIN, False)
    print(f"\nRunning on {label}. Window {w0}x{h0}. Press q to quit, h for the keys.\n")

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
            n_frames += 1
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
                if args.side == "auto" and len(vis_r) >= 20 and n_frames - auto_at >= 15:
                    auto_at = n_frames
                    mr, ml = float(np.median(vis_r)), float(np.median(vis_l))
                    better = "right" if mr > ml else "left"
                    margin = abs(mr - ml)
                    if better != side and margin > 0.08:
                        side = better
                        # the angle series jumps when the leg changes; disarm so the
                        # jump is not counted as a repetition
                        armed, settle_at = False, n_frames
                ix = SIDES[side]
                angle = knee_angle(lm, ix)
                vis = side_visibility(lm, ix)
                draw_skeleton(frame, lm, dim=vis < 0.5)
                if vis >= 0.5:
                    highlight_knee(frame, lm, ix)
                if not paused:
                    hist.append(angle)
                    # Count only once the side has actually been decided. For the
                    # first ~20 frames the code is still watching the default leg,
                    # which may be the hidden one, and its noisy angle would
                    # otherwise register a repetition that never happened.
                    decided = args.side != "auto" or len(vis_r) >= 20
                    countable = decided and vis >= 0.5 and n_frames - settle_at >= 12
                    if countable and armed and angle > 75:
                        reps, armed = reps + 1, False
                    elif angle < 35:
                        armed = True
            elif not paused:
                hist.append(hist[-1] if hist else 0.0)

            fps_s = 0.9 * fps_s + 0.1 / max(1e-6, now - t_prev)
            t_prev = now

            canvas = compose(frame, (hist, angle, reps, vis, side, paused),
                             WIN, show_panel, args.panel, full)
            ch, cw = canvas.shape[:2]
            text(canvas, f"{fps_s:4.0f} fps", (14, ch - 16), 0.5, WHITE, 1)
            # with the panel hidden there is no visible way back, so say so
            if not show_panel:
                text(canvas, "p  panel     h  keys", (14, 30), 0.6, WHITE, 1)
            if show_help:
                canvas = draw_help(canvas)
            elif not key_seen and n_frames > 90:
                # nothing has been pressed yet; the commonest reason is that the
                # terminal still has focus and OpenCV never sees the keys
                text(canvas, "click this window first  |  h  keys  |  q  quit",
                     (14, 58), 0.6, WHITE, 1)

            cv2.imshow(WIN, canvas)
            # One poll per frame. waitKey drains the queued key events, so a single
            # call does not lose presses — and on macOS each call pumps the event
            # loop and costs well over the millisecond asked for, so calling it
            # several times per frame cost two thirds of the frame rate.
            k = cv2.waitKey(1) & 0xFF

            # the window's close button is a route out that does not need focus.
            # Require two consecutive bad readings so one odd value cannot end the demo.
            try:
                gone = cv2.getWindowProperty(WIN, cv2.WND_PROP_VISIBLE) < 1
            except Exception:
                gone = True
            closed_for = closed_for + 1 if gone else 0
            if closed_for >= 2:
                break

            if k != 255:
                key_seen = True
            if k in (ord("q"), ord("Q"), 27):
                break
            elif k == ord(" "):
                paused = not paused
            elif k == ord("f"):
                full = not full
                maximise(WIN, full)
                for _ in range(5):       # let the window manager finish resizing
                    cv2.waitKey(30)
                mw, mh = window_size(WIN, full)
                print(f"  {'big' if full else 'windowed'}: drawing at {mw}x{mh}")
            elif k == ord("s"):
                shots += 1
                name = f"live_shot_{shots:02d}.png"
                cv2.imwrite(name, canvas)
                print(f"  saved {name}")
            elif k == ord("r"):
                hist.clear(); reps, armed = 0, True; vis_r.clear(); vis_l.clear()
            elif k == ord("m"):
                mirror = not mirror
            elif k == ord("p"):
                show_panel = not show_panel
            elif k in (ord("h"), ord("?")):
                show_help = not show_help
            elif k == ord("l"):
                order = ["auto", "left", "right"]
                args.side = order[(order.index(args.side) + 1) % 3]
                if args.side != "auto":
                    side = args.side
                print(f"  side: {args.side}")

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n{reps} repetitions counted.")


def run(argv=None):
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C is a legitimate way out; do not dump a traceback mid-lecture
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        print("\nstopped")


if __name__ == "__main__":
    run()
