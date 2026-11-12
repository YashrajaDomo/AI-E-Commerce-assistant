import { Link } from 'react-router-dom';

function ProductCard({ product, onAddToCart }) {
  return (
    <article className="product-card">
      <img src={product.image_url} alt={product.name} />
      <div className="product-body">
        <div className="product-header">
          <span className="badge">{product.category}</span>
          <span className="rating">⭐ {product.rating}</span>
        </div>
        <h3>{product.name}</h3>
        <p>{product.description}</p>
        <div className="product-meta">
          <strong>₹{product.price}</strong>
          <span>Stock: {product.stock}</span>
        </div>
        <div className="product-actions">
          <Link to={`/product/${product.id}`} className="link-button">
            View Details
          </Link>
          <button type="button" onClick={() => onAddToCart(product.id)}>
            Add to Cart
          </button>
        </div>
      </div>
    </article>
  );
}

export default ProductCard;
