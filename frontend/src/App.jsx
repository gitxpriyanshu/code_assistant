import { useState } from 'react';
import Header from './components/Header';
import CodeInput from './components/CodeInput';
import ResultPanel from './components/ResultPanel';
import LoadingSpinner from './components/LoadingSpinner';
import { debugCode } from './services/api';
import './App.css';

export default function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (payload) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await debugCode(payload);
      setResult(data);
    } catch (err) {
      console.error('Debug request failed:', err);
      const message =
        err.response?.data?.detail ||
        err.message ||
        'Something went wrong. Please try again.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Header />

      <main className="app-main" id="app-main">
        <div className="app-layout">
          {/* Left panel — input */}
          <section className="app-panel app-panel--input" id="input-panel">
            <div className="app-panel__header">
              <h2 className="app-panel__title">Input</h2>
              <span className="app-panel__badge">Paste & debug</span>
            </div>
            <CodeInput onSubmit={handleSubmit} isLoading={isLoading} />
          </section>

          {/* Right panel — output */}
          <section className="app-panel app-panel--output" id="output-panel">
            <div className="app-panel__header">
              <h2 className="app-panel__title">Output</h2>
              {result && (
                <span className="app-panel__badge app-panel__badge--success">
                  Results ready
                </span>
              )}
            </div>

            {/* Error alert */}
            {error && (
              <div className="app-error" id="error-alert">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>{error}</span>
                <button className="app-error__close" onClick={() => setError(null)}>✕</button>
              </div>
            )}

            {/* Loading */}
            {isLoading && <LoadingSpinner />}

            {/* Results */}
            {!isLoading && <ResultPanel result={result} />}
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer" id="app-footer">
        <p>
          Built with <span className="app-footer__heart">♥</span> using FastAPI · React · FAISS · Groq
        </p>
      </footer>
    </>
  );
}
