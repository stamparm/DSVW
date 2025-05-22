import subprocess
import json
from pathlib import Path

def run_semgrep(repo_path):
    out_dir = Path("reports")
    out_dir.mkdir(exist_ok=True)
    output_file = out_dir / "semgrep.json"
    subprocess.run([
        "semgrep", "--config", "p/owasp-top-ten", "--json", "--output", str(output_file), repo_path
    ], check=True)
    with open(output_file) as f:
        results = json.load(f).get("results", [])
    return results