import { useState, useEffect } from "react";
import { getProducts } from "../services/api";
import ProductCard from "../components/ProductCard";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Home() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");

  const categories = ["All", "Electronics", "Footwear", "Kitchen", "Outdoors"];

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (category && category !== "All") params.category = category;
      const res = await getProducts(params);
      setProducts(res.data.products);
    } catch {
      setError("Failed to load products.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [category]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchProducts();
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-10">
      {/* Hero */}
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">
          Shop Everything
        </h1>
        <p className="text-gray-500 text-lg">
          Find what you need, delivered to your door
        </p>
      </div>

      {/* Search bar */}
      <form
        onSubmit={handleSearch}
        className="flex gap-2 mb-6 max-w-xl mx-auto"
      >
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-field"
        />
        <button type="submit" className="btn-primary whitespace-nowrap">
          Search
        </button>
      </form>

      {/* Category filters */}
      <div className="flex gap-2 flex-wrap justify-center mb-10">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat === "All" ? "" : cat)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium
              transition-colors border
              ${
                (cat === "All" && !category) || category === cat
                  ? "bg-indigo-600 text-white border-indigo-600"
                  : "bg-white text-gray-600 border-gray-200 hover:border-indigo-300"
              }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Products grid */}
      {loading ? (
        <LoadingSpinner message="Loading products..." />
      ) : error ? (
        <div className="text-center py-20 text-red-500">{error}</div>
      ) : products.length === 0 ? (
        <div className="text-center py-20">
          <p className="text-gray-400 text-lg">No products found.</p>
          <button
            onClick={() => {
              setSearch("");
              setCategory("");
            }}
            className="btn-secondary mt-4 text-sm"
          >
            Clear filters
          </button>
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-400 mb-4">
            {products.length} product{products.length !== 1 ? "s" : ""} found
          </p>
          <div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3
                          xl:grid-cols-4 gap-6"
          >
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
