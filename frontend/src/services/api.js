const API_BASE_URL = import.meta.env.VITE_API_URL || '';

async function handleResponse(response) {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || 'Request failed');
  }
  return response.json();
}

export async function getProducts(params = {}) {
  const url = new URL(`${API_BASE_URL}/api/products`, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value);
    }
  });

  const response = await fetch(url);
  return handleResponse(response);
}

export async function getProduct(productId) {
  const response = await fetch(`${API_BASE_URL}/api/products/${productId}`);
  return handleResponse(response);
}

export async function getCart() {
  const response = await fetch(`${API_BASE_URL}/api/cart`);
  return handleResponse(response);
}

export async function addToCart(productId, quantity = 1) {
  const response = await fetch(`${API_BASE_URL}/api/cart`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId, quantity }),
  });
  return handleResponse(response);
}

export async function updateCartItem(itemId, quantity) {
  const response = await fetch(`${API_BASE_URL}/api/cart/${itemId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quantity }),
  });
  return handleResponse(response);
}

export async function removeCartItem(itemId) {
  const response = await fetch(`${API_BASE_URL}/api/cart/${itemId}`, {
    method: 'DELETE',
  });
  return handleResponse(response);
}

export async function chatWithAI(message) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  return handleResponse(response);
}

export async function createOrder(items) {
  const response = await fetch(`${API_BASE_URL}/api/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items }),
  });
  return handleResponse(response);
}
