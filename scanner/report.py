from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def generate_html_report(results, outdir):
    env = Environment(loader=FileSystemLoader("scanner/templates"))
    template = env.get_template("report.html.j2")
    report = template.render(results=results)
    out_path = Path(outdir) / "report.html"
    with open(out_path, "w") as f:
        f.write(report)