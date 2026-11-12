function Navbar({ cartCount, onOpenAssistant }) {
  return (
    <header className="navbar">
      <div className="brand-block">
        <span className="brand-mark">AI</span>
        <div>
          <p className="brand-name">AI Shop Assistant</p>
          <small>Smart shopping made simple</small>
        </div>
      </div>

      <div className="nav-actions">
        <button type="button" className="assistant-button" onClick={onOpenAssistant}>
          AI Assistant
        </button>
        <div className="cart-pill">Cart ({cartCount})</div>
      </div>
    </header>
  );
}

export default Navbar;
