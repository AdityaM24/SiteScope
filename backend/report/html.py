"""
HTML report generator — creates a professional-looking HTML report.
"""
from __future__ import annotations

from ..models import AuditReport


def render_html(report: AuditReport) -> str:
    """Render the audit report as a self-contained HTML page."""

    score_color = _score_color(report.overallScore)

    category_rows = ""
    for cs in report.categoryScores:
        pct = int(cs.score / cs.max_score * 100) if cs.max_score else 0
        bar_color = _score_color(pct)
        category_rows += f"""
        <tr>
            <td>{cs.category}</td>
            <td><div class="score-bar"><div class="score-fill" style="width:{pct}%;background:{bar_color}"></div></div></td>
            <td>{cs.score}/{cs.max_score}</td>
        </tr>"""

    issue_rows = ""
    for issue in report.issues:
        sev_color = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#3b82f6"}.get(issue.severity, "#6b728e")
        explanation_html = (
            f'<div class="expl">{_html_escape(issue.explanation)}</div>'
            if issue.explanation else ""
        )
        fix_html = (
            f'<details class="fix"><summary>Copy-paste fix</summary><pre><code>{_html_escape(issue.fixCode)}</code></pre></details>'
            if issue.fixCode else ""
        )
        issue_rows += f"""
        <div class="issue">
            <div class="issue-top">
                <span class="severity" style="background:{sev_color}22;color:{sev_color}">{issue.severity}</span>
                <strong>{_html_escape(issue.title)}</strong>
                <span class="gain">+{issue.estimatedScoreGain} pts · {issue.effort} effort</span>
            </div>
            <div class="issue-page"><code>{_html_escape(issue.page)}</code></div>
            <div class="issue-evidence">{_html_escape(issue.evidence)}</div>
            <div class="issue-rec">{_html_escape(issue.recommendation)}</div>
            {explanation_html}
            {fix_html}
        </div>"""

    priority_rows = ""
    for p in report.priority[:10]:
        priority_rows += f"""
        <tr>
            <td>{p.priority:.1f}</td>
            <td>Issue #{p.issueId}</td>
            <td>+{int(p.impact)}</td>
            <td>{int(p.effort)}h</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GEO Audit Report — {report.generatedAt[:10]}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.6; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 2rem; }}
  header {{ background: linear-gradient(135deg, #1e3a5f, #0f172a); color: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; }}
  header h1 {{ font-size: 1.8rem; margin-bottom: 0.5rem; }}
  header .score {{ font-size: 3rem; font-weight: 700; }}
  header .score-label {{ font-size: 0.9rem; opacity: 0.8; }}
  .section {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  .section h2 {{ font-size: 1.2rem; margin-bottom: 1rem; color: #1e3a5f; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; }}
  .scope-note {{ background: #fefce8; border-left: 4px solid #f59e0b; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1rem; font-size: 0.88rem; color: #92400e; line-height: 1.5; }}
  .summary {{ background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 1rem; border-radius: 0 8px 8px 0; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }}
  th {{ background: #f1f5f9; font-weight: 600; color: #475569; }}
  .score-bar {{ width: 100px; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }}
  .score-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s; }}
  .severity {{ padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
  code {{ background: #f1f5f9; padding: 1px 4px; border-radius: 3px; font-size: 0.85rem; }}
  footer {{ text-align: center; color: #94a3b8; font-size: 0.8rem; padding: 2rem; }}
  .priority-score {{ font-weight: 700; color: #059669; }}
  .issue {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }}
  .issue-top {{ display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }}
  .issue-page {{ margin-bottom: 0.4rem; }}
  .issue-evidence {{ font-size: 0.85rem; color: #64748b; margin-bottom: 0.4rem; }}
  .issue-rec {{ font-size: 0.88rem; margin-bottom: 0.4rem; }}
  .gain {{ margin-left: auto; font-size: 0.8rem; color: #059669; white-space: nowrap; }}
  .expl {{ font-size: 0.88rem; background: #eff6ff; border-left: 3px solid #3b82f6; padding: 0.5rem 0.75rem; border-radius: 0 6px 6px 0; margin: 0.5rem 0; }}
  .fix {{ margin-top: 0.5rem; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; }}
  .fix summary {{ cursor: pointer; padding: 0.5rem 0.75rem; background: #f8fafc; font-size: 0.82rem; font-weight: 600; color: #1d4ed8; }}
  .fix pre {{ margin: 0; padding: 0.75rem; background: #0b1220; color: #a5f3fc; font-size: 0.78rem; overflow-x: auto; }}
  .fix pre code {{ background: transparent; color: inherit; padding: 0; }}
  @media print {{ body {{ background: white; }} .container {{ max-width: 100%; }} }}
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="score-label">AI Citation Readiness Score</div>
    <div class="score" style="color:{score_color}">{report.overallScore}/100</div>
    <div class="score-label">Generated {report.generatedAt[:10]}</div>
  </header>

  <div class="section">
    <h2>Executive Summary</h2>
    {f'<div class="scope-note">ℹ️ {_html_escape(report.scopeNote)}</div>' if report.scopeNote else ''}
    <div class="summary">{report.executiveSummary}</div>
  </div>

  <div class="section">
    <h2>Category Breakdown</h2>
    <table>
      <tr><th>Category</th><th>Score</th><th>Points</th></tr>
      {category_rows}
    </table>
  </div>

  <div class="section">
    <h2>Issues Found ({len(report.issues)})</h2>
    {issue_rows or '<p>No issues found — great job!</p>'}
  </div>

  <div class="section">
    <h2>Prioritized Fixes</h2>
    <table>
      <tr><th>Priority</th><th>Issue</th><th>Score Gain</th><th>Effort</th></tr>
      {priority_rows}
    </table>
  </div>

  <footer>
    Generated by GEO Auditor &mdash; AI Citation Readiness Analyzer
  </footer>
</div>
</body>
</html>"""


def _score_color(score: int) -> str:
    if score >= 80:
        return "#10b981"
    elif score >= 60:
        return "#f59e0b"
    elif score >= 40:
        return "#f97316"
    else:
        return "#ef4444"


def _html_escape(text: str) -> str:
    """Escape text for safe embedding in HTML (code blocks and prose)."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
