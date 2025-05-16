import './ResultCard.css';

function ResultCard({ averageScore, completedTasksCount, totalTasksCount }) {
  return (
    <div className="result-card">
      <h2>Overall Result</h2>
      <div className="score-display">
        <div className="score-value">{averageScore.toFixed(2)}</div>
        <div className="score-label">Average Score</div>
      </div>
      <div className="progress-display">
        <div className="progress-bar">
          <div 
            className="progress-filled" 
            style={{ width: `${(completedTasksCount / totalTasksCount) * 100}%` }}
          ></div>
        </div>
        <div className="progress-text">
          {completedTasksCount} of {totalTasksCount} tasks completed
        </div>
      </div>
    </div>
  );
}

export default ResultCard;
