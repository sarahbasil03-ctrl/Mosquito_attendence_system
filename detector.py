"""
detector.py — Mosquito Detection & Tracking Engine
====================================================
Approach: MOG2 background subtraction + strict centroid tracking.
Key noise-rejection layers:
  1. Long warm-up (builds stable BG model before any tracking)
  2. Gaussian blur + hard threshold to kill pixel noise
  3. MIN_HIT_COUNT — blob must persist across many frames
  4. MIN_TRACK_DURATION — track must last several seconds
  5. MAX_ACTIVE_TRACKS — hard cap on simultaneous tracks
  6. Aspect-ratio filter — rejects long thin blobs (not mosquito-shaped)
"""

import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment
from collections import OrderedDict


# ══════════════════════════════════════════════════════════════════
#  PARAMETERS  (auto-tuned in analyze_video based on video FPS)
# ══════════════════════════════════════════════════════════════════
MIN_AREA          = 40      # px² after resize-to-640 — raise to cut noise
MAX_AREA          = 1200    # px² — lower to cut large blobs
MAX_DIST          = 50      # px match radius
MAX_DISAPPEARED   = 8       # frames before closing track
SKIP_FRAMES       = 2       # process every Nth frame
MIN_HIT_COUNT     = 15      # frames blob must be seen (primary noise filter)
MIN_TRACK_SECS    = 0.5     # seconds a track must last to be counted
BLUR_KERNEL       = 7       # Gaussian pre-blur (odd number)
VAR_THRESHOLD     = 120     # MOG2 strictness (higher = fewer detections)
BG_HISTORY        = 600     # MOG2 background frames
WARMUP_RATIO      = 0.12    # fraction of video used for warm-up (no tracking)
MAX_ACTIVE_TRACKS = 30      # hard cap on simultaneous live tracks
MAX_BLOBS_PER_FRAME = 15    # ignore frames with too many blobs (noise burst)
MAX_ASPECT_RATIO  = 4.0     # blob width/height must be < this (mosquito-shaped)
# ══════════════════════════════════════════════════════════════════


class CentroidTracker:
    def __init__(self):
        self.next_id     = 1
        self.objects     = OrderedDict()   # id → centroid
        self.disappeared = OrderedDict()   # id → miss count
        self.entry_frame = {}
        self.exit_frame  = {}
        self.hit_count   = {}
        self.last_frame  = {}              # last frame this track was active

    def register(self, centroid, frame_no):
        oid = self.next_id
        self.objects[oid]     = centroid
        self.disappeared[oid] = 0
        self.entry_frame[oid] = frame_no
        self.hit_count[oid]   = 1
        self.last_frame[oid]  = frame_no
        self.next_id         += 1

    def deregister(self, oid, frame_no):
        self.exit_frame[oid]  = frame_no
        del self.objects[oid]
        del self.disappeared[oid]

    def update(self, centroids, frame_no):
        # ── Increment disappear counters if no detections ─────────
        if len(centroids) == 0:
            for oid in list(self.disappeared):
                self.disappeared[oid] += 1
                if self.disappeared[oid] > MAX_DISAPPEARED:
                    self.deregister(oid, frame_no)
            return

        # ── First frame — register (up to cap) ───────────────────
        if len(self.objects) == 0:
            for c in centroids[:MAX_ACTIVE_TRACKS]:
                self.register(c, frame_no)
            return

        # ── Hungarian matching ────────────────────────────────────
        obj_ids   = list(self.objects.keys())
        obj_cents = np.array(list(self.objects.values()), dtype=float)
        new_cents = np.array(centroids, dtype=float)
        D         = np.linalg.norm(
            obj_cents[:, None] - new_cents[None, :], axis=2
        )
        row_ind, col_ind = linear_sum_assignment(D)

        used_rows, used_cols = set(), set()
        for r, c in zip(row_ind, col_ind):
            if D[r, c] > MAX_DIST:
                continue
            oid = obj_ids[r]
            self.objects[oid]     = centroids[c]
            self.disappeared[oid] = 0
            self.hit_count[oid]   = self.hit_count.get(oid, 0) + 1
            self.last_frame[oid]  = frame_no
            used_rows.add(r)
            used_cols.add(c)

        for r, oid in enumerate(obj_ids):
            if r not in used_rows:
                self.disappeared[oid] += 1
                if self.disappeared[oid] > MAX_DISAPPEARED:
                    self.deregister(oid, frame_no)

        # Register new centroids only if under cap
        if len(self.objects) < MAX_ACTIVE_TRACKS:
            for c in range(len(centroids)):
                if c not in used_cols:
                    self.register(centroids[c], frame_no)
                    if len(self.objects) >= MAX_ACTIVE_TRACKS:
                        break


def _get_centroids(frame, bg_sub):
    """
    Extract valid mosquito-blob centroids from a single frame.
    Returns list of (cx, cy) tuples.
    """
    gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (BLUR_KERNEL, BLUR_KERNEL), 0)
    fg      = bg_sub.apply(blurred)

    # Hard binary threshold — only very confident foreground
    _, thresh = cv2.threshold(fg, 240, 255, cv2.THRESH_BINARY)

    # Three-pass morphological cleanup
    k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN,  k3, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, k3, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN,  k5, iterations=1)

    num_labels, _, stats, centroids_all = cv2.connectedComponentsWithStats(
        thresh, connectivity=8
    )

    valid = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if not (MIN_AREA <= area <= MAX_AREA):
            continue
        # Aspect ratio filter — real mosquitoes are roughly circular/oval
        bw = stats[i, cv2.CC_STAT_WIDTH]
        bh = stats[i, cv2.CC_STAT_HEIGHT]
        if bh > 0 and bw / bh > MAX_ASPECT_RATIO:
            continue
        if bw > 0 and bh / bw > MAX_ASPECT_RATIO:
            continue
        valid.append((int(centroids_all[i][0]), int(centroids_all[i][1])))

    return valid


def _fmt(frame_no, fps):
    s = int(frame_no / max(fps, 1))
    return f"{s // 60:02d}:{s % 60:02d}"


def analyze_video(video_path: str) -> dict:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps          = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    vid_w        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_h        = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    filename     = video_path.replace("\\", "/").split("/")[-1]

    # Scale MIN_HIT_COUNT to video FPS so it always means ~0.5 seconds
    # e.g. 30fps → need 15 hits across skipped frames = ~1 second visible
    effective_hit_count = max(
        MIN_HIT_COUNT,
        int((fps / SKIP_FRAMES) * MIN_TRACK_SECS)
    )

    bg_sub = cv2.createBackgroundSubtractorMOG2(
        history=BG_HISTORY,
        varThreshold=VAR_THRESHOLD,
        detectShadows=False
    )
    tracker  = CentroidTracker()
    frame_no = 0

    # ── Warm-up phase: no tracking, just feed frames to BG model ──
    warmup_count = max(60, int(total_frames * WARMUP_RATIO))
    warmup_count = min(warmup_count, 200)  # cap at 200 frames

    for _ in range(warmup_count):
        ret, frame = cap.read()
        if not ret:
            break
        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (BLUR_KERNEL, BLUR_KERNEL), 0)
        bg_sub.apply(blurred)   # learning=−1 uses default learning rate
        frame_no += 1

    # ── Tracking phase ────────────────────────────────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_no % SKIP_FRAMES == 0:
            h, w = frame.shape[:2]
            scale = min(1.0, 640 / max(h, w, 1))
            if scale < 1.0:
                frame = cv2.resize(
                    frame, (int(w * scale), int(h * scale)),
                    interpolation=cv2.INTER_AREA
                )

            blobs = _get_centroids(frame, bg_sub)

            # Reject noisy frames — if too many blobs, skip this frame
            if len(blobs) <= MAX_BLOBS_PER_FRAME:
                tracker.update(blobs, frame_no)
            else:
                # Still age existing tracks so they don't become immortal
                for oid in list(tracker.disappeared):
                    tracker.disappeared[oid] += 1
                    if tracker.disappeared[oid] > MAX_DISAPPEARED:
                        tracker.deregister(oid, frame_no)

        frame_no += 1

    cap.release()

    # ── Confirm tracks by hit count AND minimum duration ─────────
    confirmed = set()
    for oid, hits in tracker.hit_count.items():
        if hits < effective_hit_count:
            continue
        # Track must span at least MIN_TRACK_SECS in real time
        entry_f = tracker.entry_frame.get(oid, 0)
        last_f  = tracker.last_frame.get(oid, entry_f)
        span_sec = (last_f - entry_f) / fps
        if span_sec >= MIN_TRACK_SECS:
            confirmed.add(oid)

    still_active = {oid for oid in tracker.objects if oid in confirmed}

    # ── Build attendance records ──────────────────────────────────
    records = []
    for oid in sorted(confirmed):
        is_present = oid in still_active
        records.append({
            "id":      f"Mosquito #{oid:02d}",
            "entry":   _fmt(tracker.entry_frame.get(oid, 0), fps),
            "exit":    _fmt(tracker.exit_frame[oid], fps)
                       if oid in tracker.exit_frame else "—",
            "present": is_present,
            "pct":     100 if is_present else 0
        })

    total_entered = len(records)
    absent_count  = sum(1 for r in records if not r["present"])
    present_count = total_entered - absent_count

    return {
        "filename":      filename,
        "duration":      _fmt(total_frames, fps),
        "fps":           round(fps, 2),
        "total_frames":  total_frames,
        "totalDetected": total_entered,
        "totalEntered":  total_entered,
        "totalLeft":     absent_count,
        "presentCount":  present_count,
        "absentCount":   absent_count,
        "records":       records
    }
