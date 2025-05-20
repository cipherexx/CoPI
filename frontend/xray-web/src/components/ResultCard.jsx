// components/ResultCard.jsx
import './ResultCard.css';

function ResultCard({ averageScore, completedTasksCount, totalTasksCount, breakdown, imageUrl }) {
  const percentage = (completedTasksCount / totalTasksCount) * 100;

  return (
    <div className="result-card">
      <div className="result-header">
        <h2 className="result-title">Overall Rating</h2>
        <div className="completion-indicator">
          <span className="completion-text">
            {completedTasksCount} of {totalTasksCount} sources
          </span>
          <div className="completion-bar">
            <div 
              className="completion-progress" 
              style={{ width: `${percentage}%` }}
            ></div>
          </div>
        </div>
      </div>
      
      <div className="result-content">        
        <div className="main-score">
          <div className="semicircle-container">
            <div className="semicircle">
              <svg viewBox="0 0 200 100">
                <path 
                  className="semicircle-bg" 
                  d="M20,90 A70,70 0 0,1 180,90"
                />
                <path 
                  className="semicircle-fill" 
                  d="M20,90 A70,70 0 0,1 180,90"
                  style={{ 
                    strokeDasharray: `${(averageScore / 10) * 251}, 251` 
                  }}
                />
                <text x="100" y="85" className="score-text">
                  {averageScore.toFixed(2)}
                </text>
                <text x="100" y="50" className="score-label">
                  CoPI Score
                </text>
              </svg>
            </div>
          </div>
        </div>
        
        <div className="breakdown-section">
          <h3 className="breakdown-title">Score Breakdown</h3>
          <div className="breakdown-items">
            {breakdown.map(({ label, value, weight }) => (
              <div key={label} className="breakdown-item">
                <div className="breakdown-info">
                  <span className="breakdown-label">{label}</span>
                  <span className="breakdown-weight">{weight}%</span>
                </div>
                <div className="breakdown-bar-container">
                  <div className="breakdown-bar">
                    <div 
                      className="breakdown-progress" 
                      style={{ 
                        width: value !== null ? `${(value / 10) * 100}%` : '0%',
                        opacity: value !== null ? 1 : 0.3
                      }}
                    ></div>
                  </div>
                  <span className="breakdown-value">
                    {value !== null ? value.toFixed(2) : 'N/A'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultCard;
