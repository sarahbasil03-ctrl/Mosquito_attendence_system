"""
app.py — Mosquito Attendance System — Flask Backend
=====================================================
Endpoints
──────────
GET  /              → serves index.html
GET  /health        → {"status": "ok"}
POST /analyze       → upload video, run detector, return JSON results
POST /analyze/demo  → returns realistic demo data (no video needed)

Run:
    python app.py
Then open:  http://localhost:5000
"""

import os
import uuid
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from detector import analyze_video

# ── App setup ─────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR  = os.path.join(BASE_DIR, "uploads")
STATIC_DIR  = BASE_DIR                        # index.html lives here
ALLOWED_EXT = {".mp4", ".mov", ".avi", ".webm", ".mkv"}
MAX_MB      = 500                             # max upload size in MB

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = MAX_MB * 1024 * 1024
CORS(app)   # allow frontend (file://) to call the API


# ── Serve frontend ────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


# ── Health check ─────────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok", "message": "Mosquito Attendance API is running"})


# ── Main analysis endpoint ────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files["video"]
    if video_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    ext = os.path.splitext(video_file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        return jsonify({"error": f"Unsupported format: {ext}. Use MP4, MOV, AVI, WEBM or MKV"}), 400

    # Save to uploads/ with a unique name to avoid conflicts
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path   = os.path.join(UPLOAD_DIR, unique_name)
    video_file.save(save_path)

    try:
        result = analyze_video(save_path)
        # Put original filename back
        result["filename"] = video_file.filename
        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up the temp file
        if os.path.exists(save_path):
            os.remove(save_path)


# ── Demo endpoint (no video required) ────────────────────────────
@app.route("/analyze/demo", methods=["POST"])
def analyze_demo():
    """Returns realistic hardcoded demo data for testing the UI."""
    import random, math
    random.seed(42)
    total   = 37
    absent  = 8
    present = total - absent
    records = []
    duration = 90  # seconds

    def fmt(sec):
        return f"{sec//60:02d}:{sec%60:02d}"

    entry_times = sorted(random.sample(range(0, int(duration * 0.6)), total))
    absent_ids  = set(random.sample(range(total), absent))

    for i, entry_sec in enumerate(entry_times):
        is_absent = i in absent_ids
        exit_sec  = None
        if is_absent:
            exit_sec = entry_sec + random.randint(5, duration - entry_sec - 2)

        records.append({
            "id":      f"Mosquito #{i+1:02d}",
            "entry":   fmt(entry_sec),
            "exit":    fmt(exit_sec) if exit_sec else "—",
            "present": not is_absent,
            "pct":     0 if is_absent else 100
        })

    return jsonify({
        "filename":      "demo_video.mp4",
        "duration":      fmt(duration),
        "fps":           30.0,
        "total_frames":  duration * 30,
        "totalDetected": total,
        "totalEntered":  total,
        "totalLeft":     absent,
        "presentCount":  present,
        "absentCount":   absent,
        "records":       records
    })


# ── Error handlers ────────────────────────────────────────────────
@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": f"File too large. Max size is {MAX_MB} MB"}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


# ── Run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  🦟  MOSQUITO ATTENDANCE SYSTEM — BACKEND")
    print("="*55)
    print(f"  Server  : http://localhost:5000")
    print(f"  API     : http://localhost:5000/analyze")
    print(f"  Health  : http://localhost:5000/health")
    print(f"  Uploads : {UPLOAD_DIR}")
    print("="*55 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
