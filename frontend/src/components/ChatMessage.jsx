function ChatMessage({ message, products = [] }) {
  return (
    <div className={`chat-message ${message.role === 'user' ? 'user' : 'assistant'}`}>
      <p>{message.text}</p>
      {products.length > 0 && (
        <div className="chat-products">
          {products.map((product) => (
            <div key={product.id} className="mini-product-card">
              <strong>{product.name}</strong>
              <span>₹{product.price}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ChatMessage;
