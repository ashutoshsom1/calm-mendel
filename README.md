# LinkedIn Premium Full-Funnel Job Hunter (Program Manager Edition)

An autonomous job search, matching, application, and recruiter outreach system designed specifically for **Program Managers** leveraging **LinkedIn Premium**.

---

## 🎯 Features

1. **LinkedIn Premium Lead Extractor**:
   - Captures **Hiring Managers** and **Recruiters** listed under *"Meet the hiring team"* on job listings.
   - Automatically drafts high-converting, personalized **InMail pitches** tailored to the job description and your PM track record.
2. **Safe Automated Easy-Apply**:
   - Uses real Google Chrome via Playwright with anti-detection masking (`navigator.webdriver` stripped, human mouse jitter, random keystroke delays).
   - Solves dynamic screening questions (Agile/Scrum experience, notice period, compensation, certifications, work authorization).
   - Selects/uploads your resume automatically.
3. **Account Safety Guardrails**:
   - Enforces a daily cap (default: **25 applications/day**) to protect your LinkedIn Premium account from shadowbans or checkpoints.
   - Random delays between applications (15–35 seconds) to mimic human browsing behavior.
   - Optional **Co-Pilot Review Mode (`--review`)**: pauses at the final review screen so you can verify before clicking submit.
4. **Persistent Session (Zero Cleartext Passwords)**:
   - Uses a persistent browser profile (`session_data/chrome_profile`).
   - You log in once manually through Chrome (with full 2FA/OTP support); the session is safely remembered.
5. **Job Pipeline CRM & CSV Export**:
   - Built-in SQLite database (`data/jobs.db`) tracking every discovered job, application status, recruiter contact, and timestamps.
   - Export your entire pipeline to CSV with a single command.

---

## 🚀 Quick Start Guide

### Step 1: Configure Your Profile & Resume
1. **Add your resume**:
   Drop your Program Manager resume (PDF or DOCX) into the `resumes/` folder:
   ```powershell
   # Example:
   copy "C:\path\to\Your_Resume.pdf" resumes\
   ```
2. **Update your details in `config/profile.yaml`**:
   Open [config/profile.yaml](file:///c:/Users/ashutosh.somvanshi/Documents/antigravity/calm-mendel/config/profile.yaml) and customize:
   - Your contact info (Phone, Email, LinkedIn URL)
   - Target locations (e.g. `Bengaluru`, `Remote`, `India`)
   - Notice period and compensation expectations
   - Years of experience with PM skills (Agile, JIRA, Stakeholder Management, PMP, CSM)

---

### Step 2: Initialize System
Run the initialization check:
```powershell
.\.venv\Scripts\python.exe cli.py init
```

---

### Step 3: One-Time LinkedIn Login
Launch Google Chrome to log into your LinkedIn Premium account and persist your session:
```powershell
.\.venv\Scripts\python.exe cli.py login
```
- A Google Chrome window will open to `https://www.linkedin.com/login`.
- Log in normally (including 2FA / OTP if prompted).
- Once you see your LinkedIn homepage/feed, return to your terminal and press **Enter**.
- *Your session is now securely saved in `session_data/`!*

---

### Step 4: Search & Discover Program Manager Jobs
Scrape LinkedIn for target roles and capture hiring team leads:
```powershell
# Default search (Program Manager in your configured locations)
.\.venv\Scripts\python.exe cli.py search

# Custom search:
.\.venv\Scripts\python.exe cli.py search --keyword "Technical Program Manager" --location "Remote" --pages 3
```

---

### Step 5: View Premium Hiring Leads & InMail Pitches
View hiring managers discovered from the job listings and review your personalized outreach drafts:
```powershell
# List all captured hiring leads:
.\.venv\Scripts\python.exe cli.py leads

# View the full generated InMail pitch for Lead ID 1:
.\.venv\Scripts\python.exe cli.py leads --view-draft 1
```

---

### Step 6: Run Automated Applications (Easy Apply)
Apply to discovered jobs matching your criteria:

```powershell
# Run with Human Review (Recommended for your first run):
# Pauses at the final submit screen so you can inspect before submitting!
.\.venv\Scripts\python.exe cli.py apply --review

# Autonomous run (up to 15 jobs, minimum 50% match score):
.\.venv\Scripts\python.exe cli.py apply --limit 15 --min-score 50

# Headless mode:
.\.venv\Scripts\python.exe cli.py apply --headless
```

---

### Step 7: Check Status & Export Tracking
Monitor your progress and export your pipeline to a spreadsheet:
```powershell
# View summary table:
.\.venv\Scripts\python.exe cli.py status

# Export to CSV:
.\.venv\Scripts\python.exe cli.py export
```
The export will be saved to `data/job_applications.csv`.

---

## 🛡️ LinkedIn Premium Best Practices & Safety Rules
1. **Pacing is Key**: Do not apply to more than 25–35 jobs per day. The bot automatically enforces this limit.
2. **Combine Applications with InMail**: Applications sent within 24 hours of posting combined with a polite InMail to the recruiter have a **3x higher response rate**.
3. **Session Warm-up**: Keep your normal browsing activity on LinkedIn (reading posts, messaging connections) so your traffic fingerprint remains organic.
