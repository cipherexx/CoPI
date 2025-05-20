import { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import DataDisplay from './components/DataDisplay';
import ThemeToggle from './components/ThemeToggle';
import './theme.css';
import './App.css';

function App() {
  const [tasks, setTasks] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState('dark');
  
  useEffect(() => {
    document.body.className = `theme-${theme}`;
  }, [theme]);
  
  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const handleSearch = async (companyName) => {
    setLoading(true);
    setTasks({});
    setError(null);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/company/${companyName}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.trim()) {
            try {
              const jsonData = JSON.parse(line);
              if (jsonData.event === 'start') {
                setTasks(prev => ({ ...prev, tasksCount: jsonData.tasks_count || 5 }));
              } else if (jsonData.event === 'end') {
                console.log('Data streaming completed');
              } else if (jsonData.task) {
                setTasks(prev => ({ ...prev, [jsonData.task]: jsonData }));
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
      <header className="header">
        <div className="logo-container">
          <h1 className="logo">
            C<span className="gold-letter">o</span>PI
          </h1>
          <p className="tagline">Company Perception Index</p>
        </div>
        <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
      </header>
      
      <SearchBar onSearch={handleSearch} loading={loading} />
      
      {error && (
        <div className="error-message">
          <span className="error-icon">!</span>
          <span>{error}</span>
        </div>
      )}
      
      <DataDisplay tasks={tasks} />
    </div>
  );
}

export default App;
