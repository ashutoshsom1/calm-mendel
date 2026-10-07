import re
import urllib.parse
from typing import List, Dict, Any, Optional
from playwright.sync_api import Page
from rich.console import Console

from core.browser import human_delay, smooth_scroll
from database.models import save_job, save_lead
from config.config import AppConfig

console = Console()

# Core PM keywords for match scoring
PM_KEYWORDS = [
    "program manager",
    "technical program manager",
    "tpm",
    "agile",
    "scrum",
    "jira",
    "stakeholder management",
    "delivery",
    "roadmap",
    "cross-functional",
    "sdlc",
    "risk management",
    "pmp",
    "csm",
    "budget",
    "vendor",
    "cloud",
    "metrics",
]


class JobSearcher:
    def __init__(self, page: Page, config: AppConfig):
        self.page = page
        self.config = config

    def build_search_url(
        self,
        keyword: str,
        location: str,
        easy_apply_only: bool = True,
        date_posted: str = "past_week",
        start: int = 0,
    ) -> str:
        base_url = "https://www.linkedin.com/jobs/search/?"
        params = {
            "keywords": keyword,
            "location": location,
            "sortBy": "R",  # Relevant
            "start": str(start),
        }

        # Date posted filter
        if date_posted == "past_24h":
            params["f_TPR"] = "r86400"
        elif date_posted == "past_week":
            params["f_TPR"] = "r604800"
        elif date_posted == "past_month":
            params["f_TPR"] = "r2592000"

        # Easy Apply filter
        if easy_apply_only:
            params["f_AL"] = "true"

        # Work type (Remote = 2, Hybrid = 3, On-site = 1)
        work_types = []
        wt_cfg = self.config.target_job.get("work_types", {})
        if wt_cfg.get("onsite"):
            work_types.append("1")
        if wt_cfg.get("remote"):
            work_types.append("2")
        if wt_cfg.get("hybrid"):
            work_types.append("3")

        if work_types:
            params["f_WT"] = ",".join(work_types)

        return base_url + urllib.parse.urlencode(params)

    def search_jobs(
        self,
        keyword: str = "Program Manager",
        location: str = "Bengaluru, India",
        pages: int = 2,
    ) -> List[Dict[str, Any]]:
        discovered_jobs = []

        for page_idx in range(pages):
            start_offset = page_idx * 25
            url = self.build_search_url(
                keyword=keyword,
                location=location,
                easy_apply_only=self.config.target_job.get("easy_apply_only", True),
                date_posted=self.config.target_job.get("date_posted", "past_week"),
                start=start_offset,
            )

            console.print(
                f"[cyan]Navigating to search page {page_idx + 1}[/cyan] ({keyword} in {location})..."
            )
            self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
            human_delay(3.0, 5.0)

            # Check if user needs to log in
            if "/login" in self.page.url or "/checkpoint" in self.page.url:
                console.print(
                    "[bold red]Login required![/bold red] Please run `python cli.py login` first."
                )
                return []

            # Scroll through the jobs list to load lazy items
            self._scroll_job_list()

            # Extract job cards from the search result list
            job_cards = self.page.locator(
                "div.job-card-container, li.jobs-search-results__list-item"
            ).all()
            console.print(f"Found [green]{len(job_cards)}[/green] job cards on page {page_idx + 1}")

            for idx, card in enumerate(job_cards):
                try:
                    job_info = self._parse_job_card(card)
                    if not job_info or not job_info.get("id"):
                        continue

                    # Click the card to load job details in the side panel
                    try:
                        card.click(timeout=3000)
                        human_delay(1.5, 2.5)
                    except Exception:
                        pass

                    # Extract full details and hiring team / recruiter (LinkedIn Premium perk)
                    full_details = self._extract_job_details(job_info["id"])
                    job_info.update(full_details)

                    # Calculate PM Match Score
                    score, reasons = self._calculate_match_score(
                        job_info["title"], job_info.get("description", "")
                    )
                    job_info["match_score"] = score
                    job_info["match_reasons"] = reasons

                    # Save to database
                    save_job(
                        job_id=job_info["id"],
                        title=job_info["title"],
                        company=job_info["company"],
                        location=job_info["location"],
                        posted_time=job_info.get("posted_time", ""),
                        job_url=job_info["url"],
                        is_easy_apply=job_info.get("is_easy_apply", True),
                        description=job_info.get("description", ""),
                        match_score=score,
                        match_reasons=reasons,
                    )

                    # Save hiring manager lead if found
                    if job_info.get("hiring_manager"):
                        hm = job_info["hiring_manager"]
                        save_lead(
                            job_id=job_info["id"],
                            name=hm["name"],
                            headline=hm.get("headline", ""),
                            profile_url=hm["profile_url"],
                        )
                        console.print(
                            f"  [magenta][Premium Lead]:[/magenta] {hm['name']} ({hm.get('headline', 'Recruiter')})"
                        )

                    discovered_jobs.append(job_info)
                    console.print(
                        f"  [{idx+1}/{len(job_cards)}] [bold]{job_info['title']}[/bold] at [yellow]{job_info['company']}[/yellow] (Match: [green]{score}%[/green])"
                    )

                except Exception as e:
                    console.print(f"  [red]Error parsing job card:[/red] {e}")
                    continue

            human_delay(2.0, 4.0)

        return discovered_jobs

    def _scroll_job_list(self):
        """Scroll down the job results list pane to ensure all jobs load."""
        try:
            list_container = self.page.locator(".jobs-search-results-list").first
            if list_container.is_visible(timeout=3000):
                for _ in range(4):
                    list_container.evaluate("el => el.scrollTop += 600")
                    human_delay(0.5, 1.0)
            else:
                smooth_scroll(self.page, steps=4, distance=400)
        except Exception:
            smooth_scroll(self.page, steps=3, distance=400)

    def _parse_job_card(self, card) -> Optional[Dict[str, Any]]:
        # Extract Job ID
        job_id = None
        data_urn = card.get_attribute("data-job-id") or card.get_attribute("data-occludable-job-id")
        if data_urn:
            job_id = data_urn
        else:
            link_el = card.locator("a.job-card-list__title, a.job-card-container__link").first
            if link_el.count() > 0:
                href = link_el.get_attribute("href") or ""
                match = re.search(r"currentJobId=(\d+)", href) or re.search(r"/view/(\d+)", href)
                if match:
                    job_id = match.group(1)

        if not job_id:
            return None

        # Title
        title_el = card.locator(
            ".job-card-list__title, .artdeco-entity-lockup__title, .job-card-container__link"
        ).first
        title = title_el.inner_text().strip() if title_el.count() > 0 else "Unknown Title"
        title = title.split("\n")[0].strip()

        # Company
        comp_el = card.locator(
            ".job-card-container__primary-description, .artdeco-entity-lockup__subtitle"
        ).first
        company = comp_el.inner_text().strip() if comp_el.count() > 0 else "Unknown Company"
        company = company.split("\n")[0].strip()

        # Location
        loc_el = card.locator(
            ".job-card-container__metadata-item, .artdeco-entity-lockup__caption"
        ).first
        location = loc_el.inner_text().strip() if loc_el.count() > 0 else ""

        # Easy Apply check
        card_text = card.inner_text().lower()
        is_easy_apply = "easy apply" in card_text

        # Job URL
        job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"

        return {
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": job_url,
            "is_easy_apply": is_easy_apply,
        }

    def _extract_job_details(self, job_id: str) -> Dict[str, Any]:
        details: Dict[str, Any] = {"description": "", "hiring_manager": None}

        # Extract Job Description
        try:
            desc_el = self.page.locator(
                ".jobs-description__content, .jobs-description-content__text, #job-details"
            ).first
            if desc_el.is_visible(timeout=2000):
                details["description"] = desc_el.inner_text()
        except Exception:
            pass

        # Extract Hiring Team / Job Poster (LinkedIn Premium Feature)
        try:
            hirer_card = self.page.locator(
                ".hirer-card__hirer-information, div[data-view-name='job-details-hirer-card'], .jobs-poster"
            ).first
            if hirer_card.is_visible(timeout=2000):
                name_el = hirer_card.locator(
                    ".jobs-poster__name, .hirer-card__name, strong, a"
                ).first
                title_el = hirer_card.locator(".hirer-card__hirer-job-title, .jobs-poster__title").first
                link_el = hirer_card.locator("a[href*='/in/']").first

                name = name_el.inner_text().strip() if name_el.count() > 0 else ""
                headline = title_el.inner_text().strip() if title_el.count() > 0 else ""
                profile_href = link_el.get_attribute("href") if link_el.count() > 0 else ""

                if profile_href:
                    if profile_href.startswith("/"):
                        profile_href = "https://www.linkedin.com" + profile_href
                    profile_url = profile_href.split("?")[0]
                else:
                    profile_url = ""

                if name and profile_url:
                    details["hiring_manager"] = {
                        "name": name,
                        "headline": headline,
                        "profile_url": profile_url,
                    }
        except Exception:
            pass

        return details

    def _calculate_match_score(self, title: str, description: str) -> tuple[int, List[str]]:
        score = 40  # Base score for matching the search query
        reasons = []

        text = (title + " " + description).lower()

        # Check title specificity
        title_lower = title.lower()
        if "program manager" in title_lower or "technical program manager" in title_lower:
            score += 25
            reasons.append("Exact target title match")
        elif "project manager" in title_lower:
            score += 15
            reasons.append("Adjacent PM title match")

        # Check key skill keywords
        matches_found = []
        for kw in PM_KEYWORDS:
            if kw in text:
                matches_found.append(kw)

        if len(matches_found) >= 8:
            score += 25
            reasons.append(f"High skill overlap ({len(matches_found)} core PM keywords)")
        elif len(matches_found) >= 4:
            score += 15
            reasons.append(f"Moderate skill overlap ({len(matches_found)} PM keywords)")

        # Certifications bonus
        if "pmp" in text or "prince2" in text or "csm" in text:
            score += 10
            reasons.append("Recognized PM certification mentioned")

        score = min(score, 100)
        return score, reasons
