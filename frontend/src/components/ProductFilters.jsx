function ProductFilters({ filters, onFilterChange, onApply, onReset }) {
  return (
    <div className="filter-panel">
      <select
        value={filters.category}
        onChange={(event) => onFilterChange('category', event.target.value)}
      >
        <option value="">All categories</option>
        <option value="Laptops">Laptops</option>
        <option value="Mobile Phones">Mobile Phones</option>
        <option value="Audio">Audio</option>
        <option value="Accessories">Accessories</option>
        <option value="Fashion">Fashion</option>
      </select>

      <input
        type="number"
        placeholder="Min price"
        value={filters.min_price}
        onChange={(event) => onFilterChange('min_price', event.target.value)}
      />

      <input
        type="number"
        placeholder="Max price"
        value={filters.max_price}
        onChange={(event) => onFilterChange('max_price', event.target.value)}
      />

      <input
        type="number"
        step="0.1"
        min="0"
        max="5"
        placeholder="Min rating"
        value={filters.min_rating}
        onChange={(event) => onFilterChange('min_rating', event.target.value)}
      />

      <button type="button" onClick={onApply}>Apply</button>
      <button type="button" className="secondary" onClick={onReset}>Reset</button>
    </div>
  );
}

export default ProductFilters;
