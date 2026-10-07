import os
from typing import Dict, Any, Optional
from rich.console import Console

from linkedin_jobhunter.database.models import get_db_connection, get_leads
from linkedin_jobhunter.config.config import AppConfig

console = Console()


class InMailDrafter:
    def __init__(self, config: AppConfig):
        self.config = config
        self.api_key = os.getenv("GEMINI_API_KEY")

    def generate_pitch(
        self,
        recruiter_name: str,
        job_title: str,
        company: str,
        job_description: str = "",
    ) -> Dict[str, str]:
        """
        Drafts a high-converting, personalized 3-part outreach pitch for LinkedIn InMail.
        """
        first_name = recruiter_name.split()[0] if recruiter_name else "there"
        applicant_name = self.config.full_name
        tagline = self.config.outreach.get(
            "sender_tagline", "Program Manager | Agile & Cross-Functional Delivery"
        )
        strengths = self.config.outreach.get(
            "core_strengths",
            [
                "Led end-to-end delivery of high-impact engineering programs across distributed teams",
                "Championed Agile best practices, streamlining release cycle times by 30%",
                "Managed executive stakeholder alignment and risk mitigation",
            ],
        )

        subject = f"{job_title} Application | {applicant_name}"

        body = (
            f"Hi {first_name},\n\n"
            f"I hope you're having a productive week! I recently submitted my application for the "
            f"{job_title} role at {company} and wanted to personally reach out.\n\n"
            f"With over 6+ years of experience leading complex, cross-functional programs, I specialize in:\n"
            f"• {strengths[0]}\n"
            f"• {strengths[1]}\n"
            f"• {strengths[2]}\n\n"
            f"Given {company}'s ongoing growth and initiatives, I would love to connect for a quick 10-minute "
            f"conversation to share how my background aligns with your team's goals.\n\n"
            f"Best regards,\n"
            f"{applicant_name}\n"
            f"{tagline}\n"
            f"LinkedIn: {self.config.personal.get('linkedin_url', '')}"
        )

        return {"subject": subject, "body": body}

    def draft_all_pending_leads(self):
        """Generates drafts for all discovered leads that lack an InMail draft."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT l.id, l.name, l.headline, j.title, j.company, j.description
                FROM leads l
                JOIN jobs j ON l.job_id = j.id
                WHERE l.inmail_message IS NULL OR l.inmail_message = ''
                """
            )
            rows = cursor.fetchall()
            if not rows:
                console.print("[dim]No pending leads requiring InMail drafts.[/dim]")
                return

            console.print(f"[cyan]Drafting personalized InMails for {len(rows)} leads...[/cyan]")
            for row in rows:
                lead_id, name, headline, title, company, desc = row
                pitch = self.generate_pitch(
                    recruiter_name=name,
                    job_title=title,
                    company=company,
                    job_description=desc or "",
                )

                cursor.execute(
                    """
                    UPDATE leads
                    SET inmail_subject = ?, inmail_message = ?
                    WHERE id = ?
                    """,
                    (pitch["subject"], pitch["body"], lead_id),
                )
                console.print(f"  [green][+] Drafted InMail for:[/green] {name} ({company})")

            conn.commit()
        finally:
            conn.close()
