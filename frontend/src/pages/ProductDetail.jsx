import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getProduct, addToCart } from "../services/api";
import { useAuth } from "../context/AuthContext";
import LoadingSpinner from "../components/LoadingSpinner";

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    getProduct(id)
      .then((res) => setProduct(res.data.product))
      .catch(() => navigate("/"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    setAdding(true);
    try {
      await addToCart(product.id, quantity);
      setMessage("Added to cart successfully!");
      setTimeout(() => setMessage(""), 3000);
    } catch (err) {
      setMessage(err.response?.data?.error || "Could not add to cart.");
    } finally {
      setAdding(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!product) return null;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-gray-500 hover:text-indigo-600
                         transition-colors mb-6 flex items-center gap-1"
      >
        ← Back
      </button>

      <div className="grid md:grid-cols-2 gap-10">
        {/* Image */}
        <div>
          <img
            src={
              product.image_url || "https://placehold.co/500x500?text=No+Image"
            }
            alt={product.name}
            className="w-full rounded-2xl object-cover bg-gray-100 shadow-sm"
          />
        </div>

        {/* Info */}
        <div className="flex flex-col gap-4">
          {product.category && (
            <span
              className="text-xs font-medium text-indigo-600 bg-indigo-50
                             px-2 py-0.5 rounded-full w-fit"
            >
              {product.category}
            </span>
          )}

          <h1 className="text-3xl font-bold text-gray-900">{product.name}</h1>

          <p className="text-gray-500 leading-relaxed">
            {product.description || "No description available."}
          </p>

          <div className="flex items-center gap-4 mt-2">
            <span className="text-3xl font-bold text-gray-900">
              ${product.price.toFixed(2)}
            </span>
            <span
              className={`text-sm font-medium px-3 py-1 rounded-full
              ${
                product.stock > 0
                  ? "text-green-700 bg-green-50"
                  : "text-red-600 bg-red-50"
              }`}
            >
              {product.stock > 0 ? `${product.stock} in stock` : "Out of stock"}
            </span>
          </div>

          {/* Quantity selector */}
          {product.stock > 0 && (
            <div className="flex items-center gap-3 mt-2">
              <label className="text-sm font-medium text-gray-700">Qty:</label>
              <div className="flex items-center border border-gray-300 rounded-lg">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-3 py-1.5 text-gray-600 hover:bg-gray-100
                             rounded-l-lg transition-colors font-bold"
                >
                  −
                </button>
                <span
                  className="px-4 py-1.5 text-sm font-medium border-x
                                 border-gray-300"
                >
                  {quantity}
                </span>
                <button
                  onClick={() =>
                    setQuantity(Math.min(product.stock, quantity + 1))
                  }
                  className="px-3 py-1.5 text-gray-600 hover:bg-gray-100
                             rounded-r-lg transition-colors font-bold"
                >
                  +
                </button>
              </div>
            </div>
          )}

          {/* Feedback message */}
          {message && (
            <div
              className={`text-sm px-4 py-2 rounded-lg
              ${
                message.includes("success")
                  ? "bg-green-50 text-green-700"
                  : "bg-red-50 text-red-700"
              }`}
            >
              {message}
            </div>
          )}

          <button
            onClick={handleAddToCart}
            disabled={adding || product.stock === 0}
            className="btn-primary mt-2 text-base py-3"
          >
            {adding ? "Adding..." : "Add to Cart"}
          </button>
        </div>
      </div>
    </div>
  );
}
