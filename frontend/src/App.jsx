import { useEffect, useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import Cart from './components/Cart';
import ChatBot from './components/ChatBot';
import Home from './pages/Home';
import ProductDetails from './pages/ProductDetails';
import { addToCart, getCart, getProducts, removeCartItem, updateCartItem, chatWithAI } from './services/api';

const defaultFilters = {
  category: '',
  min_price: '',
  max_price: '',
  min_rating: '',
};

function App() {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState(defaultFilters);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      text: 'Hi! Ask me for a good laptop, headphones, or a product recommendation.',
      products: [],
    },
  ]);

  const fetchCart = async () => {
    const data = await getCart();
    setCart(data);
  };

  const fetchProducts = async (nextSearch = searchTerm, nextFilters = filters) => {
    const params = {
      q: nextSearch || undefined,
      category: nextFilters.category || undefined,
      min_price: nextFilters.min_price || undefined,
      max_price: nextFilters.max_price || undefined,
      min_rating: nextFilters.min_rating || undefined,
    };

    const data = await getProducts(params);
    setProducts(data);
  };

  useEffect(() => {
    fetchProducts();
    fetchCart();
  }, []);

  const handleAddToCart = async (productId) => {
    await addToCart(productId, 1);
    await fetchCart();
  };

  const handleIncrease = async (item) => {
    await updateCartItem(item.id, item.quantity + 1);
    await fetchCart();
  };

  const handleDecrease = async (item) => {
    const nextQuantity = item.quantity - 1;
    if (nextQuantity <= 0) {
      await removeCartItem(item.id);
    } else {
      await updateCartItem(item.id, nextQuantity);
    }
    await fetchCart();
  };

  const handleRemove = async (itemId) => {
    await removeCartItem(itemId);
    await fetchCart();
  };

  const handleSearch = async () => {
    await fetchProducts(searchTerm, filters);
  };

  const handleApplyFilters = async () => {
    await fetchProducts(searchTerm, filters);
  };

  const handleResetFilters = async () => {
    setFilters(defaultFilters);
    await fetchProducts(searchTerm, defaultFilters);
  };

  const handleChatSubmit = async (message) => {
    setChatMessages((previous) => [...previous, { role: 'user', text: message, products: [] }]);

    const response = await chatWithAI(message);
    setChatMessages((previous) => [
      ...previous,
      { role: 'assistant', text: response.message, products: response.products || [] },
    ]);

    await fetchCart();
  };

  return (
    <BrowserRouter>
      <div className="app-shell">
        <Navbar
          cartCount={cart.items.reduce((sum, item) => sum + item.quantity, 0)}
          onOpenAssistant={() => setChatOpen(true)}
        />

        <div className="content-shell">
          <Routes>
            <Route
              path="/"
              element={
                <Home
                  products={products}
                  searchTerm={searchTerm}
                  onSearchTermChange={setSearchTerm}
                  onSearch={handleSearch}
                  filters={filters}
                  onFilterChange={(key, value) => setFilters((previous) => ({ ...previous, [key]: value }))}
                  onApplyFilters={handleApplyFilters}
                  onResetFilters={handleResetFilters}
                  onAddToCart={handleAddToCart}
                />
              }
            />
            <Route path="/product/:id" element={<ProductDetails onAddToCart={handleAddToCart} />} />
          </Routes>

          <Cart
            items={cart.items}
            total={cart.total}
            onIncrease={handleIncrease}
            onDecrease={handleDecrease}
            onRemove={handleRemove}
          />
        </div>

        <ChatBot
          isOpen={chatOpen}
          onClose={() => setChatOpen(false)}
          messages={chatMessages}
          onSend={handleChatSubmit}
        />
      </div>
    </BrowserRouter>
  );
}

export default App;
