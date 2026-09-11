# 🦟 Mosquito Attendance System

An AI-powered computer vision system that detects and tracks mosquitoes in uploaded videos and automatically generates a real-time attendance report.

Built as a college project demonstrating the use of background subtraction, centroid tracking, and a full-stack web dashboard.

---

## 🖥️ Screenshots

### Page 1 — Video Upload
![Upload Page](images/Screenshot%20(7).png)

---

### AI Scanning Overlay
![AI Scanning](images/Screenshot%20(8).png)

---

### Page 2 — Attendance Dashboard
![Attendance Dashboard](images/Screenshot%20(6).png)

---

## 📸 Features

- 🎥 **Video Upload** — drag & drop or browse (MP4, MOV, AVI, WEBM, MKV)
- 🔍 **AI Detection** — OpenCV MOG2 background subtraction isolates moving mosquito blobs
- 📍 **Centroid Tracking** — Hungarian algorithm assigns persistent IDs to each mosquito
- 📊 **Attendance Dashboard** — Present / Absent / Total / Attendance % stats
- 🗂️ **Attendance Table** — searchable, sortable, with entry/exit timestamps per mosquito
- 🔵 **Circular Progress Indicator** — visual attendance percentage
- 🎨 **Fun Mode Toggle** — mosquito animations, floating particles, funny subtitle (on/off via one config variable)
- 🌑 **Dark Futuristic UI** — neon glowing cards, glassmorphism, animated scan overlay
- 🔌 **Demo Fallback** — if backend is offline, realistic demo data is used automatically

---

## 🗂️ Project Structure

```
mosquito/
├── app.py              # Flask backend — REST API server
├── detector.py         # OpenCV detection + centroid tracking engine
├── index.html          # Full frontend — served by Flask
├── diagnose.py         # Calibration tool for tuning detection parameters
├── run.bat             # One-click launcher (Windows)
├── requirements.txt    # Python dependencies
├── .gitignore          # Excludes uploads/, __pycache__, etc.
├── images/             # Screenshots for README
└── uploads/            # Temporary video storage (auto-cleaned, git-ignored)
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask, Flask-CORS |
| Detection | OpenCV (MOG2 background subtraction) |
| Tracking | Centroid tracker + SciPy Hungarian algorithm |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Charts | Pure CSS circular progress + canvas particles |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/sarahbasil03-ctrl/Mosquito_attendence_system.git
cd Mosquito_attendence_system

# 2. Install dependencies
pip install flask flask-cors opencv-python numpy scipy

# 3. Start the server
python app.py
```

### Open the website

```
http://localhost:5000
```

Or on Windows, just double-click **`run.bat`**.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serves the frontend |
| GET | `/health` | Backend health check |
| POST | `/analyze` | Upload video → returns attendance JSON |
| POST | `/analyze/demo` | Returns demo attendance data (no video needed) |

### Sample `/analyze` Response

```json
{
  "filename": "mosquito_video.mp4",
  "duration": "01:30",
  "fps": 30.0,
  "totalEntered": 12,
  "totalLeft": 4,
  "presentCount": 8,
  "absentCount": 4,
  "records": [
    { "id": "Mosquito #01", "entry": "00:04", "exit": "—",     "present": true,  "pct": 100 },
    { "id": "Mosquito #02", "entry": "00:08", "exit": "00:31", "present": false, "pct": 0   }
  ]
}
```

---

## 🧠 How Detection Works

```
Video Frame
    ↓
Grayscale + Gaussian Blur        ← removes pixel noise
    ↓
MOG2 Background Subtraction      ← isolates moving foreground
    ↓
Binary Threshold + Morphology    ← cleans up blobs
    ↓
Connected Components             ← labels individual blobs
    ↓
Size + Aspect Ratio Filter       ← keeps mosquito-sized blobs only
    ↓
Centroid Tracker (Hungarian)     ← assigns persistent IDs
    ↓
Attendance Records               ← entry time, exit time, status
```

---

## 🎨 Fun Mode

All decorative elements (mosquito animations, floating particles, funny subtitle) are controlled by a single variable in `index.html`:

```js
const ENABLE_FUN_MODE = true;   // set to false for clean professional UI
```

- `true` → mosquito emojis 🦟, animated particles, floating decorations
- `false` → clean dark futuristic UI, no animations, plain icons

---

## 🔧 Calibration

If mosquito counts are inaccurate for your specific video, run the diagnostic tool:

```bash
python diagnose.py "path/to/your/video.mp4"
```

It analyzes blob sizes in your video and recommends the best `MIN_AREA` and `MAX_AREA` values for `detector.py`.

---

## 📋 Attendance Logic

| Condition | Status |
|---|---|
| Mosquito entered and still inside at end of video | ✅ PRESENT |
| Mosquito entered but exited before video ends | ❌ ABSENT |

```
Attendance % = (Present / Total Entered) × 100
```

---

## 📦 Requirements

```
flask>=3.0.0
flask-cors>=4.0.0
opencv-python>=4.8.0
numpy>=1.24.0
scipy>=1.11.0
```

---

## 👩‍💻 Author

**Niya Elsa Shiby**
GitHub: [@sarahbasil03-ctrl](https://github.com/sarahbasil03-ctrl)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
