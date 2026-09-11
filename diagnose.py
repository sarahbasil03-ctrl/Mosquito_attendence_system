"""
diagnose.py — Run this to calibrate the detector for your specific video.
Usage: python diagnose.py "path\\to\\your\\video.mp4"
"""
import cv2
import numpy as np
import sys
import os

if len(sys.argv) < 2:
    print("Usage: python diagnose.py \"path\\to\\video.mp4\"")
    sys.exit(1)

video_path = sys.argv[1]
if not os.path.exists(video_path):
    print(f"File not found: {video_path}")
    sys.exit(1)

cap = cv2.VideoCapture(video_path)
fps          = cap.get(cv2.CAP_PROP_FPS) or 25.0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
duration     = total_frames / fps

print(f"\n{'='*55}")
print(f"  VIDEO INFO")
print(f"{'='*55}")
print(f"  File         : {os.path.basename(video_path)}")
print(f"  Resolution   : {w} x {h}")
print(f"  FPS          : {fps}")
print(f"  Total frames : {total_frames}")
print(f"  Duration     : {duration:.1f}s ({duration/60:.1f} min)")

# ── Sample frames and count blobs at various thresholds ──────────
bg_sub = cv2.createBackgroundSubtractorMOG2(
    history=500, varThreshold=80, detectShadows=False
)

# Warm up
warmup = min(80, total_frames // 4)
for _ in range(warmup):
    ret, frame = cap.read()
    if not ret: break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bg_sub.apply(cv2.GaussianBlur(gray, (5,5), 0))

print(f"\n{'='*55}")
print(f"  BLOB SIZE DISTRIBUTION (sample from 20 frames)")
print(f"  (tells us what area range real mosquitoes are)")
print(f"{'='*55}")

area_samples = []
frame_count = 0
sample_interval = max(1, (total_frames - warmup) // 20)

while frame_count < 20:
    ret, frame = cap.read()
    if not ret: break

    scale = min(1.0, 640 / max(h, w, 1))
    if scale < 1.0:
        frame = cv2.resize(frame, (int(w*scale), int(h*scale)))

    gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    fg      = bg_sub.apply(blurred)
    _, thresh = cv2.threshold(fg, 240, 255, cv2.THRESH_BINARY)
    kernel  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    thresh  = cv2.morphologyEx(thresh, cv2.MORPH_OPEN,  kernel, iterations=2)
    thresh  = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(thresh, connectivity=8)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if 10 <= area <= 5000:
            area_samples.append(area)

    # Skip ahead
    for _ in range(sample_interval - 1):
        cap.read()

    frame_count += 1

cap.release()

if area_samples:
    area_samples.sort()
    total_blobs = len(area_samples)
    print(f"  Total blobs found  : {total_blobs}")
    print(f"  Min blob area      : {min(area_samples)} px²")
    print(f"  Max blob area      : {max(area_samples)} px²")
    print(f"  Median blob area   : {area_samples[len(area_samples)//2]} px²")
    print(f"  Mean blob area     : {int(np.mean(area_samples))} px²")
    print()

    # Distribution
    ranges = [(10,50),(50,100),(100,200),(200,500),(500,1000),(1000,2000),(2000,5000)]
    print(f"  Area range (px²)  | Count | % of total")
    print(f"  {'─'*45}")
    for lo, hi in ranges:
        cnt = sum(1 for a in area_samples if lo <= a < hi)
        bar = '█' * min(30, int(cnt / max(total_blobs,1) * 60))
        print(f"  {lo:5d} – {hi:5d}     | {cnt:5d} | {bar}")

    print(f"\n{'='*55}")
    print(f"  RECOMMENDED detector.py SETTINGS")
    print(f"{'='*55}")

    # Suggest MIN_AREA = 40th percentile, MAX_AREA = 95th percentile
    p40 = area_samples[int(len(area_samples)*0.40)]
    p95 = area_samples[int(len(area_samples)*0.95)]
    # Cap suggestions to sane ranges
    suggested_min = max(30, min(int(p40), 200))
    suggested_max = max(suggested_min+100, min(int(p95), 3000))

    print(f"  MIN_AREA      = {suggested_min}")
    print(f"  MAX_AREA      = {suggested_max}")
    print(f"  VAR_THRESHOLD = 80  (keep as-is)")
    print(f"  MIN_HIT_COUNT = 8   (keep as-is)")
    print()
    print(f"  Edit these values in detector.py and re-upload.")
else:
    print("  No blobs detected after warmup — video may already be clean")
    print("  or background subtraction needs lower varThreshold.")

print(f"{'='*55}\n")
