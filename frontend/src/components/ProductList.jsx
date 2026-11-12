import ProductCard from './ProductCard';

function ProductList({ products, onAddToCart }) {
  if (!products.length) {
    return <p className="empty-state">No products matched your search.</p>;
  }

  return (
    <div className="product-grid">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} onAddToCart={onAddToCart} />
      ))}
    </div>
  );
}

export default ProductList;
