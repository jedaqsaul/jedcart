import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  getCart,
  removeFromCart,
  updateCartItem,
  placeOrder,
} from "../services/api";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Cart() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [placing, setPlacing] = useState(false);
  const navigate = useNavigate();

  const fetchCart = async () => {
    try {
      const res = await getCart();
      setCart(res.data.cart);
    } catch {
      setCart(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const handleRemove = async (product_id) => {
    await removeFromCart(product_id);
    fetchCart();
  };

  const handleQuantityChange = async (product_id, qty) => {
    if (qty < 1) return;
    await updateCartItem(product_id, qty);
    fetchCart();
  };

  const handlePlaceOrder = async () => {
    if (!window.confirm("Place order for all items in your cart?")) return;
    setPlacing(true);
    try {
      await placeOrder();
      navigate("/orders");
    } catch (err) {
      alert(err.response?.data?.error || "Could not place order.");
    } finally {
      setPlacing(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading cart..." />;

  const isEmpty = !cart || cart.items.length === 0;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Your Cart</h1>

      {isEmpty ? (
        <div className="text-center py-20">
          <span className="text-6xl">🛒</span>
          <p className="text-gray-400 mt-4 mb-6">Your cart is empty.</p>
          <Link to="/" className="btn-primary">
            Browse Products
          </Link>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {/* Cart items */}
          {cart.items.map((item) => (
            <div key={item.id} className="card flex items-center gap-4">
              <img
                src={
                  item.product.image_url ||
                  "https://placehold.co/80x80?text=Item"
                }
                alt={item.product.name}
                className="w-20 h-20 object-cover rounded-lg bg-gray-100 flex-shrink-0"
              />

              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 truncate">
                  {item.product.name}
                </h3>
                <p className="text-sm text-gray-500">
                  ${item.product.price.toFixed(2)} each
                </p>

                {/* Quantity controls */}
                <div className="flex items-center gap-2 mt-2">
                  <button
                    onClick={() =>
                      handleQuantityChange(item.product.id, item.quantity - 1)
                    }
                    className="w-7 h-7 rounded-full border border-gray-300
                               flex items-center justify-center text-gray-600
                               hover:bg-gray-100 font-bold text-sm"
                  >
                    −
                  </button>
                  <span className="text-sm font-medium w-6 text-center">
                    {item.quantity}
                  </span>
                  <button
                    onClick={() =>
                      handleQuantityChange(item.product.id, item.quantity + 1)
                    }
                    className="w-7 h-7 rounded-full border border-gray-300
                               flex items-center justify-center text-gray-600
                               hover:bg-gray-100 font-bold text-sm"
                  >
                    +
                  </button>
                </div>
              </div>

              <div className="text-right flex-shrink-0">
                <p className="font-bold text-gray-900">
                  ${item.subtotal.toFixed(2)}
                </p>
                <button
                  onClick={() => handleRemove(item.product.id)}
                  className="text-xs text-red-500 hover:text-red-700
                             transition-colors mt-1"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}

          {/* Summary */}
          <div className="card mt-4 bg-gray-50">
            <div
              className="flex justify-between items-center text-lg
                            font-bold text-gray-900"
            >
              <span>Total</span>
              <span>${cart.total.toFixed(2)}</span>
            </div>
            <button
              onClick={handlePlaceOrder}
              disabled={placing}
              className="btn-primary w-full mt-4 py-3 text-base"
            >
              {placing ? "Placing Order..." : "Place Order →"}
            </button>
            <Link
              to="/"
              className="block text-center text-sm text-gray-500
                             hover:text-indigo-600 mt-3 transition-colors"
            >
              Continue shopping
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
