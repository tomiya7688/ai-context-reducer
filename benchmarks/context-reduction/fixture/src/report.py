from dataclasses import dataclass

@dataclass
class Report:
    title: str
    lines: list[str]

def render_report(report: Report) -> str:
    body = "\n".join(report.lines)
    return f"# {report.title}\n\n{body}\n"
