// Popup Script (Manifest V3)

document.addEventListener("DOMContentLoaded", async () => {
  const tabStatusEl = document.getElementById("tabStatus");
  const dailyCountText = document.getElementById("dailyCountText");
  const progressFill = document.getElementById("progressFill");
  const btnAutoFill = document.getElementById("btnAutoFill");
  const btnScrapeRecruiter = document.getElementById("btnScrapeRecruiter");
  const resultBox = document.getElementById("resultBox");
  const resultContent = document.getElementById("resultContent");
  const btnCopy = document.getElementById("btnCopy");

  // 1. Fetch Daily Application Count from Background
  try {
    const response = await chrome.runtime.sendMessage({ action: "getDailyCount" });
    const count = response?.count || 0;
    const max = 25;
    dailyCountText.innerText = `${count} / ${max}`;
    const pct = Math.min(100, Math.round((count / max) * 100));
    progressFill.style.width = `${pct}%`;
  } catch (err) {
    console.error("Error fetching daily count:", err);
  }

  // 2. Check if current active tab is LinkedIn Jobs
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const isLinkedInJobs = tab?.url && tab.url.includes("linkedin.com/jobs");

  if (isLinkedInJobs) {
    tabStatusEl.innerText = "Connected";
    tabStatusEl.className = "status-badge connected";
  } else {
    tabStatusEl.innerText = "Inactive";
    tabStatusEl.className = "status-badge disconnected";
    btnAutoFill.disabled = true;
    btnScrapeRecruiter.disabled = true;
    btnAutoFill.title = "Open a LinkedIn Jobs page to use this feature";
    btnScrapeRecruiter.title = "Open a LinkedIn Jobs page to use this feature";
  }

  // 3. Handle Auto-Fill Button Click
  btnAutoFill.addEventListener("click", async () => {
    btnAutoFill.innerText = "Auto-filling...";
    try {
      const storage = await chrome.storage.local.get("profile");
      const profile = storage.profile || {};

      const res = await chrome.tabs.sendMessage(tab.id, {
        action: "autofill_modal",
        profile
      });

      if (res?.success) {
        btnAutoFill.innerText = `✔ Filled ${res.fieldsFilled} Fields!`;
        await chrome.runtime.sendMessage({ action: "incrementDailyCount" });
        setTimeout(() => {
          btnAutoFill.innerText = "⚡ Auto-Fill Easy Apply Form";
        }, 3000);
      } else {
        btnAutoFill.innerText = "No Easy Apply modal open";
        setTimeout(() => {
          btnAutoFill.innerText = "⚡ Auto-Fill Easy Apply Form";
        }, 2500);
      }
    } catch (err) {
      console.error(err);
      btnAutoFill.innerText = "Error (Make sure page is loaded)";
      setTimeout(() => {
        btnAutoFill.innerText = "⚡ Auto-Fill Easy Apply Form";
      }, 2500);
    }
  });

  // 4. Handle Draft Recruiter InMail Button Click
  btnScrapeRecruiter.addEventListener("click", async () => {
    btnScrapeRecruiter.innerText = "Extracting...";
    try {
      const res = await chrome.tabs.sendMessage(tab.id, {
        action: "scrape_job_and_recruiter"
      });

      if (res?.success && res.details) {
        const { title, company, recruiter } = res.details;
        const storage = await chrome.storage.local.get("profile");
        const applicantName = storage.profile?.fullName || "Candidate";

        let recruiterName = "Hiring Team";
        let pitch = "";

        if (recruiter && recruiter.name) {
          recruiterName = recruiter.name.split(" ")[0];
        }

        pitch = `Subject: ${title} Application | ${applicantName}\n\n` +
          `Hi ${recruiterName},\n\n` +
          `I recently applied for the ${title} position at ${company} and wanted to introduce myself directly.\n\n` +
          `With 6+ years delivering complex, cross-functional engineering initiatives, my core strengths include:\n` +
          `• End-to-end program governance and Agile transformation (reduced cycle times by 30%)\n` +
          `• Enterprise stakeholder alignment, budgeting, and risk management\n\n` +
          `I'd welcome the chance for a brief 10-minute introductory conversation regarding your team's goals.\n\n` +
          `Best regards,\n${applicantName}`;

        resultContent.innerText = pitch;
        resultBox.classList.remove("hidden");
        btnScrapeRecruiter.innerText = "✉️ Draft Recruiter InMail";
      } else {
        btnScrapeRecruiter.innerText = "No job details found";
        setTimeout(() => {
          btnScrapeRecruiter.innerText = "✉️ Draft Recruiter InMail";
        }, 2000);
      }
    } catch (err) {
      console.error(err);
      btnScrapeRecruiter.innerText = "Error extracting lead";
      setTimeout(() => {
        btnScrapeRecruiter.innerText = "✉️ Draft Recruiter InMail";
      }, 2000);
    }
  });

  // 5. Copy Pitch to Clipboard
  btnCopy.addEventListener("click", () => {
    navigator.clipboard.writeText(resultContent.innerText);
    btnCopy.innerText = "Copied!";
    setTimeout(() => {
      btnCopy.innerText = "Copy";
    }, 2000);
  });
});
