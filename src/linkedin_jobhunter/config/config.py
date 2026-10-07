import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE_PATH = PACKAGE_DIR / "default_profile.yaml"


def get_base_dir() -> Path:
    """Returns the working directory or an environment-specified directory."""
    env_dir = os.getenv("LINKEDIN_HUNTER_DIR")
    if env_dir:
        return Path(env_dir).resolve()
    return Path.cwd()


def get_config_path() -> Path:
    # 1. Check current working directory config/profile.yaml
    cwd_cfg = get_base_dir() / "config" / "profile.yaml"
    if cwd_cfg.exists():
        return cwd_cfg
    # 2. Check profile.yaml in current working directory directly
    cwd_direct = get_base_dir() / "profile.yaml"
    if cwd_direct.exists():
        return cwd_direct
    # 3. Fallback to bundled template
    return DEFAULT_TEMPLATE_PATH


def get_data_dir() -> Path:
    d = get_base_dir() / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_resumes_dir() -> Path:
    d = get_base_dir() / "resumes"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_session_dir() -> Path:
    d = get_base_dir() / "session_data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def init_workspace():
    """Initializes user directories and copies default profile if not present."""
    base = get_base_dir()
    cfg_dir = base / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    target_cfg = cfg_dir / "profile.yaml"
    if not target_cfg.exists():
        shutil.copyfile(DEFAULT_TEMPLATE_PATH, target_cfg)
    get_data_dir()
    get_resumes_dir()
    get_session_dir()
    return target_cfg


def load_yaml_config(path: Optional[Path] = None) -> Dict[str, Any]:
    if path is None:
        path = get_config_path()
    if not path.exists():
        path = DEFAULT_TEMPLATE_PATH
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
        res_dir = get_resumes_dir()
        pdf_files = list(res_dir.glob("*.pdf"))
        if pdf_files:
            return pdf_files[0]
        docx_files = list(res_dir.glob("*.docx"))
        if docx_files:
            return docx_files[0]
        return None
