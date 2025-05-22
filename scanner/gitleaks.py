import subprocess
import json
from pathlib import Path

def run_gitleaks(repo_path):
    out_dir = Path("reports")
    out_dir.mkdir(exist_ok=True)
    output_file = out_dir / "gitleaks.json"
    try:
        print("Starting gitleaks subprocess...")
        subprocess.run([
            "gitleaks", "detect", "-s", repo_path, "--no-git", "--report-format", "json", "-r", str(output_file)
        ], check=True)
        print("Gitleaks subprocess finished.")
    except subprocess.CalledProcessError as e:
        print("Gitleaks found leaks (expected for vulnerable repos). Continuing...")

    print("Reading gitleaks output file...")
    with open(output_file) as f:
        try:
            results = json.load(f)
            print("Done loading JSON from gitleaks.")
            if isinstance(results, dict) and "leaks" in results:
                return results["leaks"]
            return results
        except Exception as ex:
            print(f"Error loading gitleaks output: {ex}")
            return []
