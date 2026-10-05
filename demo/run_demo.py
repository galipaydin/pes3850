#!/usr/bin/env python3
"""
PES 517 · Week 1 — build the opening demo from a video clip.

Produces the three files you show in class:
    <out>/demo_side_by_side.png   one frame, raw | skeleton
    <out>/demo_overlay.mp4        the clip with the skeleton drawn on
    <out>/demo_knee_angle.png     the knee-angle curve

Usage
    python3 run_demo.py clips/squat_frontal_raise.mp4
    python3 run_demo.py my_clip.mov --out out_mine --seconds 8 --side left
    python3 run_demo.py clips/*.mp4 --compare        # rank several clips

Install
    pip install mediapipe opencv-python matplotlib pandas

Uses MediaPipe Pose Landmarker through the **Tasks API**. The old `mp.solutions.pose`
interface was removed in MediaPipe 1.0 — if you find a tutorial using it, it is dead code.
"""
from __future__ import annotations
import argparse, sys, subprocess, shutil
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
             "pose_landmarker_{size}/float16/latest/pose_landmarker_{size}.task")

# MediaPipe gives 33 landmarks. These are the ones a sagittal squat needs.
SIDES = {"right": dict(hip=24, knee=26, ankle=28, heel=30, foot=32),
         "left":  dict(hip=23, knee=25, ankle=27, heel=29, foot=31)}

EDGES = [(11, 12), (11, 23), (12, 24), (23, 24),              # torso
         (11, 13), (13, 15), (12, 14), (14, 16),              # arms
         (23, 25), (25, 27), (27, 29), (29, 31), (27, 31),    # left leg + foot
         (24, 26), (26, 28), (28, 30), (30, 32), (28, 32)]    # right leg + foot

MAROON_BGR = (43, 28, 138)
TEAL_BGR   = (112, 100, 27)


def fetch_model(size: str = "full") -> Path:
    path = Path(f"pose_landmarker_{size}.task")
    if path.exists() and path.stat().st_size > 1_000_000:
        return path
    url = MODEL_URL.format(size=size)
    print(f"  downloading {path.name} ...", end=" ", flush=True)
    try:
        import urllib.request
        urllib.request.urlretrieve(url, path)
    except Exception as e:
        sys.exit(f"\n  could not download the model: {e}\n  URL: {url}")
    print(f"{path.stat().st_size/1e6:.1f} MB")
    return path


def prepare(src: Path, seconds: int, height: int, workdir: Path) -> Path:
    """Trim and downscale if needed. Stock footage is usually 4K and far too long."""
    cap = cv2.VideoCapture(str(src))
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n, fps = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), cap.get(cv2.CAP_PROP_FPS) or 30
    cap.release()
    dur = n / fps
    print(f"  source   : {w}x{h}, {dur:.1f}s, {fps:.0f} fps")
    if h <= height and dur <= seconds and src.suffix.lower() == ".mp4":
        return src
    if not shutil.which("ffmpeg"):
        print("  ! ffmpeg not found — using the clip as-is (this may be slow)")
        return src
    out = workdir / "clip_prepared.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src),
                    "-t", str(seconds), "-vf", f"scale=-2:{height}",
                    "-an", str(out)], check=True)
    cap = cv2.VideoCapture(str(out))
    print(f"  prepared : {int(cap.get(3))}x{int(cap.get(4))}, "
          f"{cap.get(7)/(cap.get(5) or 30):.1f}s  -> {out.name}")
    cap.release()
    return out


def crop_box(src: Path, model: Path, pad: float = 0.12):
    """Bounding box of the athlete across the whole clip, padded. Returns (x,y,w,h) or None.
    The person is often small in a wide frame; cropping makes the slide readable from the back."""
    options = vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(model)),
        running_mode=vision.RunningMode.VIDEO, num_poses=1)
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    step = max(1, n // 40)
    xs, ys = [], []
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if i % step == 0:
                img = mp.Image(image_format=mp.ImageFormat.SRGB,
                               data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                res = landmarker.detect_for_video(img, int(i / fps * 1000))
                if res.pose_landmarks:
                    for lm in res.pose_landmarks[0]:
                        if lm.visibility > 0.5:
                            xs.append(lm.x); ys.append(lm.y)
            i += 1
    cap.release()
    if not xs:
        return None
    x0, x1 = max(0.0, min(xs) - pad), min(1.0, max(xs) + pad)
    y0, y1 = max(0.0, min(ys) - pad), min(1.0, max(ys) + pad)
    x, y = int(x0 * W), int(y0 * H)
    w, h = int((x1 - x0) * W), int((y1 - y0) * H)
    w -= w % 2; h -= h % 2                      # H.264 needs even dimensions
    if w < 80 or h < 80 or (w * h) > 0.92 * W * H:
        return None                              # nothing worth cropping
    print(f"  crop     : {w}x{h} from {W}x{H}  ({100*w*h/(W*H):.0f}% of the frame)")
    return x, y, w, h


def apply_crop(src: Path, box, out: Path) -> Path:
    x, y, w, h = box
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src),
                    "-vf", f"crop={w}:{h}:{x}:{y}", "-an", str(out)], check=True)
    return out


def draw(img, lms):
    h, w = img.shape[:2]
    pt = lambda i: (int(lms[i].x * w), int(lms[i].y * h))
    for a, b in EDGES:
        cv2.line(img, pt(a), pt(b), (255, 255, 255), 5, cv2.LINE_AA)
        cv2.line(img, pt(a), pt(b), TEAL_BGR, 3, cv2.LINE_AA)
    for i in range(11, 33):
        cv2.circle(img, pt(i), 6, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(img, pt(i), 4, MAROON_BGR, -1, cv2.LINE_AA)
    return img


def pick_side(src: Path, model: Path, sample: int = 40) -> str:
    """Whichever side faces the camera tracks far better. Sample a few frames and choose."""
    options = vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(model)),
        running_mode=vision.RunningMode.VIDEO, num_poses=1)
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or sample
    step = max(1, n // sample)
    score = {"right": [], "left": []}
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if i % step == 0:
                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                                  data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                res = landmarker.detect_for_video(mp_img, int(i / fps * 1000))
                if res.pose_landmarks:
                    lms = res.pose_landmarks[0]
                    for name, ix in SIDES.items():
                        score[name].append(min(lms[ix["hip"]].visibility,
                                               lms[ix["knee"]].visibility,
                                               lms[ix["ankle"]].visibility,
                                               lms[ix["foot"]].visibility))
            i += 1
    cap.release()
    med = {k: (float(np.median(v)) if v else 0.0) for k, v in score.items()}
    best = max(med, key=med.get)
    print(f"  side     : {best}  (visibility right {med['right']:.2f} · left {med['left']:.2f})")
    return best


def track(src: Path, model: Path, side: str, out_dir: Path, stem: str,
          write_video: bool = True):
    idx_ = SIDES[side]
    options = vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(model)),
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = (cv2.VideoWriter(str(out_dir / f"{stem}_overlay.mp4"),
                              cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
              if write_video else None)

    rows, still = [], None
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                              data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            res = landmarker.detect_for_video(mp_img, int(i / fps * 1000))
            drawn = frame
            if res.pose_landmarks:
                lms = res.pose_landmarks[0]
                drawn = draw(frame.copy(), lms)
                g = lambda k: lms[idx_[k]]
                rows.append(dict(
                    t=i / fps,
                    hip_x=g("hip").x,     hip_y=g("hip").y,
                    knee_x=g("knee").x,   knee_y=g("knee").y,
                    ankle_x=g("ankle").x, ankle_y=g("ankle").y,
                    vis=min(g("hip").visibility, g("knee").visibility,
                            g("ankle").visibility),
                    foot_vis=g("foot").visibility))
                if still is None and i > fps:
                    still = (frame.copy(), drawn.copy())
            if writer:
                writer.write(drawn)
            i += 1
    cap.release()
    if writer:
        writer.release()
    return pd.DataFrame(rows), still, i, fps


def knee_flexion(df: pd.DataFrame) -> pd.Series:
    """Angle at the knee between thigh and shank. 0 degrees is a straight leg."""
    thigh = np.c_[df.hip_x - df.knee_x, df.hip_y - df.knee_y]
    shank = np.c_[df.ankle_x - df.knee_x, df.ankle_y - df.knee_y]
    cos = (thigh * shank).sum(1) / (np.linalg.norm(thigh, axis=1)
                                    * np.linalg.norm(shank, axis=1))
    return pd.Series(180 - np.degrees(np.arccos(np.clip(cos, -1, 1))), index=df.index)


def count_reps(sm: np.ndarray, floor: float) -> int:
    peaks, armed = 0, True
    for i in range(1, len(sm) - 1):
        if armed and sm[i] > floor and sm[i] >= sm[i - 1] and sm[i] > sm[i + 1]:
            peaks, armed = peaks + 1, False
        elif sm[i] < floor * 0.6:
            armed = True
    return peaks


def report(df, frames, fps, label=""):
    found = len(df) / max(frames, 1)
    sm = df["smooth"].values
    rom = df.smooth.max() - df.smooth.min()
    reps = count_reps(sm, df.smooth.min() + 0.55 * rom)
    return dict(clip=label, frames=frames, found=found,
                peak=df.smooth.max(), rom=rom, reps=reps,
                vis=df.vis.median(), foot_vis=df.foot_vis.median())


def make_figures(df, still, out_dir: Path, stem: str):
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(df.t, df.smooth, color="#8A1C2B", lw=2.4)
    ax.fill_between(df.t, df.smooth.min(), df.smooth, color="#8A1C2B", alpha=.08)
    ax.set_xlabel("Time (seconds)", fontsize=12)
    ax.set_ylabel("Knee flexion (degrees)", fontsize=12)
    ax.set_title("Knee angle, measured from an ordinary video", fontsize=14, pad=12)
    ax.grid(alpha=.3)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_dir / f"{stem}_knee_angle.png", dpi=160)
    plt.close(fig)

    if still is not None:
        raw, ovl = still
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        ax[0].imshow(cv2.cvtColor(raw, cv2.COLOR_BGR2RGB))
        ax[0].set_title("What the camera recorded", fontsize=13)
        ax[1].imshow(cv2.cvtColor(ovl, cv2.COLOR_BGR2RGB))
        ax[1].set_title("What the computer found", fontsize=13)
        for a in ax:
            a.axis("off")
        fig.tight_layout()
        fig.savefig(out_dir / f"{stem}_side_by_side.png", dpi=160)
        plt.close(fig)


def preflight(size: str) -> None:
    """MediaPipe 1.0.x aborts the whole process on some macOS arm64 builds (a Metal
    service error inside the graph). An abort cannot be caught, so probe it in a
    subprocess and give a useful message instead of a stack trace."""
    model = fetch_model(size)
    probe = (
        "import mediapipe as mp, numpy as np\n"
        "from mediapipe.tasks import python as P\n"
        "from mediapipe.tasks.python import vision as V\n"
        f"o=V.PoseLandmarkerOptions(base_options=P.BaseOptions(model_asset_path='{model}'),"
        "running_mode=V.RunningMode.VIDEO,num_poses=1)\n"
        "with V.PoseLandmarker.create_from_options(o) as l:\n"
        "    l.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,"
        "data=np.zeros((64,64,3),np.uint8)),0)\n")
    r = subprocess.run([sys.executable, "-c", probe],
                       capture_output=True, text=True)
    if r.returncode == 0:
        return
    if "DrishtiMetalHelper" in r.stderr or "Service is unavailable" in r.stderr:
        sys.exit(
            f"\nMediaPipe {mp.__version__} cannot start on this machine.\n"
            "  This is a known fault in the 1.0.x macOS (Apple silicon) build: the task graph\n"
            "  tries to reach a Metal service that is not there, and aborts the process.\n\n"
            "  Fix:   pip install 'mediapipe==0.10.18'\n"
            "         That release has the same Tasks API this script uses and works on macOS.\n\n"
            "  Or run the notebook in Google Colab instead, which is Linux and unaffected.")
    sys.exit(f"\nMediaPipe could not start:\n{r.stderr[-800:]}")


def to_h264(path: Path) -> Path:
    """OpenCV writes mpeg4, which some players and every browser refuse. Re-encode."""
    if not shutil.which("ffmpeg"):
        print("  ! ffmpeg not found — demo_overlay.mp4 is mpeg4 and may not play everywhere")
        return path
    out = path.with_name(path.stem + "_web.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(path),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    str(out)], check=True)
    path.unlink(missing_ok=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clips", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=Path("out"))
    ap.add_argument("--seconds", type=int, default=12)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--side", choices=["right", "left", "auto"], default="auto",
                    help="which leg to measure; auto picks whichever faces the camera")
    ap.add_argument("--model", choices=["lite", "full", "heavy"], default="full")
    ap.add_argument("--crop", action="store_true",
                    help="auto-crop to the athlete so the slide reads from the back row")
    ap.add_argument("--compare", action="store_true",
                    help="rank several clips; writes figures only for the best")
    args = ap.parse_args()

    print(f"mediapipe {mp.__version__} · opencv {cv2.__version__}")
    preflight(args.model)
    if hasattr(mp, "solutions"):
        print("  note: this build still carries the legacy mp.solutions API; "
              "this script does not use it")
    model = fetch_model(args.model)
    args.out.mkdir(parents=True, exist_ok=True)

    results = []
    for clip in args.clips:
        if not clip.exists():
            print(f"\n{clip}: NOT FOUND"); continue
        print(f"\n{clip.name}")
        prepared = prepare(clip, args.seconds, args.height, args.out)
        if args.crop and shutil.which("ffmpeg"):
            box = crop_box(prepared, model)
            if box:
                prepared = apply_crop(prepared, box, args.out / "clip_cropped.mp4")
        side = pick_side(prepared, model) if args.side == "auto" else args.side
        df, still, frames, fps = track(prepared, model, side, args.out, clip.stem,
                                       write_video=not args.compare)
        if df.empty:
            print("  no landmarks found at all — see FILMING.md"); continue
        df["knee_flex_deg"] = knee_flexion(df)
        df["smooth"] = df.knee_flex_deg.rolling(5, center=True, min_periods=1).mean()
        r = report(df, frames, fps, clip.name)
        r["side"] = side
        results.append((r, df, still))
        print(f"  landmarks: {r['found']:.0%} of frames · median confidence {r['vis']:.2f} "
              f"(foot {r['foot_vis']:.2f})")
        print(f"  knee     : peak {r['peak']:.0f}° · range {r['rom']:.0f}° · {r['reps']} reps detected")
        if r["found"] < 0.7:
            print("  ! patchy detection — whole body in frame? busy background?")
        if r["vis"] < 0.5:
            print("  ! low confidence — the model is guessing these landmarks")

    for tmp in ("clip_prepared.mp4", "clip_cropped.mp4"):
        (args.out / tmp).unlink(missing_ok=True)

    if not results:
        sys.exit("\nNothing to report.")

    if args.compare:
        print("\n" + "=" * 78)
        print("RANKED  (detection rate x confidence x whether the feet are visible)")
        print("=" * 78)
        tbl = pd.DataFrame([r for r, _, _ in results])
        tbl["score"] = tbl["found"] * tbl["vis"] * tbl["foot_vis"]
        tbl = tbl.sort_values("score", ascending=False)
        print(tbl[["clip", "side", "found", "vis", "foot_vis", "peak", "rom", "reps", "score"]]
              .to_string(index=False,
                         formatters={"found": "{:.0%}".format, "vis": "{:.2f}".format,
                                     "foot_vis": "{:.2f}".format, "peak": "{:.0f}°".format,
                                     "rom": "{:.0f}°".format, "score": "{:.3f}".format}))
        best = tbl.iloc[0]["clip"]
        print(f"\nBest tracked: {best}")
        print("\nThe score measures how well the model TRACKS, not how good a teaching clip it is.")
        print("Also weigh: is the movement one everybody recognises, are there two or three clean")
        print("repetitions, and is the person large enough in the frame to read from the back row.")
        print("\nRe-run without --compare on your chosen clip to write the output files.")
    else:
        r, df, still = results[0]
        stem = args.clips[0].stem
        make_figures(df, still, args.out, stem)
        overlay = args.out / f"{stem}_overlay.mp4"
        if overlay.exists():
            to_h264(overlay)
        print(f"\nWrote to {args.out}/")
        for f in [f"{stem}_side_by_side.png", f"{stem}_overlay_web.mp4",
                  f"{stem}_knee_angle.png"]:
            p = args.out / f
            if p.exists():
                print(f"  {f}  ({p.stat().st_size/1e3:.0f} KB)")
        print(f"\nSide measured: {r['side']} leg · {r['reps']} repetitions · "
              f"peak {r['peak']:.0f}° · range {r['rom']:.0f}°")
        print("\nShow them in this order: the still, then the video (twice), then the curve.")
        print("Put them on the machine you will teach from, and play the video once in the room.")


if __name__ == "__main__":
    main()
