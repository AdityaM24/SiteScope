function scoreColor(s) {
  if (s >= 80) return '#10b981'
  if (s >= 60) return '#f59e0b'
  if (s >= 40) return '#f97316'
  return '#ef4444'
}

export default function ScoreCard({ score }) {
  return (
    <div className="score-card">
      <div className="score-number" style={{ color: scoreColor(score) }}>
        {score}
      </div>
      <div className="score-label">AI Citation Readiness Score (out of 100)</div>
    </div>
  )
}
