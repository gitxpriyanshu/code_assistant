import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import InputPanel from './components/InputPanel';
import OutputPanel from './components/OutputPanel';
import { debugCode } from './services/api';

export default function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') === 'dark' ||
        (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
    }
    return true;
  });

  useEffect(() => {
    const root = window.document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  const handleSubmit = async (payload) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await debugCode(payload);
      setResult(data);
    } catch (err) {
      console.error('Debug API fixed:', err);
      setError(
        err.response?.data?.detail || 
        err.message || 
        'An error occurred connecting to the backend.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleExplain = async (payload) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const { explainCode } = await import('./services/api');
      const data = await explainCode(payload);
      setResult({ isExplain: true, explanation: data.explanation });
    } catch (err) {
      console.error('Explain API failed:', err);
      setError(
        err.response?.data?.detail || 
        err.message || 
        'An error occurred connecting to the backend.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors duration-200 font-sans text-gray-900 dark:text-gray-200 flex flex-col">
      <Navbar isDark={isDark} toggleTheme={toggleTheme} />
      
      <main className="w-full max-w-6xl mx-auto px-6 py-8 flex-1 flex flex-col">
        
        {error && (
          <div className="mb-6 bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400 p-4 rounded-lg border border-red-200 dark:border-red-800 flex justify-between">
            <p className="text-sm">{error}</p>
            <button onClick={() => setError(null)} className="font-semibold">x</button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start flex-1">
          <InputPanel onSubmit={handleSubmit} onExplain={handleExplain} isLoading={isLoading} />
          <OutputPanel result={result} isLoading={isLoading} />
        </div>
      </main>
    </div>
  );
}
