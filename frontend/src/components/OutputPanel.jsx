import React, { useState } from 'react';
import { Loader2, Copy, Check } from 'lucide-react';

export default function OutputPanel({ result, isLoading }) {
  const [copiedSection, setCopiedSection] = useState(null);

  const handleCopy = (text, section) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(section);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const CopyButton = ({ text, section }) => {
    const isCopied = copiedSection === section;
    return (
      <button
        onClick={() => handleCopy(text, section)}
        className="absolute top-2 right-2 p-1.5 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-md transition-colors"
        title="Copy code"
      >
        {isCopied ? <Check size={14} className="text-green-600 dark:text-green-400" /> : <Copy size={14} />}
      </button>
    );
  };

  if (isLoading) {
    return (
      <div className="h-full min-h-[400px] flex flex-col items-center justify-center p-8 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl">
        <Loader2 size={24} className="animate-spin text-blue-500 mb-4" />
        <p className="text-sm text-gray-500 dark:text-gray-400">Generating fix...</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="h-full min-h-[400px] flex flex-col items-center justify-center p-8 text-center bg-gray-50 dark:bg-gray-900/50 border border-dashed border-gray-300 dark:border-gray-800 rounded-xl">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Analysis results will appear here.
        </p>
      </div>
    );
  }

  if (result.isExplain) {
    return (
      <div className="flex flex-col gap-6 h-full">

        {/* Warning banner — same style as debug view */}
        {result.warning && result.warning === "Rate limit exceeded" ? (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 rounded-xl p-4">
            <p className="text-sm font-medium text-red-800 dark:text-red-200">
              ⚠️ API limit reached. Please try again later.
            </p>
          </div>
        ) : result.warning ? (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800/50 rounded-xl p-4">
            <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
              ⚠️ {result.warning}
            </p>
          </div>
        ) : null}

        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 h-full overflow-y-auto">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-200 mb-4">Line-by-Line Explanation</h3>
          <div className="relative bg-gray-50 dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-lg p-4">
            <CopyButton text={result.explanation} section="explain" />
            <pre className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-wrap font-mono pr-8">
              {result.explanation}
            </pre>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">

      {/* Warning Section */}
      {result.warning && result.warning === "Rate limit exceeded" ? (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 rounded-xl p-4 flex items-start gap-3">
          <p className="text-sm font-medium text-red-800 dark:text-red-200">
            ⚠️ API limit reached. Please try again later.
          </p>
        </div>
      ) : result.warning ? (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800/50 rounded-xl p-4 flex items-start gap-3">
          <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
            ⚠️ {result.warning}
          </p>
        </div>
      ) : null}

      {/* Explanation Section */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-200">Explanation</h3>
            {result.error_type && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700 border border-blue-200 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-800">
                {result.error_type}
              </span>
            )}
          </div>
          {result.confidence && (
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${
              result.confidence > 0.85 ? 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800' :
              result.confidence > 0.7 ? 'bg-yellow-100 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800' :
              'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800'
            }`}>
              Confidence: {(result.confidence * 100).toFixed(0)}%
            </span>
          )}
        </div>
        <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
          {result.explanation}
        </p>
      </div>

      {/* Source Context Section */}
      {result.sources && result.sources.length > 0 && (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-200 mb-4">Source Context</h3>
          <div className="bg-gray-50 dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-lg p-4">
            <ul className="list-disc pl-5 space-y-2 text-sm text-gray-700 dark:text-gray-300">
              {result.sources.slice(0, 3).map((source, index) => (
                <li key={index} className="leading-relaxed">
                  {source.length > 150 ? source.substring(0, 150).trim() + "..." : source}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Fix Section */}
      {result.fix && (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-200 mb-4">Fixed Code</h3>
          <div className="relative group bg-gray-50 dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-lg">
            <CopyButton text={result.fix} section="fix" />
            <div className="p-4 overflow-x-auto">
              <pre className="text-sm font-mono text-gray-900 dark:text-gray-200 whitespace-pre pr-8">{result.fix}</pre>
            </div>
          </div>
        </div>
      )}

      {/* Why Fix Works Section */}
      {result.why_fix_works && (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-200 mb-4">Why this fix works</h3>
          <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
            {result.why_fix_works}
          </p>
        </div>
      )}

      {/* Optimization Section */}
      {result.optimized_code && result.optimized_code !== result.fix && (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-200 mb-4">Optimization</h3>
          <div className="relative group bg-gray-50 dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-lg">
            <CopyButton text={result.optimized_code} section="opt" />
            <div className="p-4 overflow-x-auto">
              <pre className="text-sm font-mono text-gray-900 dark:text-gray-200 whitespace-pre pr-8">{result.optimized_code}</pre>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
