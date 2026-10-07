// Content script running inside LinkedIn Jobs pages
// Handles DOM inspection, autofilling Easy Apply questions, and scraping hiring managers

console.log("LinkedIn Job Hunter Co-Pilot content script active.");

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      if (message.action === "scrape_job_and_recruiter") {
        const details = scrapeCurrentJobDetails();
        sendResponse({ success: true, details });
      } else if (message.action === "autofill_modal") {
        const profile = message.profile || {};
        const count = autofillEasyApplyModal(profile);
        sendResponse({ success: true, fieldsFilled: count });
      } else if (message.action === "detect_modal") {
        const modal = document.querySelector("div[role='dialog'], .jobs-easy-apply-modal");
        sendResponse({ success: true, isModalOpen: Boolean(modal) });
      } else {
        sendResponse({ success: false, error: "Unknown action" });
      }
    } catch (err) {
      sendResponse({ success: false, error: err.message });
    }
  })();
  return true; // Keep channel open
});

function scrapeCurrentJobDetails() {
  // Extract Job Title
  const titleEl = document.querySelector(".job-details-jobs-unified-top-card__job-title, .jobs-unified-top-card__job-title, h1");
  const title = titleEl ? titleEl.innerText.trim() : "Program Manager";

  // Extract Company Name
  const companyEl = document.querySelector(".job-details-jobs-unified-top-card__company-name, .jobs-unified-top-card__company-name, .jobs-unified-top-card__subtitle-primary-grouping a");
  const company = companyEl ? companyEl.innerText.trim() : "Target Company";

  // Extract Hiring Team / Recruiter Card (LinkedIn Premium feature)
  let recruiter = null;
  const hirerCard = document.querySelector(".hirer-card__hirer-information, div[data-view-name='job-details-hirer-card'], .jobs-poster");
  
  if (hirerCard) {
    const nameEl = hirerCard.querySelector(".jobs-poster__name, .hirer-card__name, strong, a");
    const titleEl = hirerCard.querySelector(".hirer-card__hirer-job-title, .jobs-poster__title");
    const linkEl = hirerCard.querySelector("a[href*='/in/']");

    if (nameEl && linkEl) {
      let href = linkEl.getAttribute("href") || "";
      if (href.startsWith("/")) href = "https://www.linkedin.com" + href;
      recruiter = {
        name: nameEl.innerText.trim(),
        headline: titleEl ? titleEl.innerText.trim() : "Recruiter",
        profileUrl: href.split("?")[0]
      };
    }
  }

  return { title, company, recruiter };
}

function autofillEasyApplyModal(profile) {
  const modal = document.querySelector("div[role='dialog'], .jobs-easy-apply-modal");
  if (!modal) return 0;

  let fieldsFilled = 0;

  // 1. Solve Radio Buttons (Yes/No questions)
  const fieldsets = modal.querySelectorAll("fieldset");
  fieldsets.forEach((fs) => {
    const legend = fs.querySelector("legend, span.fb-dash-form-element__label");
    const qText = (legend ? legend.innerText : fs.innerText).toLowerCase();
    const radios = fs.querySelectorAll("input[type='radio'], label");

    // Rules
    let desired = "yes";
    if (qText.includes("sponsorship") || qText.includes("require visa")) {
      desired = profile.requiresSponsorship ? "yes" : "no";
    } else if (qText.includes("authorized") || qText.includes("relocate") || qText.includes("experience") || qText.includes("pmp") || qText.includes("scrum") || qText.includes("background")) {
      desired = "yes";
    }

    radios.forEach((r) => {
      const rText = r.innerText.trim().toLowerCase();
      if ((desired === "yes" && (rText === "yes" || rText === "true")) ||
          (desired === "no" && (rText === "no" || rText === "false"))) {
        r.click();
        fieldsFilled++;
      }
    });
  });

  // 2. Solve Select / Dropdowns
  const selects = modal.querySelectorAll("select");
  selects.forEach((sel) => {
    const label = sel.getAttribute("aria-label") || "";
    const options = Array.from(sel.options);

    if (options.length > 1 && sel.selectedIndex <= 0) {
      // Find matching option or select 2nd option
      const yesOpt = options.find(o => o.text.toLowerCase().includes("yes") || o.text.toLowerCase().includes("fluent") || o.text.toLowerCase().includes("30"));
      if (yesOpt) {
        sel.value = yesOpt.value;
      } else {
        sel.selectedIndex = 1;
      }
      sel.dispatchEvent(new Event("change", { bubbles: true }));
      fieldsFilled++;
    }
  });

  // 3. Solve Text & Numeric Inputs
  const inputs = modal.querySelectorAll("input[type='text'], input[type='number']");
  inputs.forEach((inp) => {
    if (inp.value && inp.value.trim() !== "") return; // Don't overwrite existing user data

    const labelEl = modal.querySelector(`label[for='${inp.id}']`);
    const qText = (labelEl ? labelEl.innerText : inp.getAttribute("aria-label") || "").toLowerCase();

    let val = "";
    if (qText.includes("notice")) {
      val = profile.noticePeriodDays || "30";
    } else if (qText.includes("current") && (qText.includes("ctc") || qText.includes("salary"))) {
      val = profile.currentCtc || "25";
    } else if (qText.includes("expected") && (qText.includes("ctc") || qText.includes("salary"))) {
      val = profile.expectedCtc || "32";
    } else if (qText.includes("years") || qText.includes("experience")) {
      val = profile.yearsExperience || "6";
    } else if (qText.includes("phone") || qText.includes("mobile")) {
      val = profile.phone || "9876543210";
    }

    if (val) {
      inp.value = val;
      inp.dispatchEvent(new Event("input", { bubbles: true }));
      inp.dispatchEvent(new Event("change", { bubbles: true }));
      fieldsFilled++;
    }
  });

  return fieldsFilled;
}
