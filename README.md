
# Mosquito_attendence_system
AI-powered mosquito attendance system using Python, Flask, and OpenCV. Detects and tracks mosquitoes in video using background subtraction + centroid tracking. Features a dark futuristic web dashboard with real-time attendance reports, search/sort table, and Fun Mode toggle.
<img width="1280" height="640" alt="git (1)" src="https://github.com/user-attachments/assets/8920b256-2ba8-4988-b824-5351134eb4bd" />

# Mosquito Attendance System 🦟🎯

## Basic Details

### Team Name: [TRAAASH]

### Team Members
- Team Lead: [SARAH BASIL] - [COLLEGE OF ENGINEERING CHENGANUUR]
- Member 2: THEERTHA S B] - [COLLEGE OF ENGINEERING CHENGANUUR]

## Project Description

Mosquito Attendance System is a fun computer-vision-based project that treats mosquitoes like students taking attendance. 🦟

The system processes mosquito videos, detects and tracks mosquito movement, and determines whether each mosquito is **Present or Absent** based on its movement in the monitored area.

## The Problem (that doesn't exist)

Who is attending class and who has flown away? 👀

Normally, nobody keeps attendance for mosquitoes.

But mosquitoes enter, move around, disappear, and come back without informing anyone.

Manual mosquito monitoring is also slow and difficult.

So we decided to solve the most important problem nobody asked us to solve:

**"How do we take attendance of mosquitoes?"** 🦟

## The Solution (that nobody asked for)

We built a computer-vision-based **Mosquito Attendance System**.

The user uploads a video and the system analyzes the video to detect mosquito-like objects, track their movement and generate attendance results.

### Basic Flow

**Video → Detection → Tracking → Entry/Exit Analysis → Attendance → Dashboard**

Because even mosquitoes deserve attendance. 😌🦟

---

# Technical Details

## Technologies/Components Used

### For Software:

- **Languages:** Python, HTML, CSS, JavaScript
- **Backend:** Flask
- **Computer Vision:** OpenCV
- **Numerical Processing:** NumPy
- **Frontend:** HTML, CSS, JavaScript
- **Version Control:** Git
- **Repository:** GitHub
- **Development Environment:** Kiro IDE

### For Hardware:

No dedicated hardware is required.

The project is designed to run on a **laptop/desktop computer** with:

- Laptop/PC
- Webcam or video file
- Standard computing environment

Raspberry Pi and microcontrollers were part of the original conceptual architecture, but the implemented project uses a laptop-based approach.


---

## 🖥️ Screenshots

### Page 1 — Video Upload
![Upload Page](images/Screenshot%20(7).png)
 upload zone with mosquito icon, drag & drop, TAKE ATTENDANCE button
---

### AI Scanning Overlay
![AI Scanning](images/Screenshot%20(8).png)
Analyzing Page: Uploads the video, detects mosquitoes, tracks their movement, generates attendance data, and finalizes the attendance report.
---

### Page 2 — Attendance Dashboard
![Attendance Dashboard](images/Screenshot%20(6).png)
Take Attendance Page: Displays the total mosquito count, number entered, absent, and left, along with the final attendance percentage. It also shows each mosquito’s ID, entry time, and leave time for detailed tracking.
---
# Project Demo
<video controls src="WhatsApp Video 2026-09-12 at 04.40.42.mp4" title=""></video>

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
Team Contributions

Sarah Basil: Frontend design and development, user interface, video upload and attendance dashboard, project integration and testing.

Theertha S B: Backend development, mosquito detection and tracking, attendance calculation, video processing and system testing.

## 👩‍💻 Author

**theertha S B**
GitHub: [@sarahbasil03-ctrl](https://github.com/sarahbasil03-ctrl)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
Made with ❤️ at TinkerHub Useless Projects
