function Cart({ items, total, onIncrease, onDecrease, onRemove, onCheckout, checkingOut, orderMessage }) {
  return (
    <aside className="cart-panel">
      <h2>Shopping Cart</h2>
      {items.length === 0 ? (
        <p className="empty-state">Your cart is empty.</p>
      ) : (
        <div className="cart-items">
          {items.map((item) => (
            <div key={item.id} className="cart-item">
              <div>
                <strong>{item.product_name}</strong>
                <p>₹{item.product_price}</p>
              </div>
              <div className="cart-controls">
                <button type="button" onClick={() => onDecrease(item)}>-</button>
                <span>{item.quantity}</span>
                <button type="button" onClick={() => onIncrease(item)}>+</button>
                <button type="button" className="remove-button" onClick={() => onRemove(item.id)}>
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      <div className="cart-total">
        <span>Total</span>
        <strong>₹{total}</strong>
      </div>
      <button
        type="button"
        className="checkout-button"
        disabled={!items.length || checkingOut}
        onClick={onCheckout}
      >
        {checkingOut ? 'Processing...' : 'Checkout (demo)'}
      </button>
      {orderMessage && <p className="order-message" role="status">{orderMessage}</p>}
    </aside>
  );
}

export default Cart;
