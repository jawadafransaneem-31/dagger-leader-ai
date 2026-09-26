from __future__ import annotations
import subprocess
from config.settings import get_settings


def run_dbt(args: list[str] | None = None) -> str:
    s = get_settings()
    cmd = ["dbt"] + (args or ["run"])
    return subprocess.check_output(cmd, cwd=s.dbt_project_dir, text=True)
