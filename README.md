# LinkedIn Premium Full-Funnel Job Hunter (Program Manager Edition)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-automated%20windows%20release-brightgreen.svg)](https://github.com/ashutoshsom1/calm-mendel/actions)

An autonomous job search, matching, application, and recruiter outreach system designed specifically for **Program Managers** leveraging **LinkedIn Premium**.

---

## 🚀 How Anyone Can Use This (Even Without Python!)

### 🌟 Option 1: One-Click Launcher (Easiest - Recommended)
If you do not have Python installed or do not want to use command line tools:

1. **Download this repository**:
   Click the green **`< > Code`** button at the top of GitHub, then click **`Download ZIP`**.
2. **Extract the ZIP** anywhere on your computer.
3. **Double-click `run.bat`**:
   - If Python is missing, the script will automatically install it via Windows Package Manager.
   - It sets up all dependencies in a self-contained local folder.
   - It opens an easy interactive menu where you just type numbers (e.g. `1` to login, `2` to search, `3` to apply):

```text
================================================================
      LinkedIn Premium Job Hunter - Control Center
================================================================

  [1] One-Time Login (Connect your LinkedIn Premium account)
  [2] Search & Match Jobs (Scrape roles & hiring team leads)
  [3] Review & Apply (Co-Pilot: review each job before submit)
  [4] Autonomous Apply (Fast batch apply within safety caps)
  [5] View Discovered Hiring Managers & InMail Pitches
  [6] View Application Pipeline Status
  [7] Export Applications to CSV / Excel
  [8] Open Configuration File (config\profile.yaml)
  [9] Exit

================================================================
Enter your choice [1-9]:
```

---

### 💻 Option 2: Standard Developer Installation
If you have Python 3.9+ and Git:

```powershell
# Clone the repository
git clone https://github.com/ashutoshsom1/calm-mendel.git
cd calm-mendel

# Create & activate a virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install package
pip install -e .
```

After installation, the CLI tool `linkedin-jobhunter` is available globally in your environment.

---

## 🎯 Key Features

1. **LinkedIn Premium Lead Harvester**:
   - Captures **Hiring Managers** and **Recruiters** listed under *"Meet the hiring team"* on job listings.
   - Automatically drafts high-converting, personalized **InMail pitches** tailored to the job description and your PM track record.
2. **Safe Automated Easy-Apply**:
   - Uses real Google Chrome via Playwright with anti-detection masking (`navigator.webdriver` stripped, human mouse jitter, random keystroke delays).
   - Solves dynamic screening questions (Agile/Scrum experience, notice period, compensation, certifications, work authorization).
   - Selects/uploads your resume automatically.
3. **Account Safety Guardrails**:
   - Enforces a daily cap (default: **25 applications/day**) to protect your LinkedIn Premium account from shadowbans or checkpoints.
   - Random delays between applications (15–35 seconds) to mimic human browsing behavior.
   - **Co-Pilot Review Mode (`--review`)**: pauses at the final review screen so you can verify before clicking submit.
4. **Persistent Session (Zero Cleartext Passwords)**:
   - Uses a persistent browser profile (`session_data/chrome_profile`).
   - You log in once manually through Chrome (with full 2FA/OTP support); the session is safely remembered.
5. **Job Pipeline CRM & CSV Export**:
   - Built-in SQLite database (`data/jobs.db`) tracking every discovered job, application status, recruiter contact, and timestamps.
   - Export your entire pipeline to CSV with a single command.

---

## 📋 3-Step Setup Guide

### 1. Add Your Resume & Edit Profile
- Place your Program Manager resume (PDF or DOCX) in the `resumes/` folder.
- Open [config/profile.yaml](config/profile.yaml) (or select option `8` in `run.bat`) to adjust your phone, target locations, notice period, and salary expectation.

### 2. Connect Your LinkedIn Account (Once)
Run:
```powershell
linkedin-jobhunter login
```
*(Or select option `1` in `run.bat`)*. Google Chrome will open. Log into LinkedIn Premium and complete any 2FA/OTP. Your session is now saved securely in your local folder!

### 3. Search & Apply
- Search roles: `linkedin-jobhunter search` *(Option `2` in `run.bat`)*
- Review & Apply: `linkedin-jobhunter apply --review` *(Option `3` in `run.bat`)*
- View Hiring Managers & InMails: `linkedin-jobhunter leads` *(Option `5` in `run.bat`)*

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

## 🛡️ LinkedIn Safety Best Practices
1. **Pacing is Key**: Do not apply to more than 25–35 jobs per day. The bot automatically enforces this limit.
2. **Combine Applications with InMail**: Applications sent within 24 hours of posting combined with a polite InMail to the recruiter have a **3x higher response rate**.
3. **Session Warm-up**: Keep your normal browsing activity on LinkedIn (reading posts, messaging connections) so your traffic fingerprint remains organic.
