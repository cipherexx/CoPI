import { useState } from 'react';
import SearchBar from './components/SearchBar';
import DataDisplay from './components/DataDisplay';
import './App.css';

function App() {
  const [tasks, setTasks] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (companyName) => {
    setLoading(true);
    setTasks({});
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/api/company/${companyName}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      // Process each chunk from the stream
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        // Decode the chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });
        
        // Split buffer by newlines and process each complete line
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Last line might be incomplete
        
        for (const line of lines) {
          if (line.trim()) {
            try {
              const jsonData = JSON.parse(line);
              
              // Handle different types of events/tasks
              if (jsonData.event === 'start') {
                setTasks(prev => ({
                  ...prev,
                  tasksCount: jsonData.tasks_count || 5
                }));
              } else if (jsonData.event === 'end') {
                // End event received, all data has been streamed
                console.log('Data streaming completed');
              } else if (jsonData.task) {
                // Update the specific task data
                setTasks(prev => ({
                  ...prev,
                  [jsonData.task]: jsonData
                }));
              }
            } catch (e) {
              console.error('Error parsing JSON:', e, line);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to fetch data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>Project X-Ray</h1>
      <SearchBar onSearch={handleSearch} loading={loading} />
      {error && <div className="error-message">{error}</div>}
      <DataDisplay tasks={tasks} />
    </div>
  );
}

export default App;
