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
    <form onSubmit={handleSubmit} className="search-bar">
      <input
        type="text"
        value={companyName}
        onChange={(e) => setCompanyName(e.target.value)}
        placeholder="Enter company name"
        disabled={loading}
      />
      <button type="submit" disabled={loading || !companyName.trim()}>
        {loading ? 'Searching...' : 'Search'}
      </button>
    </form>
  );
}

export default SearchBar;
