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
        className="absolute top-3 right-3 p-1.5 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-md transition-colors"
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

  return (
    <div className="flex flex-col gap-6">

      {/* Explanation Section */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-200">Explanation</h3>
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700">
            High Confidence
          </span>
        </div>
        <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
          {result.explanation}
        </p>
      </div>

      {/* Fix Section */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-200 mb-4">Fixed Code</h3>
        <div className="relative group bg-gray-50 dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-lg p-4 overflow-x-auto">
          <CopyButton text={result.fix} section="fix" />
          <pre className="text-sm font-mono text-gray-900 dark:text-gray-200 whitespace-pre pr-8">{result.fix}</pre>
        </div>
      </div>

      {/* Optimization Section */}
      {result.optimized_code && result.optimized_code !== result.fix && (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-200 mb-4">Optimization</h3>
          <div className="relative group bg-gray-50 dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-lg p-4 overflow-x-auto">
            <CopyButton text={result.optimized_code} section="opt" />
            <pre className="text-sm font-mono text-gray-900 dark:text-gray-200 whitespace-pre pr-8">{result.optimized_code}</pre>
          </div>
        </div>
      )}

    </div>
  );
}
