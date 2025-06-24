---



---
# 🕵️‍♂️ XPOSE — Digital Risk Scanner

> ⚔️ Scan. Analyze. Expose.  
> **XPOSE** is a full-stack OSINT-based intelligence platform that analyzes your email and username across platforms, generates risk reports, and provides security recommendations — all in a seamless Flask + ShellScript + HTML/JS interface.
## 🚀 Key Features

- 🔍 **Username + Email Exposure Scanning** via Sherlock, Holehe, WhatsMyName, and theHarvester  
- 📊 **Risk Scoring** algorithm based on breach count, platform hits, and domain data  
- 📝 **Auto-Generated Reports** (text + data-backed)  
- 🌐 **REST API** with async background scanning (threaded)  
- 🗃️ **SQLite3 Database** for all scans  
- 📜 **Modular Scripts** (Shell + Python) for maintainability  
- 📦 Built for extensibility — add more OSINT tools easily  



## 🛠️ Tech Stack

| Layer      | Tech                             |
|------------|----------------------------------|
| Frontend   | HTML, CSS, JavaScript            |
| Backend    | Python Flask, SQLite             |
| Async Proc | Python subprocess + threading    |
| Scripts    | Bash (Shellscripts)              |
| Tools      | `sherlock`, `holehe`, `h8mail`, `theHarvester`, `whatsmyname` |
| Storage    | SQLite3 DB + Text-based Reports  |

---

## 🧠 Workflow Diagram

```mermaid
graph TD
    A[User Submits Form] --> B[Flask Backend]
    B --> C[Store in SQLite DB]
    C --> D[Launch Background Processor]
    D --> E[Run OSINT Tools]
    E -->|emailripping| F[Email Analysis]
    E -->|usernameripping| G[Username Analysis]
    F --> H[Generate Email Report]
    G --> I[Generate Username Report]
    H --> J[Calculate Risk Scores]
    I --> J
    J --> K[Update Database]
    K --> L[Display Results]
    L --> M[PDF Export Option]
````

---

## 🗃️ Database Schema

```sql
CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    username TEXT,
    domain TEXT,
    platforms TEXT,
    form_data TEXT,
    risk_score INTEGER,
    email_report TEXT,
    username_report TEXT,
    recommendations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);
```

---

## 🧩 Project Structure

```
XPOSE/
│
├── app.py                 # Flask main app
├── processor.py           # Async processor for running scans
├── xpose.db               # SQLite database (auto-created)
├── reports/               # Email report storage
├── username_reports/      # Username report storage
├── emailripping           # Shell script: Email scanner
├── usernameripping        # Shell script: Username scanner
├── Frontend/
│   ├── index.html         # Submission form
│   └── results.html       # Results page
└── README.md              # You are here
```

---

## 📡 API Endpoints

| Route                | Method | Purpose                            |
| -------------------- | ------ | ---------------------------------- |
| `/submit`            | POST   | Submit a scan request              |
| `/status/<scan_id>`  | GET    | Check scan status + report + score |
| `/results/<scan_id>` | GET    | Serve frontend results page        |

> All responses are in JSON except `/results/<id>` which serves HTML.

---

## ⚙️ How to Run

### 1. Clone Repo

```bash
git clone https://github.com/yourusername/xpose.git
cd xpose
```

### 2. Install Dependencies

Make sure you have the following OSINT tools installed:

```bash
pip install flask flask-cors
sudo apt install sherlock holehe theharvester h8mail
```

> 🔁 **Note:** `sherlock`, `holehe`, `whatsmyname`, and `theHarvester` must be accessible globally (via `$PATH`). You may need to clone and install some tools manually.

### 3. Run the App

```bash
python3 app.py
```

Access the form at:
`http://localhost:5000/Frontend/index.html`

Status endpoint example:
`http://localhost:5000/status/1`

---

## 🧪 Sample JSON for Testing `/submit`

```json
{
  "email": "user@example.com",
  "username": "userhandle",
  "platforms": ["github", "twitter", "linkedin"]
}
```

---

## 📌 How It Works (Flow Summary)

| Stage         | Description                                     | Time       |
| ------------- | ----------------------------------------------- | ---------- |
| 1. Submission | User fills and submits frontend form            | Instant    |
| 2. Queueing   | Data stored in SQLite, background thread starts | <1s        |
| 3. Scanning   | Email & username OSINT tools execute            | \~2–5 mins |
| 4. Reporting  | Risk calculated, reports saved to `.txt`        | <10s       |
| 5. Results    | API status route gives final data/score         | Instant    |

---

## 📌 Recommendations Logic

| Risk Score | Label       | Recommendation Summary           |
| ---------- | ----------- | -------------------------------- |
| 70–100     | 🔴 Critical | Change all passwords, enable 2FA |
| 40–69      | 🟠 High     | Review all platforms' privacy    |
| 0–39       | 🟢 Normal   | Monitor occasionally             |

---

## 💡 Future Scope Ideas

* 🧾 PDF Report Export
* 🧠 AI-based Threat Pattern Clustering
* 📤 Email Notifications for Scan Results
* 🧑‍💼 Admin Dashboard to Manage All Scans
* 🧱 Modular Tool Plugin System (plug-in new scanners)

---

## 🧑 Author & Credits

* 👤 **@dhruvillearning**
* 🛠 Built with love, Linux, and late-night debugging
* 💬 DM on GitHub or open an issue for suggestions!

```

---


```
