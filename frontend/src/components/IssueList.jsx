import { useState } from 'react'

function FixCodeBlock({ code }) {
  const [copied, setCopied] = useState(false)

  async function copy() {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      // clipboard blocked (http, old browser) — fall back to selecting
      const el = document.getElementById('fix-code')
      if (el) {
        const range = document.createRange()
        range.selectNodeContents(el)
        const sel = window.getSelection()
        sel.removeAllRanges()
        sel.addRange(range)
      }
    }
  }

  return (
    <div className="fix-block">
      <div className="fix-header">
        <span>📋 Copy-paste this fix</span>
        <button type="button" className="copy-btn" onClick={copy}>
          {copied ? '✓ Copied' : 'Copy'}
        </button>
      </div>
      <pre id="fix-code" className="fix-code"><code>{code}</code></pre>
    </div>
  )
}

export default function IssueList({ issues }) {
  if (!issues || issues.length === 0) {
    return <div className="summary">✅ No issues found — great job!</div>
  }

  return (
    <div>
      {issues.map(iss => (
        <div key={iss.id} className="issue">
          <div className="issue-header">
            <span className="issue-title">{iss.title}</span>
            <span className={`severity severity-${iss.severity}`}>
              {iss.severity}
            </span>
          </div>

          {iss.explanation && (
            <div className="issue-explanation">💡 {iss.explanation}</div>
          )}

          <div className="issue-evidence">{iss.evidence}</div>
          <div className="issue-rec">✅ {iss.recommendation}</div>

          {iss.fixCode && <FixCodeBlock code={iss.fixCode} />}

          <div className="issue-meta">
            <span>🎯 +{iss.estimatedScoreGain} pts</span>
            <span>⏱️ Effort: {iss.effort}</span>
            {iss.page && <span>📄 {iss.page}</span>}
          </div>
        </div>
      ))}
    </div>
  )
}
