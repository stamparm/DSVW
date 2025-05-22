import os
import requests

def batch_suggest_remediation(findings):
    api_key = os.getenv("OPENAI_API_KEY")
    # Make a prompt for all findings
    prompt = "Suggest secure fixes for the following security findings:\n\n"
    for idx, finding in enumerate(findings, 1):
        msg = finding.get("extra", {}).get("message") or finding.get("description", "No message")
        file_path = finding.get("path") or finding.get("file", "unknown file")
        line = finding.get("start", {}).get("line") or finding.get("line", "?")
        prompt += f"{idx}. [{file_path}:{line}] {msg}\n"
    prompt += "\nReturn your answers as a numbered list with specific fixes or recommendations for each finding."

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1200,  # Adjust if needed
    }
    r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=60)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    # Split the LLM response back to individual findings
    # This assumes the LLM returns a numbered list as requested
    ai_fixes = content.strip().split("\n")
    # Assign AI fix to each finding (if available)
    for idx, finding in enumerate(findings):
        if idx < len(ai_fixes):
            finding["ai_remediation"] = ai_fixes[idx]
        else:
            finding["ai_remediation"] = "N/A"
    return findings
