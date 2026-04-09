import React from 'react';
import { Loader2 } from 'lucide-react';

const LANGUAGES = [
  'python', 'javascript', 'typescript', 'java', 'c++', 'go', 'rust'
];

export default function InputPanel({ onSubmit, isLoading }) {
  const [code, setCode] = React.useState('');
  const [errorText, setErrorText] = React.useState('');
  const [language, setLanguage] = React.useState('python');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (code.trim() && errorText.trim() && !isLoading) {
      onSubmit({ code, error_message: errorText, language });
    }
  };

  const isReady = code.trim() && errorText.trim();

  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 transition-colors duration-200">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-200">
          Input
        </h2>
        <select 
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="text-sm py-1.5 px-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-950 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {LANGUAGES.map(l => (
            <option key={l} value={l}>{l.charAt(0).toUpperCase() + l.slice(1)}</option>
          ))}
        </select>
      </div>
      
      <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
        
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-400">
            Source Code
          </label>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="// Paste failing code here"
            spellCheck={false}
            className="w-full h-64 border border-gray-300 dark:border-gray-800 rounded-lg px-4 py-3 bg-gray-50 dark:bg-gray-950 text-sm font-mono text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none transition-colors"
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-400">
            Error Output
          </label>
          <textarea
            value={errorText}
            onChange={(e) => setErrorText(e.target.value)}
            placeholder="Paste stack trace or error message"
            spellCheck={false}
            className="w-full h-24 border border-gray-300 dark:border-gray-800 rounded-lg px-4 py-3 bg-gray-50 dark:bg-gray-950 text-sm font-mono text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none transition-colors"
          />
        </div>

        <button
          type="submit"
          disabled={!isReady || isLoading}
          className={`flex items-center justify-center gap-2 w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-lg transition duration-200
            ${!isReady || isLoading ? 'opacity-50 cursor-not-allowed hover:bg-blue-600' : ''}`}
        >
          {isLoading ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              Analyzing...
            </>
          ) : (
            'Debug Code'
          )}
        </button>

      </form>
    </div>
  );
}
