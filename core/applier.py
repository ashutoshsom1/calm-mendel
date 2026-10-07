import time
from typing import Optional, Dict, Any
from playwright.sync_api import Page, Locator
from rich.console import Console

from core.browser import human_delay, human_type
from core.solver import ScreeningSolver
from database.models import update_job_status, get_daily_applied_count
from config.config import AppConfig

console = Console()


class EasyApplyBot:
    def __init__(self, page: Page, config: AppConfig):
        self.page = page
        self.config = config
        self.solver = ScreeningSolver(config)

    def apply_to_job(self, job: Dict[str, Any]) -> bool:
        job_id = job["id"]
        job_url = job.get("job_url") or f"https://www.linkedin.com/jobs/view/{job_id}/"

        # Check daily application cap
        applied_today = get_daily_applied_count()
        if applied_today >= self.config.max_daily_apps:
            console.print(
                f"[bold yellow][!] Daily safety limit reached ({applied_today}/{self.config.max_daily_apps} applied today).[/bold yellow]"
            )
            console.print("Stopping to protect your LinkedIn Premium account standing.")
            return False

        console.print(
            f"\n[cyan]Targeting:[/cyan] [bold]{job['title']}[/bold] at [yellow]{job['company']}[/yellow]"
        )
        console.print(f"URL: {job_url}")

        try:
            self.page.goto(job_url, wait_until="domcontentloaded", timeout=60000)
            human_delay(2.5, 4.0)

            # Check if already applied
            if self._is_already_applied():
                console.print("[dim green]Already applied to this role. Marking as APPLIED.[/dim green]")
                update_job_status(job_id, "APPLIED", notes="Previously applied")
                return True

            # Find the Easy Apply button
            apply_btn = self._find_easy_apply_button()
            if not apply_btn:
                console.print("[dim yellow]No Easy Apply button found (Direct external application).[/dim yellow]")
                update_job_status(job_id, "SKIPPED", notes="External application")
                return False

            # Click Easy Apply
            console.print("[green]Clicking 'Easy Apply'...[/green]")
            apply_btn.click()
            human_delay(2.0, 3.5)

            # Handle application modal
            success = self._handle_modal(job_id)
            if success:
                console.print(
                    f"[bold green][+] Successfully applied to {job['title']} at {job['company']}![/bold green]"
                )
                update_job_status(job_id, "APPLIED")
                return True
            else:
                console.print(f"[yellow]Application incomplete or skipped for {job['title']}.[/yellow]")
                return False

        except Exception as e:
            console.print(f"[red]Error during application process:[/red] {e}")
            self._dismiss_modal_if_open()
            return False

    def _is_already_applied(self) -> bool:
        applied_indicators = self.page.locator(
            ".jobs-s-apply__applied-date, .artdeco-inline-feedback--success, span:has-text('Applied')"
        )
        return applied_indicators.count() > 0 and applied_indicators.first.is_visible()

    def _find_easy_apply_button(self) -> Optional[Locator]:
        selectors = [
            "button.jobs-apply-button",
            "button[aria-label*='Easy Apply']",
            "button:has-text('Easy Apply')",
        ]
        for sel in selectors:
            loc = self.page.locator(sel).first
            if loc.is_visible(timeout=3000):
                return loc
        return None

    def _handle_modal(self, job_id: str) -> bool:
        modal = self.page.locator("div[role='dialog'], .jobs-easy-apply-modal").first
        if not modal.is_visible(timeout=5000):
            return False

        max_steps = 10
        step = 0

        while step < max_steps:
            step += 1
            human_delay(1.5, 2.5)

            # Solve any form elements on this step
            self._fill_step_inputs(modal)

            # Check if there's a resume upload required
            self._handle_resume_selection(modal)

            # Check footer action buttons
            next_btn = modal.locator("button[aria-label*='Continue to next step'], button:has-text('Next')").first
            review_btn = modal.locator("button[aria-label*='Review your application'], button:has-text('Review')").first
            submit_btn = modal.locator("button[aria-label*='Submit application'], button:has-text('Submit application')").first

            if submit_btn.is_visible(timeout=1000):
                console.print("  [cyan]Reached Final Submission Screen.[/cyan]")
                if self.config.manual_review_mode:
                    console.print(
                        "[bold yellow]⏸ Manual Review Mode active:[/bold yellow] Inspect the browser window. Press [green]Enter[/green] in console to submit, or [red]'s'[/red] to skip..."
                    )
                    choice = input()
                    if choice.strip().lower() == "s":
                        self._dismiss_modal_if_open()
                        return False

                submit_btn.click()
                human_delay(3.0, 5.0)
                self._dismiss_modal_if_open()
                return True

            elif review_btn.is_visible(timeout=1000):
                console.print("  [dim]Clicking Review...[/dim]")
                review_btn.click()

            elif next_btn.is_visible(timeout=1000):
                console.print("  [dim]Clicking Next step...[/dim]")
                next_btn.click()

            else:
                # If no forward button, check if submission completed
                done_btn = self.page.locator("button:has-text('Done'), button[aria-label*='Dismiss']").first
                if done_btn.is_visible(timeout=2000):
                    done_btn.click()
                    return True
                break

        # If we exited the loop without submitting, safely dismiss
        self._dismiss_modal_if_open()
        return False

    def _fill_step_inputs(self, modal: Locator):
        # 1. Radio groups
        fieldset_locators = modal.locator("fieldset").all()
        for fieldset in fieldset_locators:
            try:
                self.solver.solve_radio_group(fieldset)
            except Exception:
                pass

        # 2. Dropdowns (<select>)
        select_locators = modal.locator("select").all()
        for sel in select_locators:
            try:
                self.solver.solve_dropdown(sel)
            except Exception:
                pass

        # 3. Text & Numeric Inputs
        input_locators = modal.locator("input[type='text'], input[type='number']").all()
        for inp in input_locators:
            try:
                if not inp.input_value():
                    self.solver.solve_text_input(inp)
            except Exception:
                pass

    def _handle_resume_selection(self, modal: Locator):
        # Check if user needs to select or upload a resume
        resume_cards = modal.locator(".jobs-document-upload__card, .ui-attachment").all()
        if resume_cards:
            # Select the most recent resume card if available
            try:
                first_card = resume_cards[0]
                first_card.click()
            except Exception:
                pass

        # Check file upload input if file upload is empty
        file_input = modal.locator("input[type='file']").first
        if file_input.count() > 0:
            resume_path = self.config.get_resume_path()
            if resume_path and resume_path.exists():
                try:
                    file_input.set_input_files(str(resume_path))
                    console.print(f"  [green]Uploaded resume:[/green] {resume_path.name}")
                    human_delay(2.0, 3.0)
                except Exception as e:
                    console.print(f"  [dim yellow]File upload notice: {e}[/dim yellow]")

    def _dismiss_modal_if_open(self):
        try:
            dismiss_btn = self.page.locator("button[aria-label*='Dismiss'], button[data-test-modal-close-btn]").first
            if dismiss_btn.is_visible(timeout=2000):
                dismiss_btn.click()
                human_delay(1.0, 1.5)
                # Handle discard confirmation dialog if prompted
                discard_btn = self.page.locator("button[data-control-name='discard_application_confirm_btn'], button:has-text('Discard')").first
                if discard_btn.is_visible(timeout=2000):
                    discard_btn.click()
        except Exception:
            pass
