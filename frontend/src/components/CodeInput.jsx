import { useState } from 'react';

const LANGUAGES = [
  'python',
  'javascript',
  'typescript',
  'java',
  'c++',
  'c',
  'go',
  'rust',
  'ruby',
  'php',
  'swift',
  'kotlin',
  'other',
];

const PLACEHOLDER_CODE = `def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)

result = calculate_average([])`;

const PLACEHOLDER_ERROR = `ZeroDivisionError: division by zero`;

export default function CodeInput({ onSubmit, isLoading }) {
  const [code, setCode] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [language, setLanguage] = useState('python');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!code.trim() || !errorMessage.trim()) return;

    onSubmit({
      code: code.trim(),
      error_message: errorMessage.trim(),
      language,
    });
  };

  const handleClear = () => {
    setCode('');
    setErrorMessage('');
  };

  const canSubmit = code.trim() && errorMessage.trim() && !isLoading;

  return (
    <form className="code-input" id="code-input-form" onSubmit={handleSubmit}>
      {/* Language selector */}
      <div className="code-input__header">
        <div className="code-input__lang-group">
          <label htmlFor="language-select" className="code-input__label">
            Language
          </label>
          <select
            id="language-select"
            className="code-input__select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            {LANGUAGES.map((lang) => (
              <option key={lang} value={lang}>
                {lang.charAt(0).toUpperCase() + lang.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <button
          type="button"
          className="code-input__clear-btn"
          onClick={handleClear}
          disabled={!code && !errorMessage}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
          Clear
        </button>
      </div>

      {/* Code textarea */}
      <div className="code-input__field">
        <label htmlFor="code-textarea" className="code-input__label">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" />
          </svg>
          Your Code
        </label>
        <div className="code-input__textarea-wrapper">
          <textarea
            id="code-textarea"
            className="code-input__textarea"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder={PLACEHOLDER_CODE}
            rows={12}
            spellCheck={false}
          />
          <div className="code-input__line-count">
            {code ? code.split('\n').length : 0} lines
          </div>
        </div>
      </div>

      {/* Error textarea */}
      <div className="code-input__field">
        <label htmlFor="error-textarea" className="code-input__label code-input__label--error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          Error / Traceback
        </label>
        <textarea
          id="error-textarea"
          className="code-input__textarea code-input__textarea--error"
          value={errorMessage}
          onChange={(e) => setErrorMessage(e.target.value)}
          placeholder={PLACEHOLDER_ERROR}
          rows={4}
          spellCheck={false}
        />
      </div>

      {/* Submit */}
      <button
        type="submit"
        id="submit-btn"
        className="code-input__submit"
        disabled={!canSubmit}
      >
        {isLoading ? (
          <>
            <span className="code-input__submit-spinner" />
            Analyzing…
          </>
        ) : (
          <>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 20V4M5 11l7-7 7 7" />
            </svg>
            Debug My Code
          </>
        )}
      </button>
    </form>
  );
}
