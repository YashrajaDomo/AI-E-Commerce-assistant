import ProductFilters from '../components/ProductFilters';
import ProductList from '../components/ProductList';
import SearchBar from '../components/SearchBar';

function Home({
  products,
  searchTerm,
  onSearchTermChange,
  onSearch,
  filters,
  onFilterChange,
  onApplyFilters,
  onResetFilters,
  onAddToCart,
}) {
  return (
    <main className="page-shell">
      <section className="hero-banner">
        <div>
          <p className="eyebrow">AI powered shopping</p>
          <h1>Find the right product faster</h1>
        </div>
      </section>

      <div className="content-layout">
        <section className="catalog-area">
          <SearchBar value={searchTerm} onChange={onSearchTermChange} onSearch={onSearch} />
          <ProductFilters
            filters={filters}
            onFilterChange={onFilterChange}
            onApply={onApplyFilters}
            onReset={onResetFilters}
          />
          <ProductList products={products} onAddToCart={onAddToCart} />
        </section>
      </div>
    </main>
  );
}

export default Home;
