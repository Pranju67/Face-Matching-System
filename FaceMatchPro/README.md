# FaceMatch Pro
## AI Face Verification & Similarity System

A production-ready desktop application for comparing face images using pure
**OpenCV + NumPy** — no TensorFlow, no PyTorch, no heavy AI frameworks.

---

## Features

| Feature | Details |
|---------|---------|
| Multi-method similarity | Histogram + SSIM + LBP feature vectors |
| Haar cascade detection | Automatic face crop & normalization |
| Professional dark UI | CustomTkinter, glassmorphism cards |
| Verification history | Stored in MongoDB or in-memory fallback |
| Analytics dashboard | KPI cards + Matplotlib charts |
| PDF reports | ReportLab-generated professional reports |
| CSV export | One-click history export |
| Settings persistence | JSON settings file |

---

## Project Structure

```
FaceMatchPro/
├── app.py            Main application window + all UI tabs
├── database.py       MongoDB CRUD (with in-memory fallback)
├── face_matcher.py   OpenCV pipeline: detect → normalize → score
├── pdf_generator.py  ReportLab PDF report builder
├── settings.py       JSON-backed settings manager
├── utils.py          CSV export, formatting helpers
├── assets/           Icons / images (optional)
├── reports/          Auto-saved PDF reports
├── data/             settings.json persisted here
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Python 3.10+
```bash
python --version
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. MongoDB (optional)
The app works without MongoDB using an in-memory store.
If you want persistence across sessions:

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
```

**Windows:**
Download the installer from https://www.mongodb.com/try/download/community
and follow the wizard.

---

## Run

```bash
cd FaceMatchPro
python app.py
```

---

## Usage

1. **Compare Tab** — Upload two face images using *Browse Image*.  
   Click **Compare Faces**. Results appear in the right panel within seconds.

2. **History Tab** — Every comparison is stored automatically.  
   Search, filter by status, delete records, or export to CSV.

3. **Analytics Tab** — KPI overview and daily-trend bar chart.

4. **Settings Tab** — Adjust the similarity threshold (default 60 %),
   MongoDB connection details, and the PDF export directory.

---

## Similarity Algorithm

```
Final Score = 0.30 × Histogram  +  0.35 × SSIM  +  0.35 × LBP Features
```

| Score Range | Label |
|-------------|-------|
| 90 – 100 % | Excellent Match |
| 75 – 89 % | Strong Match |
| 60 – 74 % | Possible Match |
| 40 – 59 % | Weak Match |
| 0 – 39 % | No Match |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `customtkinter not found` | `pip install customtkinter` |
| `cv2 not found` | `pip install opencv-python` |
| `PIL not found` | `pip install Pillow` |
| MongoDB not connecting | App auto-falls back to in-memory store |
| PDF error | `pip install reportlab` |
| Charts missing | `pip install matplotlib` |

---

## License
MIT — free for personal and commercial use.
