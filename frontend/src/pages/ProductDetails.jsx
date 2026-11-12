import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getProduct } from '../services/api';

function ProductDetails({ onAddToCart }) {
  const { id } = useParams();
  const [product, setProduct] = useState(null);

  useEffect(() => {
    const loadProduct = async () => {
      const data = await getProduct(id);
      setProduct(data);
    };

    loadProduct();
  }, [id]);

  if (!product) {
    return <div className="page-shell"><p>Loading product...</p></div>;
  }

  return (
    <main className="page-shell product-details">
      <Link to="/" className="back-link">← Back to products</Link>
      <div className="detail-layout">
        <img src={product.image_url} alt={product.name} />
        <div className="detail-content">
          <span className="badge">{product.category}</span>
          <h1>{product.name}</h1>
          <p className="rating-line">⭐ {product.rating} rating</p>
          <p className="detail-description">{product.description}</p>
          <div className="detail-meta">
            <strong>₹{product.price}</strong>
            <span>Stock: {product.stock}</span>
          </div>
          <button type="button" onClick={() => onAddToCart(product.id)}>
            Add to Cart
          </button>
        </div>
      </div>
    </main>
  );
}

export default ProductDetails;
