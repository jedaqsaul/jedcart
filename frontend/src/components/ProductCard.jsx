import { Link } from "react-router-dom";
import { addToCart } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useState } from "react";

export default function ProductCard({ product, onCartUpdate }) {
  const { isAuthenticated } = useAuth();
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      window.location.href = "/login";
      return;
    }
    setAdding(true);
    try {
      await addToCart(product.id, 1);
      setAdded(true);
      onCartUpdate?.();
      setTimeout(() => setAdded(false), 2000);
    } catch (err) {
      alert(err.response?.data?.error || "Could not add to cart");
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="card flex flex-col hover:shadow-md transition-shadow">
      {/* Product image */}
      <Link to={`/products/${product.id}`}>
        <img
          src={
            product.image_url || "https://placehold.co/300x300?text=No+Image"
          }
          alt={product.name}
          className="w-full h-48 object-cover rounded-lg mb-4 bg-gray-100"
        />
      </Link>

      {/* Category badge */}
      {product.category && (
        <span
          className="text-xs font-medium text-indigo-600 bg-indigo-50
                         px-2 py-0.5 rounded-full w-fit mb-2"
        >
          {product.category}
        </span>
      )}

      {/* Name + description */}
      <Link to={`/products/${product.id}`}>
        <h3
          className="font-semibold text-gray-900 hover:text-indigo-600
                       transition-colors leading-tight mb-1"
        >
          {product.name}
        </h3>
      </Link>
      <p className="text-sm text-gray-500 line-clamp-2 mb-4 flex-1">
        {product.description || "No description available."}
      </p>

      {/* Price + stock */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-xl font-bold text-gray-900">
          ${product.price.toFixed(2)}
        </span>
        <span
          className={`text-xs font-medium px-2 py-0.5 rounded-full
          ${
            product.stock > 0
              ? "text-green-700 bg-green-50"
              : "text-red-600 bg-red-50"
          }`}
        >
          {product.stock > 0 ? `${product.stock} in stock` : "Out of stock"}
        </span>
      </div>

      {/* Add to cart button */}
      <button
        onClick={handleAddToCart}
        disabled={adding || product.stock === 0}
        className="btn-primary w-full text-sm"
      >
        {adding ? "Adding..." : added ? "✓ Added!" : "Add to Cart"}
      </button>
    </div>
  );
}
