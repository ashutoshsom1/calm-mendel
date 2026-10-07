// Web Dashboard Client Script

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const jobTitleInput = document.getElementById("jobTitle");
  const companyNameInput = document.getElementById("companyName");
  const recruiterNameInput = document.getElementById("recruiterName");
  const candidateNameInput = document.getElementById("candidateName");
  const btnGeneratePitch = document.getElementById("btnGeneratePitch");
  const outputPitch = document.getElementById("outputPitch");
  const btnCopyPitch = document.getElementById("btnCopyPitch");

  const btnSaveProfile = document.getElementById("btnSaveProfile");
  const btnDownloadConfig = document.getElementById("btnDownloadConfig");

  const crmBody = document.getElementById("crmBody");
  const btnAddRow = document.getElementById("btnAddRow");
  const btnExportCsv = document.getElementById("btnExportCsv");

  // Initial Sample Applications
  const defaultApplications = [
    { role: "Senior Technical Program Manager", company: "Microsoft", date: "2026-10-05", status: "Interviewing" },
    { role: "Staff Program Manager - Cloud Infrastructure", company: "Google", date: "2026-10-06", status: "Applied" },
    { role: "Lead Agile Program Manager", company: "Amazon", date: "2026-10-07", status: "Applied" }
  ];

  let applications = JSON.parse(localStorage.getItem("job_applications") || "null") || defaultApplications;

  // 1. InMail Generator Logic
  function generatePitchText() {
    const title = jobTitleInput.value.trim() || "Program Manager";
    const company = companyNameInput.value.trim() || "Target Company";
    const recruiter = recruiterNameInput.value.trim();
    const candidate = candidateNameInput.value.trim() || "Ashutosh Somvanshi";

    const greeting = recruiter ? `Hi ${recruiter.split(" ")[0]},` : "Hi there,";

    return `Subject: ${title} Application | ${candidate}\n\n` +
      `${greeting}\n\n` +
      `I hope you're having a great week! I recently submitted my application for the ${title} position at ${company} and wanted to personally connect.\n\n` +
      `With 6+ years leading complex, cross-functional engineering initiatives across distributed teams, my background includes:\n` +
      `• Enterprise Agile transformation & governance (accelerated release velocity by 30%)\n` +
      `• Cross-functional stakeholder alignment, roadmapping, and technical risk mitigation\n` +
      `• Budget management and delivery ownership across multi-million dollar initiatives\n\n` +
      `Given ${company}'s ongoing scaling and goals, I'd welcome the chance for a brief 10-minute sync to discuss how my track record aligns with your team's objectives.\n\n` +
      `Best regards,\n${candidate}\n` +
      `LinkedIn: linkedin.com/in/ashutosh-somvanshi`;
  }

  // Generate initial pitch
  outputPitch.value = generatePitchText();

  btnGeneratePitch.addEventListener("click", () => {
    outputPitch.value = generatePitchText();
    outputPitch.focus();
  });

  btnCopyPitch.addEventListener("click", () => {
    navigator.clipboard.writeText(outputPitch.value);
    btnCopyPitch.innerText = "✔ Copied!";
    setTimeout(() => {
      btnCopyPitch.innerText = "Copy Pitch";
    }, 2000);
  });

  // 2. Profile Configuration Logic
  btnSaveProfile.addEventListener("click", () => {
    const profileData = {
      name: document.getElementById("pName").value,
      phone: document.getElementById("pPhone").value,
      location: document.getElementById("pLocation").value,
      notice: document.getElementById("pNotice").value,
      currentCtc: document.getElementById("pCurrentCtc").value,
      expectedCtc: document.getElementById("pExpectedCtc").value,
      years: document.getElementById("pYears").value,
      pmp: document.getElementById("pPmp").checked,
      csm: document.getElementById("pCsm").checked,
      auth: document.getElementById("pAuth").checked,
      spons: document.getElementById("pSpons").checked,
    };
    localStorage.setItem("hunter_profile", JSON.stringify(profileData));
    btnSaveProfile.innerText = "✔ Saved to Browser!";
    setTimeout(() => {
      btnSaveProfile.innerText = "💾 Save Profile";
    }, 2500);
  });

  btnDownloadConfig.addEventListener("click", () => {
    const name = document.getElementById("pName").value;
    const phone = document.getElementById("pPhone").value;
    const location = document.getElementById("pLocation").value;
    const notice = document.getElementById("pNotice").value;
    const currentCtc = document.getElementById("pCurrentCtc").value;
    const expectedCtc = document.getElementById("pExpectedCtc").value;
    const years = document.getElementById("pYears").value;

    const yamlContent = 
`personal:
  full_name: "${name}"
  phone_number: "${phone}"
  current_location: "${location}"

target_job:
  roles:
    - "Program Manager"
    - "Technical Program Manager"
  locations:
    - "${location}"

screening_answers:
  notice_period_days: ${notice}
  current_ctc_in_lpa: "${currentCtc}"
  expected_ctc_in_lpa: "${expectedCtc}"
  skills_experience_years:
    "program management": ${years}
    "agile": ${years}
    "jira": ${years}
`;

    const blob = new Blob([yamlContent], { type: "text/yaml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "profile.yaml";
    a.click();
    URL.revokeObjectURL(url);
  });

  // 3. Application CRM Render & Management
  function renderCrmTable() {
    crmBody.innerHTML = "";
    applications.forEach((app, idx) => {
      const tr = document.createElement("tr");
      const statusClass = app.status === "Interviewing" ? "status-interview" : "status-applied";
      tr.innerHTML = `
        <td><strong>${app.role}</strong></td>
        <td>${app.company}</td>
        <td>${app.date}</td>
        <td><span class="status-tag ${statusClass}">${app.status}</span></td>
        <td>
          <button class="btn btn-sm btn-outline delete-btn" data-idx="${idx}">Delete</button>
        </td>
      `;
      crmBody.appendChild(tr);
    });

    document.querySelectorAll(".delete-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const i = parseInt(e.target.dataset.idx);
        applications.splice(i, 1);
        localStorage.setItem("job_applications", JSON.stringify(applications));
        renderCrmTable();
      });
    });
  }

  renderCrmTable();

  btnAddRow.addEventListener("click", () => {
    const role = prompt("Enter Job Title:", "Senior Program Manager");
    if (!role) return;
    const company = prompt("Enter Company Name:", "Tech Corp");
    if (!company) return;

    const today = new Date().toISOString().slice(0, 10);
    applications.unshift({
      role,
      company,
      date: today,
      status: "Applied"
    });

    localStorage.setItem("job_applications", JSON.stringify(applications));
    renderCrmTable();
  });

  btnExportCsv.addEventListener("click", () => {
    let csv = "Role,Company,Applied Date,Status\n";
    applications.forEach((a) => {
      csv += `"${a.role}","${a.company}","${a.date}","${a.status}"\n`;
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "linkedin_applications_pipeline.csv";
    a.click();
    URL.revokeObjectURL(url);
  });
});
