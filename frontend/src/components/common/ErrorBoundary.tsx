import { Component, ReactNode, ErrorInfo } from 'react';
import { AlertOctagon, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error inside Chat App boundary:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#000000] text-neutral-100 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-[#171717] border border-[#262626] rounded-2xl p-6 text-center space-y-4 shadow-2xl">
            <div className="h-12 w-12 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 flex items-center justify-center mx-auto">
              <AlertOctagon className="h-6 w-6" />
            </div>
            <h2 className="text-lg font-semibold text-white">Something went wrong</h2>
            <p className="text-xs text-neutral-400 leading-relaxed">
              {this.state.error?.message || 'An unexpected rendering error occurred in the chat UI.'}
            </p>
            <button
              onClick={this.handleReset}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white text-black hover:bg-neutral-200 text-xs font-medium transition-colors cursor-pointer"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Reload Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
