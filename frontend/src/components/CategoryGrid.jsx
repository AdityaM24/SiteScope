function barColor(score, max) {
  const pct = max ? (score / max) * 100 : 0
  if (pct >= 80) return '#10b981'
  if (pct >= 60) return '#f59e0b'
  if (pct >= 40) return '#f97316'
  return '#ef4444'
}

export default function CategoryGrid({ categories }) {
  return (
    <div className="categories">
      {categories.map(cs => (
        <div key={cs.category} className="cat-card">
          <h3>{cs.category}</h3>
          <div className="cat-bar">
            <div
              className="cat-fill"
              style={{
                width: cs.max_score ? `${(cs.score / cs.max_score) * 100}%` : '0%',
                background: barColor(cs.score, cs.max_score),
              }}
            />
          </div>
          <div className="cat-score">
            {cs.score} / {cs.max_score}
          </div>
        </div>
      ))}
    </div>
  )
}
