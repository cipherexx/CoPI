import TaskCard from './TaskCard';
import ResultCard from './ResultCard';
import './DataDisplay.css';

function DataDisplay({ tasks }) {
  // Calculate average score from all tasks with a rating
  // const calculateAverageScore = () => {
  //   const scores = Object.values(tasks)
  //     .filter(task => task.status === 'success' && task.data && task.data.rating !== undefined)
  //     .map(task => task.data.rating);
    
  //   if (scores.length === 0) return 0;
    
  //   const sum = scores.reduce((acc, score) => acc + score, 0);
  //   return sum / scores.length;
  // };
  // Updated calculateAverageScore function in DataDisplay.jsx
const calculateAverageScore = () => {
  const scores = Object.values(tasks)
    .filter(task => task.status === 'success' && task.data)
    .map(task => {
      // Handle different rating property names (case-insensitive)
      const ratingKey = Object.keys(task.data).find(key => 
        key.toLowerCase() === 'rating'
      );
      return ratingKey ? task.data[ratingKey] : undefined;
    })
    .filter(score => typeof score === 'number');

  if (scores.length === 0) return 0;
  
  const sum = scores.reduce((acc, score) => acc + score, 0);
  return sum / scores.length;
};


  const averageScore = calculateAverageScore();
  
  // Count completed tasks and total tasks
  const completedTasksCount = Object.values(tasks)
    .filter(task => task.status === 'success' || task.status === 'error').length;
  
  const totalTasksCount = tasks.tasksCount || 5; // Default to 5 if not specified

  return (
    <div className="data-display">
      <ResultCard 
        averageScore={averageScore} 
        completedTasksCount={completedTasksCount}
        totalTasksCount={totalTasksCount} 
      />
      
      <div className="task-cards">
        {Object.entries(tasks).map(([taskName, taskData]) => (
          taskName !== 'tasksCount' ? (
            <TaskCard key={taskName} taskName={taskName} taskData={taskData} />
          ) : null
        ))}
      </div>
    </div>
  );
}

export default DataDisplay;
