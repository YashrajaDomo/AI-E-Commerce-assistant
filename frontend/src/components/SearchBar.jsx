function SearchBar({ value, onChange, onSearch }) {
  return (
    <div className="search-bar-wrapper">
      <input
        type="text"
        placeholder="Search for products..."
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter') {
            onSearch();
          }
        }}
      />
      <button type="button" onClick={onSearch}>
        Search
      </button>
    </div>
  );
}

export default SearchBar;
