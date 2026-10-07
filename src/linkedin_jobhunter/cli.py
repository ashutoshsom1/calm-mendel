import sys
import argparse
import csv
from pathlib import Path

# Ensure UTF-8 output encoding on Windows PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from linkedin_jobhunter.config.config import (
    AppConfig,
    init_workspace,
    get_config_path,
    get_data_dir,
    get_resumes_dir,
)
from linkedin_jobhunter.database.models import (
    init_db,
    get_jobs,
    get_leads,
    get_statistics,
    get_daily_applied_count,
    update_job_status,
)
from linkedin_jobhunter.core.browser import get_browser, human_delay
from linkedin_jobhunter.core.searcher import JobSearcher
from linkedin_jobhunter.core.applier import EasyApplyBot
from linkedin_jobhunter.core.inmail_drafter import InMailDrafter

console = Console()


def cmd_init(args):
    """Initializes the database and prints configuration status."""
    cfg_file = init_workspace()
    init_db()
    cfg = AppConfig()
    console.print(
        Panel.fit(
            f"[bold green]LinkedIn Full-Funnel Job Hunter Initialized[/bold green]\n\n"
            f"[cyan]Candidate:[/cyan] {cfg.full_name} ({cfg.email})\n"
            f"[cyan]Target Roles:[/cyan] {', '.join(cfg.target_roles)}\n"
            f"[cyan]Target Locations:[/cyan] {', '.join(cfg.target_locations)}\n"
            f"[cyan]Daily Safety Limit:[/cyan] {cfg.max_daily_apps} applications/day\n"
            f"[cyan]Config File:[/cyan] {cfg_file}\n"
            f"[cyan]Database Location:[/cyan] {get_data_dir() / 'jobs.db'}",
            title="System Ready",
            border_style="green",
        )
    )

    resume_path = cfg.get_resume_path()
    res_dir = get_resumes_dir()
    if resume_path:
        console.print(f"[green][+] Resume detected:[/green] {resume_path.name}")
    else:
        console.print(
            f"[yellow][!] No resume found in '{res_dir}' folder.[/yellow]\n"
            f"Please place your Program Manager resume (PDF or DOCX) in the `resumes/` folder."
        )


def cmd_login(args):
    """Launches Chrome to log in to LinkedIn and save persistent session."""
    init_db()
    console.print(
        "[bold cyan]Launching Google Chrome for LinkedIn Login...[/bold cyan]\n"
        "[dim]Log into your LinkedIn Premium account. Once you see your feed, you can close the browser or press Enter here.[/dim]"
    )

    with get_browser(headless=False) as context:
        page = context.new_page()
        page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")

        console.print(
            "\n[bold yellow]Please complete login and any 2FA/verification in the opened Chrome window.[/bold yellow]"
        )
        input("Press [ENTER] in this terminal once you are logged in and see your LinkedIn homepage: ")

        # Verify login state
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        human_delay(2.0, 3.0)

        if "feed" in page.url or "mynetwork" in page.url:
            console.print("[bold green][+] Successfully logged in and session saved![/bold green]")
            console.print("Your session will now persist for automated searches and applications.")
        else:
            console.print(
                "[yellow]Warning: Could not confirm feed URL. Please verify your login if searches fail.[/yellow]"
            )


def cmd_search(args):
    """Discovers matching jobs and hiring team members."""
    init_db()
    cfg = AppConfig()

    keyword = args.keyword or cfg.target_roles[0]
    location = args.location or cfg.target_locations[0]
    pages = args.pages or 2

    console.print(
        f"[bold cyan]Searching for:[/bold cyan] '{keyword}' in '{location}' ({pages} pages)..."
    )

    with get_browser(headless=args.headless) as context:
        page = context.new_page()
        searcher = JobSearcher(page, cfg)
        discovered = searcher.search_jobs(keyword=keyword, location=location, pages=pages)

        # Draft InMail pitches for newly discovered hiring leads
        drafter = InMailDrafter(cfg)
        drafter.draft_all_pending_leads()

    stats = get_statistics()
    console.print(
        f"\n[bold green]Search completed![/bold green] Found {len(discovered)} jobs. Total in DB: {stats['total_discovered']} ({stats['total_easy_apply']} Easy Apply)."
    )


def cmd_apply(args):
    """Executes safe Easy Apply on discovered matching jobs."""
    init_db()
    cfg = AppConfig()

    # Override manual review mode if requested
    if args.review:
        cfg.safety["require_manual_review_before_submit"] = True

    applied_today = get_daily_applied_count()
    if applied_today >= cfg.max_daily_apps:
        console.print(
            f"[bold yellow][!] Daily safety limit already reached ({applied_today}/{cfg.max_daily_apps}).[/bold yellow]\n"
            "To prevent LinkedIn rate limits, wait until tomorrow or adjust max_applications_per_day in config/profile.yaml."
        )
        return

    # Fetch candidate jobs
    jobs = get_jobs(status="DISCOVERED", limit=args.limit or 20)
    eligible_jobs = [j for j in jobs if j.get("is_easy_apply")]

    # Filter by minimum match score
    min_score = args.min_score or 50
    eligible_jobs = [j for j in eligible_jobs if j.get("match_score", 0) >= min_score]

    if not eligible_jobs:
        console.print(
            f"[yellow]No unapplied Easy Apply jobs found matching minimum score {min_score}%.[/yellow]\n"
            "Run `linkedin-jobhunter search` to find new listings!"
        )
        return

    console.print(
        f"[bold cyan]Starting application runner for {len(eligible_jobs)} matching jobs...[/bold cyan]"
    )

    with get_browser(headless=args.headless) as context:
        page = context.new_page()
        bot = EasyApplyBot(page, cfg)

        applied_count = 0
        for job in eligible_jobs:
            success = bot.apply_to_job(job)
            if success:
                applied_count += 1
                human_delay(15.0, 30.0)  # Human delay between distinct job submissions
            else:
                human_delay(5.0, 10.0)

            if get_daily_applied_count() >= cfg.max_daily_apps:
                break

    console.print(
        f"\n[bold green]Run finished.[/bold green] Applied to {applied_count} jobs in this session."
    )


def cmd_leads(args):
    """Displays discovered recruiters, hiring managers, and drafted InMails."""
    init_db()
    leads = get_leads(limit=args.limit or 20)

    if not leads:
        console.print("[dim]No hiring leads captured yet. Run `linkedin-jobhunter search` first.[/dim]")
        return

    table = Table(title="LinkedIn Premium Hiring Team Leads & Outreach")
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Hiring Manager / Recruiter", style="bold white")
    table.add_column("Role & Company", style="yellow")
    table.add_column("LinkedIn Profile", style="blue")
    table.add_column("Status", style="green")

    for l in leads:
        table.add_row(
            str(l["id"]),
            f"{l['name']}\n[dim]{l.get('headline', '')}[/dim]",
            f"{l.get('job_title', '')}\nat {l.get('job_company', '')}",
            l["profile_url"],
            l["status"],
        )

    console.print(table)

    if args.view_draft:
        # Show specific lead's InMail pitch
        target = next((l for l in leads if str(l["id"]) == str(args.view_draft)), None)
        if target and target.get("inmail_message"):
            console.print(
                Panel.fit(
                    f"[bold cyan]Subject:[/bold cyan] {target.get('inmail_subject', '')}\n\n"
                    f"{target['inmail_message']}",
                    title=f"InMail Draft for {target['name']}",
                    border_style="magenta",
                )
            )


def cmd_status(args):
    """Displays pipeline status and metrics."""
    init_db()
    stats = get_statistics()

    table = Table(title="Job Search & Application Pipeline Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold green")

    table.add_row("Total Discovered Jobs", str(stats["total_discovered"]))
    table.add_row("Easy Apply Jobs Available", str(stats["total_easy_apply"]))
    table.add_row("Total Applications Submitted", str(stats["total_applied"]))
    table.add_row("Applied Today", str(stats["applied_today"]))
    table.add_row("Hiring Manager Leads Captured", str(stats["total_leads"]))

    console.print(table)


def cmd_export(args):
    """Exports all jobs and leads to a CSV file."""
    init_db()
    jobs = get_jobs(limit=1000)
    export_path = get_data_dir() / "job_applications.csv"

    if not jobs:
        console.print("[yellow]No jobs in database to export.[/yellow]")
        return

    keys = ["id", "title", "company", "location", "match_score", "status", "applied_at", "job_url"]
    with open(export_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(jobs)

    console.print(f"[bold green][+] Successfully exported {len(jobs)} jobs to:[/bold green] {export_path}")


def main():
    parser = argparse.ArgumentParser(
        prog="linkedin-jobhunter",
        description="LinkedIn Premium Full-Funnel Job Hunter for Program Managers",
    )
    subparsers = parser.add_subparsers(dest="command")

    # init
    subparsers.add_parser("init", help="Initialize database and verify configuration")

    # login
    subparsers.add_parser("login", help="Launch Chrome to log into LinkedIn & save session")

    # search
    search_p = subparsers.add_parser("search", help="Search jobs and scrape hiring leads")
    search_p.add_argument("--keyword", "-k", help="Job keyword (e.g. 'Program Manager')")
    search_p.add_argument("--location", "-l", help="Target location")
    search_p.add_argument("--pages", "-p", type=int, default=2, help="Number of pages to scan")
    search_p.add_argument("--headless", action="store_true", help="Run browser in headless mode")

    # apply
    apply_p = subparsers.add_parser("apply", help="Run automated Easy Apply on eligible jobs")
    apply_p.add_argument("--limit", type=int, default=15, help="Max jobs to process this run")
    apply_p.add_argument("--min-score", type=int, default=50, help="Minimum match score (0-100)")
    apply_p.add_argument("--review", action="store_true", help="Pause for manual review before submit")
    apply_p.add_argument("--headless", action="store_true", help="Run browser in headless mode")

    # leads
    leads_p = subparsers.add_parser("leads", help="View hiring managers and InMail drafts")
    leads_p.add_argument("--limit", type=int, default=20, help="Max leads to display")
    leads_p.add_argument("--view-draft", type=int, help="Show draft message for specific Lead ID")

    # status
    subparsers.add_parser("status", help="View current pipeline statistics")

    # export
    subparsers.add_parser("export", help="Export jobs to CSV")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "init": cmd_init,
        "login": cmd_login,
        "search": cmd_search,
        "apply": cmd_apply,
        "leads": cmd_leads,
        "status": cmd_status,
        "export": cmd_export,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
