import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "profile.yaml"
DATA_DIR = BASE_DIR / "data"
RESUMES_DIR = BASE_DIR / "resumes"
SESSION_DIR = BASE_DIR / "session_data"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RESUMES_DIR.mkdir(parents=True, exist_ok=True)
SESSION_DIR.mkdir(parents=True, exist_ok=True)


def load_yaml_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class AppConfig:
    def __init__(self, raw: Optional[Dict[str, Any]] = None):
        if raw is None:
            raw = load_yaml_config()
        self.raw = raw
        self.personal = raw.get("personal", {})
        self.target_job = raw.get("target_job", {})
        self.screening = raw.get("screening_answers", {})
        self.safety = raw.get("safety", {})
        self.outreach = raw.get("outreach", {})

    @property
    def full_name(self) -> str:
        return self.personal.get("full_name", "")

    @property
    def email(self) -> str:
        return self.personal.get("email", "")

    @property
    def phone_number(self) -> str:
        return self.personal.get("phone_number", "")

    @property
    def target_roles(self) -> List[str]:
        return self.target_job.get("roles", ["Program Manager"])

    @property
    def target_locations(self) -> List[str]:
        return self.target_job.get("locations", ["Bengaluru, India", "Remote"])

    @property
    def max_daily_apps(self) -> int:
        return self.safety.get("max_applications_per_day", 25)

    @property
    def manual_review_mode(self) -> bool:
        return self.safety.get("require_manual_review_before_submit", False)

    def get_skill_years(self, skill_name: str) -> Optional[int]:
        skill_clean = skill_name.lower().strip()
        skills_map = self.screening.get("skills_experience_years", {})
        for key, years in skills_map.items():
            if key in skill_clean or skill_clean in key:
                return int(years)
        return None

    def get_resume_path(self) -> Optional[Path]:
        pdf_files = list(RESUMES_DIR.glob("*.pdf"))
        if pdf_files:
            return pdf_files[0]
        docx_files = list(RESUMES_DIR.glob("*.docx"))
        if docx_files:
            return docx_files[0]
        return None
