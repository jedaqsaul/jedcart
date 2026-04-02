import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, message: "" };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, message: error.message };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          className="min-h-screen flex flex-col items-center
                        justify-center text-center px-4"
        >
          <span className="text-6xl mb-4">⚠️</span>
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            Something went wrong
          </h2>
          <p className="text-gray-500 text-sm mb-6 max-w-md">
            {this.state.message}
          </p>
          <button
            onClick={() => (window.location.href = "/")}
            className="btn-primary"
          >
            Go Home
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
