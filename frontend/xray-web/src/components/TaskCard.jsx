// components/TaskCard.jsx
import './TaskCard.css';

function TaskCard({ taskName, taskData, weight }) {
  const getTaskRating = () => {
    if (!taskData || taskData.status !== 'success' || !taskData.data) {
      return null;
    }
    
    // Find rating property (case-insensitive)
    const ratingKey = Object.keys(taskData.data).find(
      k => k.toLowerCase() === 'rating'
    );
    
    return ratingKey ? taskData.data[ratingKey] : null;
  };
  
  const rating = getTaskRating();
  const ratingPercentage = rating !== null ? (rating / 5) * 100 : 0;
  
  const renderTaskContent = () => {
    if (!taskData || taskData.status !== 'success' || !taskData.data) {
      return <p className="no-data">No data available</p>;
    }

    switch (taskName) {
      case 'finance':
        return renderFinanceData(taskData.data);
      case 'news':
        return renderNewsData(taskData.data);
      case 'legal':
        return renderLegalData(taskData.data);
      case 'ambitionbox':
        return renderAmbitionBoxData(taskData.data);
      case 'reviews':
        return renderReviewsData(taskData.data);
      default:
        return <pre className="json-data">{JSON.stringify(taskData.data, null, 2)}</pre>;
    }
  };

  const renderFinanceData = (data) => {
    if (!data) return <p className="no-data">Financial data not available (Rate limited)</p>;
    return (
      <div className="finance-data">
        <pre className="json-data">{JSON.stringify(data, null, 2)}</pre>
      </div>
    );
  };

  const renderNewsData = (data) => {
    if (!data || !data.articles) return <p className="no-data">News data not available</p>;
    return (
      <div className="news-data">
        <ul className="news-list">
          {data.articles.slice(0, 3).map((article, index) => (
            <li key={index} className="news-item">
              <a href={article.link} target="_blank" rel="noopener noreferrer">
                {article.title}
              </a>
            </li>
          ))}
        </ul>
        {data.articles.length > 3 && (
          <p className="more-info">+ {data.articles.length - 3} more articles</p>
        )}
      </div>
    );
  };

  const renderLegalData = (data) => {
    if (!data) return <p className="no-data">Legal data not available</p>;
    return (
      <div className="legal-data">
        <p className="legal-link">
          <a href={data.url} target="_blank" rel="noopener noreferrer">
            View Legal Details
          </a>
        </p>
      </div>
    );
  };

  const renderAmbitionBoxData = (data) => {
    if (!data) return <p className="no-data">AmbitionBox data not available</p>;
    return (
      <div className="ambitionbox-data">
        <div className="review-count">
          <span className="count-number">{data["review count"]}</span>
          <span className="count-label">reviews</span>
        </div>
        <p className="ambitionbox-link">
          <a href={data.url} target="_blank" rel="noopener noreferrer">
            View on AmbitionBox
          </a>
        </p>
      </div>
    );
  };

  const renderReviewsData = (data) => {
    if (!data || !data.Reviews) return <p className="no-data">Review data not available</p>;
    return (
      <div className="reviews-data">
        <h3 className="reviews-title">{data.Title}</h3>
        <div className="reviews-list">
          {data.Reviews.slice(0, 2).map((review, index) => (
            <div key={index} className="review-item">
              <p>{review.substring(0, 120)}...</p>
            </div>
          ))}
        </div>
        {data.Reviews.length > 2 && (
          <p className="more-info">+ {data.Reviews.length - 2} more reviews</p>
        )}
      </div>
    );
  };

  return (
    <div className={`task-card ${taskData?.status || 'loading'}`}>
      <div className="task-header">
        <h2 className="task-title">
          {taskName.charAt(0).toUpperCase() + taskName.slice(1)}
          <span className="task-weight">{weight}%</span>
        </h2>
        <div className="task-status">
          {taskData?.status === 'success' ? (
            <span className="status-success">✓</span>
          ) : taskData?.status === 'error' ? (
            <span className="status-error">✗</span>
          ) : (
            <span className="status-loading"></span>
          )}
        </div>
      </div>
      
      {rating !== null && (
        <div className="rating-display">
          <div className="semicircle-mini">
            <svg viewBox="0 0 100 50">
              <path 
                className="semicircle-bg-mini" 
                d="M10,45 A35,35 0 0,1 90,45"
              />
              <path 
                className="semicircle-fill-mini" 
                d="M10,45 A35,35 0 0,1 90,45"
                style={{ 
                  strokeDasharray: `${ratingPercentage * 1.25}, 125` 
                }}
              />
              <text x="50" y="40" className="rating-text">
                {rating.toFixed(2)}
              </text>
            </svg>
          </div>
        </div>
      )}
      
      <div className="task-content">
        {taskData?.time_taken && (
          <div className="time-taken">
            Completed in {taskData.time_taken.toFixed(2)}s
          </div>
        )}
        {renderTaskContent()}
      </div>
    </div>
  );
}

export default TaskCard;
