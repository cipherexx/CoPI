import './TaskCard.css';

function TaskCard({ taskName, taskData }) {
  const renderTaskContent = () => {
    if (!taskData || taskData.status !== 'success' || !taskData.data) {
      return <p>No data available</p>;
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
        return <pre>{JSON.stringify(taskData.data, null, 2)}</pre>;
    }
  };

  const renderFinanceData = (data) => {
    if (!data) return <p>Financial data not available (Rate limited)</p>;
    return (
      <div className="finance-data">
        <h3>Financial Data</h3>
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    );
  };

  const renderNewsData = (data) => {
    if (!data || !data.articles) return <p>News data not available</p>;
    return (
      <div className="news-data">
        <h3>News (Rating: {data.rating.toFixed(2)})</h3>
        <ul>
          {data.articles.slice(0, 25).map((article, index) => (
            <li key={index}>
              <a href={article.link} target="_blank" rel="noopener noreferrer">
                {article.title}
              </a>
            </li>
          ))}
        </ul>
        {data.articles.length > 5 && <p>+ {data.articles.length - 25} more articles</p>}
      </div>
    );
  };

  const renderLegalData = (data) => {
    if (!data) return <p>Legal data not available</p>;
    return (
      <div className="legal-data">
        <h3>Legal Information</h3>
        <p>Rating: {data.rating.toFixed(2)}</p>
        <p><a href={data.url} target="_blank" rel="noopener noreferrer">View Legal Details</a></p>
      </div>
    );
  };

  const renderAmbitionBoxData = (data) => {
    if (!data) return <p>AmbitionBox data not available</p>;
    return (
      <div className="ambitionbox-data">
        <h3>AmbitionBox Ratings</h3>
        <p>Rating: {data.rating} (from {data["review count"]} reviews)</p>
        <p><a href={data.url} target="_blank" rel="noopener noreferrer">View on AmbitionBox</a></p>
      </div>
    );
  };

  const renderReviewsData = (data) => {
    if (!data || !data.Reviews) return <p>Review data not available</p>;
    return (
      <div className="reviews-data">
        <h3>{data.Title} (Rating: {data.Rating.toFixed(2)})</h3>
        <div className="reviews-list">
          {data.Reviews.slice(0, 3).map((review, index) => (
            <div key={index} className="review-item">
              <p>{review.substring(0, 150)}...</p>
            </div>
          ))}
        </div>
        {data.Reviews.length > 3 && <p>+ {data.Reviews.length - 3} more reviews</p>}
      </div>
    );
  };

  return (
    <div className="task-card">
      <h2>{taskName.charAt(0).toUpperCase() + taskName.slice(1)}</h2>
      <div className="task-status">
        Status: <span className={`status-${taskData.status}`}>{taskData.status}</span>
        {taskData.time_taken && <span> (took {taskData.time_taken.toFixed(2)}s)</span>}
      </div>
      <div className="task-content">
        {renderTaskContent()}
      </div>
    </div>
  );
}

export default TaskCard;
