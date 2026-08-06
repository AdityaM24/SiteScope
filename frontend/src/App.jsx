import { useState } from 'react'
import ScoreCard from './components/ScoreCard'
import CategoryGrid from './components/CategoryGrid'
import IssueList from './components/IssueList'

// Default to relative path (works when backend serves the frontend, e.g. on Render).
// For a split deploy (frontend on Vercel, backend elsewhere), set VITE_API_URL to the backend origin,
// e.g. VITE_API_URL=https://geo-auditor.onrender.com/api/v1
const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

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
          {report.scopeNote && (
            <div className="scope-note">ℹ️ {report.scopeNote}</div>
          )}
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
  const esc = s => String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')

  const rows = report.categoryScores.map(cs => {
    const pct = cs.max_score ? Math.round(cs.score / cs.max_score * 100) : 0
    const color = pct >= 80 ? '#10b981' : pct >= 60 ? '#f59e0b' : pct >= 40 ? '#f97316' : '#ef4444'
    return `<tr><td>${esc(cs.category)}</td><td><div style="width:100px;height:8px;background:#334155;border-radius:4px"><div style="width:${pct}%;height:100%;background:${color};border-radius:4px"></div></div></td><td>${cs.score}/${cs.max_score}</td></tr>`
  }).join('')

  const issues = report.issues.map(iss => {
    const sc = iss.severity === 'High' ? '#ef4444' : iss.severity === 'Medium' ? '#f59e0b' : '#3b82f6'
    const explanation = iss.explanation ? `<div style="background:#1e3a5f33;border-left:3px solid #3b82f6;padding:.5rem .75rem;border-radius:0 6px 6px 0;margin:.5rem 0;font-size:.88rem;color:#bfdbfe">${esc(iss.explanation)}</div>` : ''
    const fixCode = iss.fixCode ? `<details style="margin-top:.5rem;border:1px solid #334155;border-radius:8px;overflow:hidden"><summary style="cursor:pointer;padding:.4rem .75rem;background:#1e293b;font-size:.82rem;font-weight:600;color:#60a5fa">📋 Copy-paste this fix</summary><pre style="margin:0;padding:.75rem;background:#0b1220;color:#a5f3fc;font-size:.78rem;overflow-x:auto"><code>${esc(iss.fixCode)}</code></pre></details>` : ''
    return `<div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:1rem;margin-bottom:.75rem"><div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.5rem"><span style="background:${sc}22;color:${sc};padding:2px 8px;border-radius:4px;font-size:.75rem;font-weight:700">${iss.severity}</span><strong>${esc(iss.title)}</strong><span style="margin-left:auto;font-size:.8rem;color:#10b981;white-space:nowrap">+${iss.estimatedScoreGain} pts · ${iss.effort} effort</span></div><div style="font-size:.85rem;color:#64748b;margin-bottom:.4rem"><code>${esc(iss.page)}</code></div><div style="font-size:.85rem;color:#94a3b8;margin-bottom:.4rem">${esc(iss.evidence)}</div><div style="font-size:.88rem;color:#cbd5e1;margin-bottom:.4rem">${esc(iss.recommendation)}</div>${explanation}${fixCode}</div>`
  }).join('') || '<p style="color:#94a3b8">No issues found!</p>'

  const scopeNote = report.scopeNote ? `<div style="background:#1e293b;border-left:3px solid #f59e0b;padding:.75rem 1rem;border-radius:0 8px 8px 0;margin-bottom:1rem;font-size:.85rem;color:#fde68a;line-height:1.5">ℹ️ ${esc(report.scopeNote)}</div>` : ''
  return `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>GEO Audit Report — ${esc(report.generatedAt?.slice(0,10) || '')}</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0f172a;color:#e2e8f0;max-width:900px;margin:0 auto;padding:2rem;line-height:1.6}h1{font-size:2rem;color:#38bdf8;margin-bottom:.5rem}h2{color:#38bdf8;border-bottom:1px solid #334155;padding-bottom:.5rem;margin:2rem 0 1rem;font-size:1.1rem}.score{font-size:4.5rem;font-weight:800;color:#38bdf8}.score-label{color:#94a3b8;font-size:.9rem}.summary{background:#1e293b;padding:1rem 1.25rem;border-radius:8px;border-left:4px solid #38bdf8;margin:1rem 0;font-size:.95rem}table{width:100%;border-collapse:collapse}th,td{padding:.75rem;text-align:left;border-bottom:1px solid #334155;font-size:.9rem}th{background:#1e293b;color:#94a3b8}code{background:#334155;padding:1px 4px;border-radius:3px;font-size:.82rem}footer{text-align:center;color:#475569;font-size:.8rem;padding:2rem 0}</style></head><body><h1>🔍 GEO Audit Report</h1><div class="score">${report.overallScore}/100</div><div class="score-label">Generated ${esc(report.generatedAt?.slice(0,10) || '')}</div>${scopeNote}<div class="summary">${esc(report.executiveSummary)}</div><h2>Category Breakdown</h2><table><tr><th>Category</th><th>Score</th><th>Points</th></tr>${rows}</table><h2>Issues (${report.issues.length})</h2>${issues}<footer>Generated by GEO Auditor — AI Citation Readiness Analyzer</footer></body></html>`
}
