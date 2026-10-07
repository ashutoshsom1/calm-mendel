// Background Service Worker (Manifest V3)
// Handles extension lifecycle and badge counts

chrome.runtime.onInstalled.addListener(async () => {
  console.log("LinkedIn Job Hunter Co-Pilot extension installed.");
  
  // Initialize default local storage values
  const data = await chrome.storage.local.get(["dailyCount", "lastResetDate", "profile"]);
  const today = new Date().toISOString().slice(0, 10);
  
  if (!data.lastResetDate || data.lastResetDate !== today) {
    await chrome.storage.local.set({
      dailyCount: 0,
      lastResetDate: today
    });
  }
  
  if (!data.profile) {
    // Default fallback profile
    await chrome.storage.local.set({
      profile: {
        fullName: "Ashutosh Somvanshi",
        phone: "9876543210",
        noticePeriodDays: "30",
        currentCtc: "25",
        expectedCtc: "32",
        yearsExperience: "6",
        authorizedToWork: true,
        requiresSponsorship: false,
        willingToRelocate: true,
        hasPmp: true,
        hasCsm: true
      }
    });
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      if (message.action === "getDailyCount") {
        const today = new Date().toISOString().slice(0, 10);
        const data = await chrome.storage.local.get(["dailyCount", "lastResetDate"]);
        let count = data.dailyCount || 0;
        if (data.lastResetDate !== today) {
          count = 0;
          await chrome.storage.local.set({ dailyCount: 0, lastResetDate: today });
        }
        sendResponse({ success: true, count });
      } else if (message.action === "incrementDailyCount") {
        const data = await chrome.storage.local.get("dailyCount");
        const newCount = (data.dailyCount || 0) + 1;
        await chrome.storage.local.set({ dailyCount: newCount });
        await chrome.action.setBadgeText({ text: String(newCount) });
        await chrome.action.setBadgeBackgroundColor({ color: "#0A66C2" });
        sendResponse({ success: true, newCount });
      } else {
        sendResponse({ success: false, error: "Unknown action" });
      }
    } catch (err) {
      sendResponse({ success: false, error: err.message });
    }
  })();
  return true; // Keep message channel open for async response
});
