import os
import subprocess
from pathlib import Path

root = Path(r"C:\Users\zaire\fantasy_optimizer")
log_path = root / "run_project_output.txt"

with log_path.open("w", encoding="utf-8") as log:
    log.write(f"Working directory: {root}\n")
    log.write(f"Python executable: {root / '.venv' / 'Scripts' / 'python.exe'}\n")

    def run_cmd(cmd, description):
        log.write(f"\n=== {description} ===\n")
        log.write(f"Command: {' '.join(cmd)}\n")
        try:
            completed = subprocess.run(cmd, cwd=root, capture_output=True, text=True, encoding='utf-8', errors='replace')
            log.write(f"Return code: {completed.returncode}\n")
            log.write("--- stdout ---\n")
            log.write(completed.stdout + "\n")
            log.write("--- stderr ---\n")
            log.write(completed.stderr + "\n")
        except Exception as ex:
            log.write(f"Exception: {ex}\n")

    python_exe = str(root / ".venv" / "Scripts" / "python.exe")
    run_cmd([python_exe, "-m", "pip", "install", "-r", "requirements.txt"], "Install requirements")
    run_cmd([python_exe, "-m", "pytest", "-q"], "Run tests")
    run_cmd([python_exe, "-m", "src.fantasy_optimizer.cli", "--players", "players.csv", "--budget", "500"], "Run fantasy optimizer CLI")
    log.write("RUN_COMPLETE\n")
