// components/SearchBar.jsx
import { useState } from 'react';
import './SearchBar.css';

function SearchBar({ onSearch, loading }) {
  const [companyName, setCompanyName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (companyName.trim()) {
      onSearch(companyName.trim());
    }
  };

  return (
    <form className="search-container" onSubmit={handleSubmit}>
      <div className="search-bar">
        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="Enter company name..."
          disabled={loading}
          className="search-input"
        />
        <button 
          type="submit" 
          disabled={loading || !companyName.trim()} 
          className="search-button"
        >
          {loading ? (
            <span className="loader"></span>
          ) : (
            <span>Calculate</span>
          )}
        </button>
      </div>
    </form>
  );
}

export default SearchBar;
