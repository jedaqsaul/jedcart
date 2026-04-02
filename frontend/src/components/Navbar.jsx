import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useState, useEffect } from "react";
import { getCart } from "../services/api";

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [cartCount, setCartCount] = useState(0);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      getCart()
        .then((res) => setCartCount(res.data.cart.items.length))
        .catch(() => {});
    } else {
      setCartCount(0);
    }
  }, [isAuthenticated]);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl">🛒</span>
            <span className="text-xl font-bold text-indigo-600">JedCart</span>
          </Link>

          {/* Desktop nav links */}
          <div className="hidden sm:flex items-center gap-6">
            <Link
              to="/"
              className="text-sm text-gray-600 hover:text-indigo-600
                                    transition-colors font-medium"
            >
              Products
            </Link>

            {isAuthenticated ? (
              <>
                <Link
                  to="/orders"
                  className="text-sm text-gray-600 hover:text-indigo-600
                             transition-colors font-medium"
                >
                  My Orders
                </Link>

                <Link to="/cart" className="relative">
                  <span
                    className="text-sm text-gray-600 hover:text-indigo-600
                                   transition-colors font-medium"
                  >
                    Cart
                  </span>
                  {cartCount > 0 && (
                    <span
                      className="absolute -top-2 -right-3 bg-indigo-600
                                     text-white text-xs rounded-full w-4 h-4
                                     flex items-center justify-center font-bold"
                    >
                      {cartCount}
                    </span>
                  )}
                </Link>

                <div className="flex items-center gap-3 ml-4">
                  <span className="text-sm text-gray-500">
                    Hi, <strong>{user?.username}</strong>
                  </span>
                  <button
                    onClick={handleLogout}
                    className="btn-secondary text-sm"
                  >
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-2">
                <Link to="/login" className="btn-secondary text-sm">
                  Login
                </Link>
                <Link to="/register" className="btn-primary text-sm">
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            className="sm:hidden text-gray-600 hover:text-indigo-600"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {menuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="sm:hidden border-t border-gray-100 py-3 flex flex-col gap-3">
            <Link
              to="/"
              onClick={() => setMenuOpen(false)}
              className="text-sm text-gray-700 font-medium"
            >
              Products
            </Link>
            {isAuthenticated ? (
              <>
                <Link
                  to="/cart"
                  onClick={() => setMenuOpen(false)}
                  className="text-sm text-gray-700 font-medium"
                >
                  Cart {cartCount > 0 && `(${cartCount})`}
                </Link>
                <Link
                  to="/orders"
                  onClick={() => setMenuOpen(false)}
                  className="text-sm text-gray-700 font-medium"
                >
                  Orders
                </Link>
                <button
                  onClick={() => {
                    handleLogout();
                    setMenuOpen(false);
                  }}
                  className="text-sm text-red-600 text-left font-medium"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMenuOpen(false)}
                  className="text-sm text-gray-700 font-medium"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMenuOpen(false)}
                  className="text-sm text-indigo-600 font-medium"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
