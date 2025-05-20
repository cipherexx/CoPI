import { useState, useEffect } from 'react';
import TaskCard from './TaskCard';
import ResultCard from './ResultCard';
import './DataDisplay.css';

function DataDisplay({ tasks }) {
  // Define which tasks should be used for scoring
  const WEIGHTS = {
    finance: 35,
    legal: 10,
    news: 20,
    reviews: 25,
    ambitionbox: 10,
  };
  
  // Extract image URL from the new task (assuming the task name is "image")
  const getImageUrl = () => {
    const imageTask = tasks.image;
    return imageTask && imageTask.status === 'success' && imageTask.data ? 
      imageTask.data.url || null : null;
  };
  
  const calculateWeightedScore = () => {
    let totalWeight = 0;
    let weightedSum = 0;
    const breakdown = [];
    
    Object.entries(WEIGHTS).forEach(([key, weight]) => {
      const task = tasks[key];
      let value = null;
      
      if (task && task.status === 'success' && task.data) {
        // Find rating property (case-insensitive)
        const ratingKey = Object.keys(task.data).find(
          k => k.toLowerCase() === 'rating'
        );
        value = ratingKey ? task.data[ratingKey] : null;
        
        if (typeof value === 'number') {
          weightedSum += value * weight;
          totalWeight += weight;
        }
      }
      
      breakdown.push({ 
        label: key.charAt(0).toUpperCase() + key.slice(1), 
        value, 
        weight 
      });
    });
    
    const averageScore = totalWeight > 0 ? weightedSum / totalWeight : 0;
    return { averageScore, breakdown };
  };
  
  const { averageScore, breakdown } = calculateWeightedScore();
  const imageUrl = getImageUrl();
  
  // Count completed metric tasks (excluding the image task)
  const completedMetricTasks = Object.keys(tasks)
    .filter(key => Object.keys(WEIGHTS).includes(key) && 
           (tasks[key].status === 'success' || tasks[key].status === 'error'))
    .length;
  
  // Total number of metric tasks (should be 5)
  const totalMetricTasks = Object.keys(WEIGHTS).length;
  
  return (
    <div className="data-display">
      {Object.keys(tasks).length > 0 && (
        <ResultCard 
          averageScore={averageScore} 
          completedTasksCount={completedMetricTasks} 
          totalTasksCount={totalMetricTasks}
          breakdown={breakdown}
          imageUrl={imageUrl}
        />
      )}
      
      <div className="task-cards">
        {Object.entries(tasks).map(([taskName, taskData]) => {
          if (taskName !== 'tasksCount') {
            return (
              <TaskCard 
                key={taskName} 
                taskName={taskName} 
                taskData={taskData} 
                weight={WEIGHTS[taskName] || 0}
              />
            );
          }
          return null;
        })}
      </div>
    </div>
  );
}

export default DataDisplay;