import { useState } from 'react'
import ScoreCard from './components/ScoreCard'
import CategoryGrid from './components/CategoryGrid'
import IssueList from './components/IssueList'

const API_BASE = '/api/v1'

export default function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [report, setReport] = useState(null)

  async function handleAudit(e) {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError('')
    setReport(null)

    try {
      const res = await fetch(`${API_BASE}/audit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      })
      const data = await res.json()

      if (!res.ok || !data.success) {
        throw new Error(data.detail || data.message || 'Audit failed')
      }
      setReport(data.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function downloadJSON() {
    if (!report) return
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `geo-audit-${new URL(url).hostname}-${Date.now()}.json`
    a.click()
  }

  function downloadHTML() {
    if (!report) return
    const html = buildHTMLReport(report)
    const blob = new Blob([html], { type: 'text/html' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `geo-audit-${new URL(url).hostname}-${Date.now()}.html`
    a.click()
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🔍 GEO Auditor</h1>
        <p>Check if your website is ready for AI search</p>
      </header>

      <form onSubmit={handleAudit} className="input-area">
        <input
          type="url"
          placeholder="Enter website URL (e.g. https://example.com)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={loading}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Auditing...' : 'Audit'}
        </button>
      </form>

      {error && <div className="error">⚠️ {error}</div>}

      {loading && (
        <div className="loading">
          <div className="spinner" />
          <p>Crawling, checking, scoring...</p>
        </div>
      )}

      {report && (
        <>
          <ScoreCard score={report.overallScore} />
          <CategoryGrid categories={report.categoryScores} />
          <div className="summary">{report.executiveSummary}</div>
          <h2 className="section-title">
            Issues ({report.issues.length})
          </h2>
          <IssueList issues={report.issues} />
          <div className="export-bar">
            <button className="export-btn" onClick={downloadJSON}>
              📥 Export JSON
            </button>
            <button className="export-btn" onClick={downloadHTML}>
              📄 Export HTML
            </button>
          </div>
        </>
      )}

      <footer className="footer">
        Powered by GEO Auditor — AI Citation Readiness Analyzer
      </footer>
    </div>
  )
}

function buildHTMLReport(report) {
  const rows = report.categoryScores.map(cs => {
    const pct = cs.max_score ? Math.round(cs.score / cs.max_score * 100) : 0
    const color = pct >= 80 ? '#10b981' : pct >= 60 ? '#f59e0b' : pct >= 40 ? '#f97316' : '#ef4444'
    return `<tr><td>${cs.category}</td><td><div style="width:100px;height:8px;background:#e2e8f0;border-radius:4px"><div style="width:${pct}%;height:100%;background:${color};border-radius:4px"></div></div></td><td>${cs.score}/${cs.max_score}</td></tr>`
  }).join('')

  const issues = report.issues.map(iss => {
    const sc = iss.severity === 'High' ? '#ef4444' : iss.severity === 'Medium' ? '#f59e0b' : '#3b82f6'
    return `<tr><td><span style="background:${sc}22;color:${sc};padding:2px 8px;border-radius:4px;font-size:0.75rem">${iss.severity}</span></td><td><strong>${iss.title}</strong></td><td><code>${iss.page}</code></td><td>${iss.evidence?.substring(0, 120) || ''}</td><td>${iss.recommendation?.substring(0, 200) || ''}</td><td>+${iss.estimatedScoreGain}</td><td>${iss.effort}</td></tr>`
  }).join('') || '<tr><td colspan="7">No issues found!</td></tr>'

  return `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>GEO Audit Report</title><style>body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0f172a;color:#e2e8f0;max-width:900px;margin:0 auto;padding:2rem}h1{color:#38bdf8}h2{color:#38bdf8;border-bottom:1px solid #334155;padding-bottom:0.5rem;margin:2rem 0 1rem}.score{font-size:5rem;font-weight:800;color:#38bdf8}.summary{background:#1e293b;padding:1rem;border-radius:8px;border-left:4px solid #38bdf8;margin:1rem 0}table{width:100%;border-collapse:collapse}th,td{padding:0.75rem;text-align:left;border-bottom:1px solid #334155;font-size:0.9rem}th{background:#1e293b;color:#94a3b8}</style></head><body><h1>GEO Audit Report</h1><div class="score">${report.overallScore}/100</div><div class="summary">${report.executiveSummary}</div><h2>Categories</h2><table><tr><th>Category</th><th>Score</th><th>Points</th></tr>${rows}</table><h2>Issues (${report.issues.length})</h2><table><tr><th>Severity</th><th>Issue</th><th>Page</th><th>Evidence</th><th>Recommendation</th><th>Gain</th><th>Effort</th></tr>${issues}</table><p style="color:#475569;margin-top:2rem">Generated ${report.generatedAt}</p></body></html>`
}
