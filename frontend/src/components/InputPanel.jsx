import React from 'react';
import { Loader2 } from 'lucide-react';

const LANGUAGES = [
  'python', 'javascript', 'typescript', 'java', 'c++', 'go', 'rust'
];

function detectLikelyLanguage(code) {
  const src = (code || '').trim();
  if (!src) return null;

  // Rust
  if (/\bfn\s+main\s*\(/.test(src) || /println!\s*\(/.test(src) || /\blet\s+mut\s+/.test(src)) {
    return 'rust';
  }

  // Go
  if (/\bpackage\s+main\b/.test(src) || /\bfmt\.Println\s*\(/.test(src) || /:=/.test(src)) {
    return 'go';
  }

  // C++
  if (/#include\s*<.*>/.test(src) || /\bstd::/.test(src) || /\bcout\s*<</.test(src)) {
    return 'c++';
  }

  // Java
  if (/\bpublic\s+class\b/.test(src) || /\bpublic\s+static\s+void\s+main\b/.test(src) || /\bSystem\.out\.println\s*\(/.test(src)) {
    return 'java';
  }

  // TypeScript (before JavaScript)
  if (/\binterface\s+\w+/.test(src) || /\btype\s+\w+\s*=/.test(src) || /:\s*(string|number|boolean|any|unknown|never|void)\b/.test(src)) {
    return 'typescript';
  }

  // JavaScript
  if (/\b(const|let|var)\s+\w+/.test(src) || /\bconsole\.log\s*\(/.test(src) || /=>/.test(src)) {
    return 'javascript';
  }

  // Python
  if (/\bdef\s+\w+\s*\(.*\)\s*:/.test(src) || /\bprint\s*\(/.test(src) || /\bNone\b/.test(src) || /\bTrue\b|\bFalse\b/.test(src)) {
    return 'python';
  }

  return null;
}

export default function InputPanel({ onSubmit, onExplain, isLoading, initialValues }) {
  const [code, setCode] = React.useState(initialValues?.code || '');
  const [errorText, setErrorText] = React.useState(initialValues?.error_message || '');
  const [language, setLanguage] = React.useState(initialValues?.language || 'python');

  const detectedLanguage = React.useMemo(() => detectLikelyLanguage(code), [code]);
  const languageMismatch = detectedLanguage && detectedLanguage !== language;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (code.trim() && !isLoading) {
      onSubmit({ code, error_message: errorText, language });
    }
  };

  const isReady = code.trim() !== '';

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
          {languageMismatch && (
            <div className="flex items-center justify-between gap-3 rounded-lg border border-amber-300 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/20 px-3 py-2">
              <p className="text-xs text-amber-800 dark:text-amber-300">
                Code looks like <span className="font-semibold">{detectedLanguage}</span>, but selected language is <span className="font-semibold">{language}</span>.
              </p>
              <button
                type="button"
                onClick={() => setLanguage(detectedLanguage)}
                className="shrink-0 rounded-md bg-amber-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-amber-700 transition-colors"
              >
                Switch
              </button>
            </div>
          )}
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

        <div className="flex gap-4">
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

          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              if (!code.trim()) return;
              if (onExplain) onExplain({ code, error_message: errorText, language });
            }}
            disabled={!code.trim() || isLoading}
            className={`flex items-center justify-center gap-2 w-full bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 rounded-lg transition duration-200 shadow-sm
              ${!code.trim() || isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isLoading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Explaining...
              </>
            ) : (
              'Explain Code'
            )}
          </button>
        </div>

      </form>
    </div>
  );
}
