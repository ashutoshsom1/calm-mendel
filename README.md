# LinkedIn Premium Full-Funnel Job Hunter (Program Manager Edition)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fashutoshsom1%2Fcalm-mendel)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-automated%20windows%20release-brightgreen.svg)](https://github.com/ashutoshsom1/calm-mendel/actions)

An autonomous job search, matching, application, and recruiter outreach system designed specifically for **Program Managers** leveraging **LinkedIn Premium**.

---

## 🌐 Deploy to Vercel (1-Click Public Web Dashboard)

You can deploy the web dashboard directly to **Vercel** with zero configuration:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fashutoshsom1%2Fcalm-mendel)

The Vercel-deployed web app includes:
- **Personalized InMail Pitch Drafter**: Craft high-converting outreach notes for recruiters and hiring managers.
- **Screening Answers Brain**: Configure standard answers (years of experience, notice period, CTC, PMP/CSM certifications) and download `profile.yaml`.
- **Application Pipeline CRM**: Track submitted jobs, interview statuses, and export to CSV.
- **Extension Guide**: Simple instructions for users to install the companion extension.

---

## 🛡️ Why This Architecture is 100% Safe (No Bans)

| Traditional Cloud Bots | Our Hybrid Co-Pilot Architecture |
|---|---|
| ❌ Runs on AWS/Vercel datacenter IPs (LinkedIn flags & blocks cloud IPs immediately). | ✅ Runs directly in your **residential browser** via the Chrome Extension or local runner. |
| ❌ Requires storing your personal LinkedIn password or cookies on a cloud database. | ✅ Uses your **existing active LinkedIn tab** — zero passwords or cookies ever shared. |
| ❌ Exceeds rate limits and triggers CAPTCHAs. | ✅ Built-in safety engine caps applications at **25/day** with human pacing. |

---

## 🚀 3 Ways Anyone Can Use This

### 1. 🌐 The Web Dashboard (Instant Access via Vercel)
Visit the live Vercel website to draft recruiter InMail pitches, configure your profile, and manage your pipeline tracker.

### 2. 🧩 The Chrome / Edge Extension (15-Second Install)
1. Download or clone this repository.
2. In Chrome or Edge, navigate to `chrome://extensions` and turn on **Developer mode** (top right).
3. Click **Load unpacked** and select the `extension` folder.
4. Open any LinkedIn job posting:
   - Click **⚡ Auto-Fill Easy Apply Form** to automatically answer screening questions.
   - Click **✉️ Draft Recruiter InMail** to extract the hiring manager and generate a pitch.

### 3. 💻 The Local Python Runner / `run.bat` (Power Users)
- **Windows Users (No Python needed)**: Double-click `run.bat`. It automatically sets up Python and presents an interactive menu.
- **Developers**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\activate
  pip install -e .
  linkedin-jobhunter --help
  ```

---

## 🛠️ CLI Reference

| Command | Action |
|---|---|
| `linkedin-jobhunter init` | Initializes workspace directories and config |
| `linkedin-jobhunter login` | Opens Chrome to authenticate with LinkedIn & saves persistent session |
| `linkedin-jobhunter search` | Searches PM jobs and extracts hiring manager leads |
| `linkedin-jobhunter apply --review` | Runs Easy Apply with review before submission |
| `linkedin-jobhunter leads` | Displays captured recruiters/hiring managers and tailored InMail drafts |
| `linkedin-jobhunter status` | Displays live pipeline summary |
| `linkedin-jobhunter export` | Exports pipeline tracking to `data/job_applications.csv` |

---

## 📄 License
MIT License. Open-source and free for personal and commercial career development.
