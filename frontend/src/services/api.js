import axios from "axios";

// ── Base URL points to your Flask backend ──
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ── Request interceptor: attach JWT token to every request ──
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ── Response interceptor: handle expired tokens globally ──
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

// ─────────────────────────────────────────
// AUTH
// ─────────────────────────────────────────
export const registerUser = (data) => api.post("/register", data);

export const loginUser = (data) => api.post("/login", data);

export const getMe = () => api.get("/me");

// ─────────────────────────────────────────
// PRODUCTS
// ─────────────────────────────────────────
export const getProducts = (params) => api.get("/products", { params });

export const getProduct = (id) => api.get(`/products/${id}`);

export const createProduct = (data) => api.post("/products", data);

export const updateProduct = (id, data) => api.patch(`/products/${id}`, data);

export const deleteProduct = (id) => api.delete(`/products/${id}`);

// ─────────────────────────────────────────
// CART
// ─────────────────────────────────────────
export const getCart = () => api.get("/cart");

export const addToCart = (product_id, quantity = 1) =>
  api.post("/cart/add", { product_id, quantity });

export const updateCartItem = (product_id, quantity) =>
  api.patch("/cart/update", { product_id, quantity });

export const removeFromCart = (product_id) =>
  api.delete("/cart/remove", { data: { product_id } });

export const clearCart = () => api.delete("/cart/clear");

// ─────────────────────────────────────────
// ORDERS
// ─────────────────────────────────────────
export const placeOrder = () => api.post("/orders");

export const getOrders = () => api.get("/orders");

export const getOrder = (id) => api.get(`/orders/${id}`);

export default api;
