import re
from typing import Dict, Any, Optional
from rich.console import Console
from playwright.sync_api import Locator

from linkedin_jobhunter.config.config import AppConfig

console = Console()


class ScreeningSolver:
    def __init__(self, config: AppConfig):
        self.config = config
        self.screening = config.screening

    def solve_radio_group(self, group_locator: Locator) -> bool:
        """
        Determines whether to select Yes or No (or True/False) for a radio button group.
        """
        try:
            # Get the question text from legend or label
            legend = group_locator.locator("legend, span.fb-dash-form-element__label").first
            question_text = legend.inner_text().lower() if legend.count() > 0 else ""
            if not question_text:
                question_text = group_locator.inner_text().lower()

            # Inspect available radio options
            options = group_locator.locator("label, input[type='radio']").all()

            # Determine intended answer based on rules
            intended_answer = self._determine_binary_answer(question_text)

            # Click the matching option
            for opt in options:
                opt_text = opt.inner_text().strip().lower()
                if intended_answer is True and opt_text in ["yes", "y", "true", "agree"]:
                    opt.click()
                    return True
                elif intended_answer is False and opt_text in ["no", "n", "false", "disagree"]:
                    opt.click()
                    return True

            # If no exact match found, default to Yes for positive questions, No for negative
            for opt in options:
                opt_text = opt.inner_text().strip().lower()
                if "yes" in opt_text:
                    opt.click()
                    return True

            return False
        except Exception as e:
            console.print(f"    [dim yellow]Error solving radio question: {e}[/dim yellow]")
            return False

    def solve_text_input(self, input_locator: Locator) -> bool:
        """
        Fills a numeric or single-line text input.
        """
        try:
            label_el = input_locator.locator(
                "xpath=preceding-sibling::label | xpath=ancestor::div[contains(@class, 'fb-dash-form-element')]//label"
            ).first
            question_text = label_el.inner_text().lower() if label_el.count() > 0 else ""
            if not question_text:
                question_text = input_locator.get_attribute("aria-label") or ""
            question_text = question_text.lower()

            answer = self._determine_text_answer(question_text)

            input_locator.fill("")
            input_locator.fill(str(answer))
            return True
        except Exception as e:
            console.print(f"    [dim yellow]Error solving text input: {e}[/dim yellow]")
            return False

    def solve_dropdown(self, select_locator: Locator) -> bool:
        """
        Selects the best matching option from a <select> dropdown.
        """
        try:
            label_el = select_locator.locator(
                "xpath=ancestor::div[contains(@class, 'fb-dash-form-element')]//label"
            ).first
            question_text = label_el.inner_text().lower() if label_el.count() > 0 else ""
            question_text = question_text or (select_locator.get_attribute("aria-label") or "").lower()

            # Get options in select
            options = select_locator.locator("option").all()
            opt_texts = [o.inner_text().strip() for o in options]

            chosen_value = self._determine_dropdown_option(question_text, opt_texts)
            if chosen_value:
                select_locator.select_option(label=chosen_value)
                return True
            elif len(opt_texts) > 1:
                # Default to second option (first option is often "Select an option")
                select_locator.select_option(index=1)
                return True
            return False
        except Exception as e:
            console.print(f"    [dim yellow]Error solving dropdown: {e}[/dim yellow]")
            return False

    def _determine_binary_answer(self, question: str) -> bool:
        """Rule engine for Yes/No questions."""
        q = question.lower()

        # Visa sponsorship
        if "sponsorship" in q or "require visa" in q or "require sponsorship" in q:
            return self.screening.get("requires_sponsorship", False)

        # Work authorization
        if "authorized to work" in q or "legal right" in q or "legally authorized" in q:
            return self.screening.get("legally_authorized_to_work", True)

        # Relocation / Commute
        if "relocate" in q or "relocation" in q:
            return self.screening.get("willing_to_relocate", True)
        if "commute" in q or "hybrid" in q:
            return True

        # Background check / Drug screen
        if "background check" in q or "drug" in q or "screening" in q:
            return True

        # Certifications
        if "pmp" in q:
            return self.screening.get("certifications", {}).get("pmp", True)
        if "scrum" in q or "csm" in q:
            return self.screening.get("certifications", {}).get("csm", True)

        # Driver's license
        if "driver" in q or "license" in q:
            return True

        # Default fallback for "Do you have experience with..."
        if "experience" in q or "comfortable" in q or "agree" in q:
            return True

        return True

    def _determine_text_answer(self, question: str) -> str:
        """Rule engine for text & numeric inputs."""
        q = question.lower()

        # Notice period
        if "notice period" in q or "notice" in q:
            if "day" in q:
                return str(self.screening.get("notice_period_days", 30))
            return self.screening.get("notice_period_string", "30 days")

        # CTC / Salary
        if "current ctc" in q or "current salary" in q or "current compensation" in q:
            return str(self.screening.get("current_ctc_in_lpa", "25"))
        if "expected ctc" in q or "expected salary" in q or "compensation expectation" in q:
            return str(self.screening.get("expected_ctc_in_lpa", "32"))

        # Years of experience with a specific skill
        if "how many years" in q or "years of experience" in q or "years" in q:
            # Check skill map
            skills_map = self.screening.get("skills_experience_years", {})
            for skill, yrs in skills_map.items():
                if skill in q:
                    return str(yrs)
            # Default for general experience
            return "6"

        # GPA
        if "gpa" in q or "grade" in q:
            return str(self.screening.get("gpa", "3.8"))

        # Phone
        if "phone" in q or "mobile" in q:
            return self.config.phone_number

        # Email
        if "email" in q:
            return self.config.email

        # LinkedIn Profile
        if "linkedin" in q:
            return self.config.personal.get("linkedin_url", "")

        # Default fallback for unknown numeric questions
        return "5"

    def _determine_dropdown_option(self, question: str, options: list[str]) -> Optional[str]:
        q = question.lower()

        # Notice period dropdown
        if "notice" in q:
            for opt in options:
                if "30" in opt or "1 month" in opt.lower():
                    return opt
            for opt in options:
                if "immediate" in opt.lower():
                    return opt

        # Proficiency
        if "proficiency" in q or "english" in q or "language" in q:
            for opt in options:
                if any(lvl in opt.lower() for lvl in ["fluent", "native", "professional", "advanced"]):
                    return opt

        # Education
        if "education" in q or "degree" in q:
            for opt in options:
                if "bachelor" in opt.lower() or "master" in opt.lower():
                    return opt

        # Yes / No dropdowns
        if "authorized" in q or "experience" in q:
            for opt in options:
                if opt.lower() in ["yes", "true"]:
                    return opt

        if "sponsorship" in q:
            for opt in options:
                if opt.lower() in ["no", "false"]:
                    return opt

        return None
