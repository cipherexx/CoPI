// components/DataDisplay.jsx
import { useState, useEffect } from 'react';
import TaskCard from './TaskCard';
import ResultCard from './ResultCard';
import './DataDisplay.css';

function DataDisplay({ tasks }) {
  const WEIGHTS = {
    finance: 35,
    legal: 10,
    news: 20,
    reviews: 25,
    ambitionbox: 10,
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
  
  // Count completed tasks and total tasks
  const completedTasksCount = Object.values(tasks)
    .filter(task => task.status === 'success' || task.status === 'error').length;
  const totalTasksCount = tasks.tasksCount || 5; // Default to 5 if not specified
  
  return (
    <div className="data-display">
      {Object.keys(tasks).length > 0 && (
        <ResultCard 
          averageScore={averageScore} 
          completedTasksCount={completedTasksCount} 
          totalTasksCount={totalTasksCount}
          breakdown={breakdown}
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
