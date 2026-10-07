# Chrome Web Store Metadata & Readiness

## Extension Info
- **Name**: LinkedIn Job Hunter Co-Pilot
- **Summary**: Safe LinkedIn Easy-Apply assistant and personalized recruiter InMail outreach generator for Program Managers.
- **Version**: 1.0.0
- **Category**: Productivity / Workflow
- **Languages**: English

## Store Listing Description
Accelerate your Program Manager job search safely on LinkedIn.

LinkedIn Job Hunter Co-Pilot helps Program Managers auto-fill repetitive Easy Apply screening questions and craft tailored, high-converting outreach notes to recruiters using LinkedIn Premium perks.

### Key Features:
- ⚡ **1-Click Easy Apply Auto-Fill**: Auto-fills screening questions (years of Agile/Scrum experience, notice period, compensation, certifications, work authorization) based on your custom profile.
- ✉️ **Recruiter InMail Generator**: Automatically identifies the hiring team member listed on the job posting and crafts a personalized 3-part outreach pitch highlighting your track record.
- 🛡️ **Account Safety Guardrails**: Enforces a strict 25-application daily cap and human pacing so your LinkedIn account remains safe and compliant.
- 🔒 **Privacy-First**: Operates 100% locally in your active browser session. Zero credentials, passwords, or personal data ever leave your computer.

## Permissions Justification
- `storage`: Required to save user screening answers (e.g. notice period, compensation, certifications) and maintain the safe daily application counter locally on the device.
- `activeTab`: Required to interact with the active LinkedIn Jobs page when the user explicitly clicks the extension action to autofill or scrape recruiter information.
- `scripting`: Required to inject autofill actions into the active LinkedIn job application dialog on user demand.
- `host_permissions (*://*.linkedin.com/*)`: Required exclusively to detect and interact with LinkedIn job posting cards and Easy Apply modal windows.

## Privacy & Data Use
- **Does the extension collect personal data?** No remote collection. All data stays in `chrome.storage.local` on the user's computer.
- **Does the extension sell or transfer data to third parties?** No.
- **Single Purpose**: Assists users with applying to job postings and generating outreach notes on LinkedIn.
